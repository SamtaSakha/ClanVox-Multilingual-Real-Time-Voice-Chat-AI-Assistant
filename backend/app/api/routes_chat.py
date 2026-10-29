import time
from typing import AsyncIterator
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from ..core.config import languages_registry, locales_registry, settings
from ..memory.session_store import session_store
from ..pipeline.codeswitch import split_by_script, tag_languages, matrix_language, is_code_switched
from ..pipeline.dialect_id import DialectIdentifier
from ..pipeline.context_engine import ContextEngine
from ..providers.llm.mock import MockLLMProvider
from ..providers.llm.openai import OpenAILLMProvider
from ..providers.llm.anthropic import AnthropicLLMProvider
from ..safety.moderation import moderation_service
from ..safety.prompt_injection import prompt_injection_guard
from ..schemas.chat import ChatRequest, ChatResponse

router = APIRouter(prefix="/v1", tags=["chat"])

def get_llm():
    if settings.LLM_PROVIDER == "openai" and settings.OPENAI_API_KEY:
        return OpenAILLMProvider()
    elif settings.LLM_PROVIDER == "anthropic" and settings.ANTHROPIC_API_KEY:
        return AnthropicLLMProvider()
    return MockLLMProvider()

@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    start_time = time.perf_counter()

    # Safety checks
    is_suspicious, _ = prompt_injection_guard.is_suspicious(req.message)
    if is_suspicious:
        raise HTTPException(status_code=400, detail="Invalid input detected.")

    is_safe, category, override = moderation_service.check_content(req.message, req.locale or "en-US")
    if not is_safe:
        return ChatResponse(
            session_id=req.session_id,
            reply=override.get("reply", "Message flagged by moderation."),
            language="en",
            locale=req.locale or "en-US",
            latency_ms=int((time.perf_counter() - start_time) * 1000)
        )

    mem = session_store.get_or_create(req.session_id, lang=req.language or "en", locale=req.locale or "en-US", mode="chat")

    # Code-switch & linguistic analysis
    spans = split_by_script(req.message)
    tagged = tag_languages(spans)
    code_switched = is_code_switched(tagged)
    detected_matrix = matrix_language(tagged) if code_switched else (req.language or mem.current_lang)

    mem.current_lang = detected_matrix
    mem.add_message("user", req.message, detected_matrix)

    # Prompt assembly
    dialect_id = DialectIdentifier(locales_registry)
    context_engine = ContextEngine()
    locale = dialect_id.identify_locale(req.message, detected_matrix, req.locale or mem.locale)
    formality = context_engine.decide_formality(mem.preferences.formality, locale, req.message)

    llm = get_llm()
    system_prompt = (
        f"You are ClanVox AI assistant. Reply in {detected_matrix} (locale: {locale}, formality: {formality}). "
        f"If the user mixes languages (e.g. Hinglish), reply in the same natural blend."
    )
    messages = [{"role": "system", "content": system_prompt}]
    for msg in mem.get_recent_history(limit=8):
        messages.append({"role": msg.role, "content": msg.content})

    reply_text = ""
    async for ev in llm.stream(messages):
        if ev.get("type") == "text":
            reply_text += ev.get("text", "")

    mem.add_message("assistant", reply_text, detected_matrix)
    latency_ms = int((time.perf_counter() - start_time) * 1000)

    return ChatResponse(
        session_id=req.session_id,
        reply=reply_text,
        language=detected_matrix,
        locale=locale,
        detected_code_switch=code_switched,
        matrix_language=detected_matrix,
        latency_ms=latency_ms
    )

@router.post("/chat/stream")
async def chat_stream(req: ChatRequest):
    mem = session_store.get_or_create(req.session_id, lang=req.language or "en", locale=req.locale or "en-US", mode="chat")
    mem.add_message("user", req.message, req.language or mem.current_lang)

    llm = get_llm()
    system_prompt = f"You are ClanVox AI assistant. Reply in {mem.current_lang}."
    messages = [{"role": "system", "content": system_prompt}]
    for msg in mem.get_recent_history(limit=8):
        messages.append({"role": msg.role, "content": msg.content})

    async def sse_generator() -> AsyncIterator[str]:
        full_reply = ""
        async for ev in llm.stream(messages):
            if ev.get("type") == "text":
                token = ev.get("text", "")
                full_reply += token
                yield f"data: {token}\n\n"
        mem.add_message("assistant", full_reply, mem.current_lang)
        yield "data: [DONE]\n\n"

    return StreamingResponse(sse_generator(), media_type="text/event-stream")

