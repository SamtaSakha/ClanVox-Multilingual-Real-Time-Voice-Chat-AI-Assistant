from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
CONFIG_DIR = BASE_DIR / "config"

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    APP_NAME: str = "ClanVox Multilingual Assistant"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    CORS_ORIGINS: List[str] = ["*"]

    # Language & Locales
    DEFAULT_LANGUAGE: str = "en"
    DEFAULT_LOCALE: str = "en-US"
    FALLBACK_LANGUAGE: str = "en"
    CONFIDENCE_THRESHOLD_HIGH: float = 0.80
    CONFIDENCE_THRESHOLD_LOW: float = 0.50

    # Providers
    LLM_PROVIDER: str = "mock"
    STT_PROVIDER: str = "mock"
    TTS_PROVIDER: str = "mock"

    # API Keys
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    DEEPGRAM_API_KEY: Optional[str] = None
    AZURE_SPEECH_KEY: Optional[str] = None
    AZURE_SPEECH_REGION: str = "eastus"
    ELEVENLABS_API_KEY: Optional[str] = None
    CARTESIA_API_KEY: Optional[str] = None

    # LiveKit Realtime
    LIVEKIT_URL: str = "ws://localhost:7880"
    LIVEKIT_API_KEY: str = "devkey"
    LIVEKIT_API_SECRET: str = "secret"

    # Database & Redis
    DATABASE_URL: str = "sqlite+aiosqlite:///./clanvox.db"
    REDIS_URL: str = "redis://localhost:6379/0"

    # Security
    JWT_SECRET: str = "super-secret-clanvox-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    RATE_LIMIT_PER_MINUTE: int = 60

settings = Settings()

def load_yaml(file_path: Path) -> Dict[str, Any]:
    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}

languages_registry: Dict[str, Any] = load_yaml(CONFIG_DIR / "languages.yaml").get("languages", {})
locales_registry: Dict[str, Any] = load_yaml(CONFIG_DIR / "locales.yaml").get("locales", {})
models_config: Dict[str, Any] = load_yaml(CONFIG_DIR / "models.yaml")
safety_config: Dict[str, Any] = load_yaml(CONFIG_DIR / "safety.yaml")

