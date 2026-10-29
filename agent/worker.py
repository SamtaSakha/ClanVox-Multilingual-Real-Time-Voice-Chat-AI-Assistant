import asyncio
import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from backend.app.core.config import settings
from backend.app.core.logging import logger, setup_logging

async def run_worker():
    setup_logging()
    logger.info(
        "Starting ClanVox LiveKit Voice Agent Worker",
        livekit_url=settings.LIVEKIT_URL,
        llm=settings.LLM_PROVIDER,
        stt=settings.STT_PROVIDER,
        tts=settings.TTS_PROVIDER,
    )

    try:
        # Connect to LiveKit server with API key & secret
        logger.info("Connecting to LiveKit room dispatcher...")
        # Simulates agent listening for rooms in background
        while True:
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        logger.info("Voice Agent Worker terminated.")
    except Exception as e:
        logger.error("Voice Agent Worker encountered an error", error=str(e))

if __name__ == "__main__":
    try:
        asyncio.run(run_worker())
    except KeyboardInterrupt:
        logger.info("Worker stopped by user.")

