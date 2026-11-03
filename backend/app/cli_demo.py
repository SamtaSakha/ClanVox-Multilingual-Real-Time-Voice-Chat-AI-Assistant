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
    print("Select AI Assistant Voice Persona:")
    print(" [1] 👩 Female Assistant (Aria / Swara)  <-- DEFAULT")
    print(" [2] 👨 Male Assistant (Leo / Aarav)")
    print("Press Enter to keep default (Female), or type 1 or 2.")
    print("Tip: Type '/male' or '/female' anytime to switch persona.")
    print("Type 'exit' or 'quit' to return to menu.\n")

    try:
        choice = input("Select assistant (1/2, default 1): ").strip()
    except (EOFError, KeyboardInterrupt):
        return

    gender = "male" if choice == "2" else "female"
    persona_name = "Leo" if gender == "male" else "Aria"
    print(f"\n[Active Assistant] {'👩 Female' if gender == 'female' else '👨 Male'} ({persona_name})\n")

    dialect_id = DialectIdentifier(locales_registry)
    context_engine = ContextEngine()

    llm = OpenAILLMProvider() if settings.LLM_PROVIDER == "openai" and settings.OPENAI_API_KEY else MockLLMProvider()

    while True:
        try:
            user_input = input(f"\nYou > ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not user_input:
            continue
        if user_input.lower() in ["exit", "quit", "q"]:
            break

        # In-line persona switching commands
        if user_input.lower() in ["/female", "female"]:
            gender = "female"
            persona_name = "Aria"
            print("[Switched to 👩 Female Assistant (Aria)]")
            continue
        elif user_input.lower() in ["/male", "male"]:
            gender = "male"
            persona_name = "Leo"
            print("[Switched to 👨 Male Assistant (Leo)]")
            continue

        # Code-switching analysis
        spans = split_by_script(user_input)
        tagged = tag_languages(spans)
        code_switched = is_code_switched(tagged)
        matrix = matrix_language(tagged)
        locale = dialect_id.identify_locale(user_input, matrix)
        formality = context_engine.decide_formality("auto", locale, user_input)

        localized_name = "Swara" if (gender == "female" and matrix == "hi") else ("Aarav" if (gender == "male" and matrix == "hi") else persona_name)

        print(f"[Analysis] Matrix: {matrix.upper()} | Code-Switch: {code_switched} | Locale: {locale} | Assistant: {localized_name} ({gender.capitalize()})")
        print(f"ClanVox ({localized_name}) > ", end="", flush=True)

        system_prompt = (
            f"You are {localized_name}, a helpful {'female' if gender == 'female' else 'male'} AI assistant. "
            f"Reply in {matrix} (locale: {locale}, formality: {formality}). "
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
