import asyncio
from pathlib import Path
from typing import Any, AsyncIterator, Callable, Coroutine, Dict, List, Optional
from jinja2 import Template

from ..core.config import CONFIG_DIR, languages_registry, locales_registry
from ..core.logging import logger
from ..memory.session_store import SessionMemory
from ..pipeline.sentence_chunker import chunk_sentences
from ..pipeline.language_router import LanguageRouter
from ..pipeline.codeswitch import split_by_script, tag_languages, matrix_language, is_code_switched
from ..pipeline.context_engine import ContextEngine
from ..pipeline.confidence_gate import ConfidenceGate
from ..pipeline.paralinguistics import ParalinguisticsAnalyzer
from ..pipeline.dialect_id import DialectIdentifier
from ..providers.base import LLMProvider, TTSProvider, STTProvider
from ..tools.registry import tool_registry
from ..telemetry.metrics import telemetry

PROMPTS_DIR = CONFIG_DIR / "prompts"

class TurnOrchestrator:
    def __init__(
        self,
        send_event: Callable[[Dict[str, Any]], Coroutine[Any, Any, None]],
        send_audio: Callable[[bytes], Coroutine[Any, Any, None]],
        memory: SessionMemory,
        llm: LLMProvider,
        tts: TTSProvider,
    ):
        self.send_event = send_event
        self.send_audio = send_audio
        self.memory = memory
        self.llm = llm
        self.tts = tts

        self.router = LanguageRouter(languages_registry)
        self.context_engine = ContextEngine()
        self.confidence_gate = ConfidenceGate()
        self.paralinguistics = ParalinguisticsAnalyzer()
        self.dialect_id = DialectIdentifier(locales_registry)

        self.state: str = "idle"
        self.reply_task: Optional[asyncio.Task] = None
        self._current_turn_text: str = ""

    async def update_state(self, new_state: str):
        self.state = new_state
        await self.send_event({"type": "state", "value": new_state})

    async def on_user_final(self, text: str, detected_lang: str, conf: float):
        """Called when a finalized user transcript is received."""
        spans = self.start_turn_metrics()
        telemetry.record_mark(spans, "stt_final")

        # 1. Low-resource & confidence gating
        lang_tier = languages_registry.get(detected_lang, {}).get("tier", 1)
        gate_action = self.confidence_gate.evaluate(conf, lang_tier, conf)
        if gate_action != "proceed":
            override_msg = self.confidence_gate.get_prompt_override(gate_action, text, detected_lang)
            if override_msg:
                self.memory.add_message("user", text, detected_lang)
                self.memory.add_message("assistant", override_msg, detected_lang)
                await self.send_event({"type": "llm.delta", "text": override_msg})
                # Synthesize TTS for the override
                async def text_gen():
                    yield override_msg
                async for audio_chunk in self.tts.stream(text_gen(), detected_lang):
                    await self.send_audio(audio_chunk)
                await self.update_state("listening")
                return

        # 2. Code-Switching & Matrix Language Analysis
        script_spans = split_by_script(text)
        tagged_spans = tag_languages(script_spans)
        code_switched = is_code_switched(tagged_spans)
        matrix_lang = matrix_language(tagged_spans) if code_switched else detected_lang

        # 3. Language Routing with Hysteresis
        active_lang = self.router.decide(matrix_lang, conf, self.memory.current_lang)
        self.memory.current_lang = active_lang
        telemetry.record_mark(spans, "lid_done")

        # 4. Dialect & Locale Identification
        locale = self.dialect_id.identify_locale(text, active_lang, self.memory.locale)
        self.memory.locale = locale

        # 5. Paralinguistics & Emotion
        affect = self.paralinguistics.analyze(text)

        # 6. Formality & Cultural Context Retrieval
        formality = self.context_engine.decide_formality(
            self.memory.preferences.formality, locale, text
        )
        slang_items = self.context_engine.retrieve_slang_lexicon(locale, text)
        exemplars = self.context_engine.retrieve_exemplars(locale)
        telemetry.record_mark(spans, "context_done")

        # Record user message in memory
        self.memory.add_message("user", text, active_lang)

        # Cancel any previous in-flight reply (barge-in protection)
        await self.cancel_reply()

        # Start streaming assistant response
        self.reply_task = asyncio.create_task(
            self._respond(active_lang, locale, formality, slang_items, exemplars, code_switched, spans)
        )

    async def _respond(
        self,
        lang: str,
        locale: str,
        formality: str,
        slang_items: List[Dict[str, str]],
        exemplars: List[Dict[str, str]],
        code_switched: bool,
        spans: Dict[str, float]
    ):
        await self.update_state("thinking")
        messages = self.build_prompt_messages(lang, locale, formality, slang_items, exemplars, code_switched)

        full_reply_text = ""
        first_token_sent = False

        async def text_stream() -> AsyncIterator[str]:
            nonlocal full_reply_text, first_token_sent
            tool_definitions = tool_registry.get_schemas()
            async for ev in self.llm.stream(messages, tools=tool_definitions):
                ev_type = ev.get("type")
                if ev_type == "text":
                    token = ev["text"]
                    if not first_token_sent:
                        first_token_sent = True
                        telemetry.record_mark(spans, "llm_ttft")
                    full_reply_text += token
                    await self.send_event({"type": "llm.delta", "text": token})
                    yield token
                elif ev_type == "tool_call":
                    # Execute tool call and yield results
                    tool_name = ev.get("name", "")
                    tool_args = ev.get("args", {})
                    await self.send_event({"type": "tool.call", "name": tool_name, "args": tool_args})
                    tool_res = await tool_registry.execute(tool_name, tool_args)
                    formatted_tool_res = f" [Tool '{tool_name}' result: {tool_res}] "
                    full_reply_text += formatted_tool_res
                    await self.send_event({"type": "llm.delta", "text": formatted_tool_res})
                    yield formatted_tool_res

        try:
            voice_id = languages_registry.get(lang, {}).get("tts_voice", "en-US-JennyNeural")
            seq = 0
            async for sentence in chunk_sentences(text_stream(), lang):
                if self.state != "speaking":
                    await self.update_state("speaking")
                    telemetry.record_mark(spans, "first_sentence")

                # Stream audio chunks for each sentence
                async def sentence_stream():
                    yield sentence

                async for audio_bytes in self.tts.stream(sentence_stream(), lang, voice_id):
                    seq += 1
                    await self.send_audio(audio_bytes)

            self.memory.add_message("assistant", full_reply_text, lang)
            telemetry.finish_turn(spans)
        except asyncio.CancelledError:
            # Handle user barge-in
            telemetry.record_barge_in()
            if full_reply_text:
                self.memory.add_message("assistant", full_reply_text + " [interrupted]", lang)
            await self.send_event({"type": "state", "value": "interrupted"})
            raise
        except Exception as e:
            logger.error("Error in response generation", error=str(e))
            telemetry.record_error()
            await self.send_event({"type": "error", "code": "orchestrator_error", "message": str(e)})
        finally:
            if self.state != "interrupted":
                await self.update_state("listening")

    async def on_barge_in(self):
        """Immediately interrupts the assistant speaking when user begins speaking."""
        await self.cancel_reply()
        await self.update_state("listening")

    async def cancel_reply(self):
        if self.reply_task and not self.reply_task.done():
            self.reply_task.cancel()
            try:
                await self.reply_task
            except asyncio.CancelledError:
                pass
            self.reply_task = None

    def build_prompt_messages(
        self,
        lang: str,
        locale: str,
        formality: str,
        slang_items: List[Dict[str, str]],
        exemplars: List[Dict[str, str]],
        code_switched: bool
    ) -> List[Dict[str, str]]:
        prompt_file = "system_voice.md" if self.memory.mode == "voice" else "system_chat.md"
        prompt_path = PROMPTS_DIR / prompt_file
        template_str = prompt_path.read_text(encoding="utf-8") if prompt_path.exists() else "You are ClanVox."

        lang_name = languages_registry.get(lang, {}).get("name", lang)
        rendered_prompt = Template(template_str).render(
            reply_language=lang_name,
            locale=locale,
            formality=formality,
        )

        if slang_items:
            slang_str = "\n".join([f"- {s['term']}: {s['meaning']} (example: {s['example']})" for s in slang_items])
            rendered_prompt += f"\n\nREGIONAL SLANG & COLLOQUIALISMS (use naturally if relevant):\n{slang_str}"

        if exemplars:
            ex_str = "\n".join([f"User: {e['user']}\nAssistant: {e['assistant']}" for e in exemplars])
            rendered_prompt += f"\n\nSTYLE EXEMPLARS FOR {locale}:\n{ex_str}"

        if code_switched:
            rendered_prompt += "\n\nNOTE: User is code-switching (e.g. Hinglish/Spanglish). Match their blend naturally without cleaning into a single language."

        messages = [{"role": "system", "content": rendered_prompt}]
        for msg in self.memory.get_recent_history(limit=8):
            messages.append({"role": msg.role, "content": msg.content})

        return messages

    def start_turn_metrics(self) -> Dict[str, float]:
        return telemetry.start_turn()

