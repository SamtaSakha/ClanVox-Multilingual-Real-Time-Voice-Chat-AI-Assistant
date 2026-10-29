import asyncio
import sys
from pathlib import Path

# Add project root
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

from backend.app.core.config import settings, languages_registry, locales_registry
from backend.app.pipeline.codeswitch import split_by_script, tag_languages, matrix_language, is_code_switched
from backend.app.pipeline.dialect_id import DialectIdentifier
from backend.app.pipeline.context_engine import ContextEngine
from backend.app.providers.llm.mock import MockLLMProvider
from backend.app.providers.llm.openai import OpenAILLMProvider

async def main():
    print("=" * 65)
    print("   ClanVox - Multilingual AI Assistant (Interactive CLI)")
    print("=" * 65)
    print("Type anything in English, Hindi, Hinglish, Spanish, etc.")
    print("Type 'exit' or 'quit' to return to menu.\n")

    dialect_id = DialectIdentifier(locales_registry)
    context_engine = ContextEngine()

    llm = OpenAILLMProvider() if settings.LLM_PROVIDER == "openai" and settings.OPENAI_API_KEY else MockLLMProvider()

    while True:
        try:
            user_input = input("\nYou > ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not user_input:
            continue
        if user_input.lower() in ["exit", "quit", "q"]:
            break

        # Code-switching analysis
        spans = split_by_script(user_input)
        tagged = tag_languages(spans)
        code_switched = is_code_switched(tagged)
        matrix = matrix_language(tagged)
        locale = dialect_id.identify_locale(user_input, matrix)
        formality = context_engine.decide_formality("auto", locale, user_input)

        print(f"\n[Analysis] Matrix Lang: {matrix.upper()} | Code-Switched: {code_switched} | Locale: {locale} | Formality: {formality}")
        print("ClanVox > ", end="", flush=True)

        system_prompt = (
            f"You are ClanVox AI assistant. Reply in {matrix} (locale: {locale}, formality: {formality}). "
            f"If user mixes languages (e.g. Hinglish), mirror their style naturally."
        )
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]

        async for ev in llm.stream(messages):
            if ev.get("type") == "text":
                print(ev.get("text", ""), end="", flush=True)
        print()

if __name__ == "__main__":
    asyncio.run(main())
