from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .core.config import settings
from .core.logging import logger, setup_logging
from .api.routes_auth import router as auth_router
from .api.routes_session import router as session_router
from .api.routes_chat import router as chat_router
from .api.ws_realtime import router as ws_router

# Ensure tools are imported and registered
import backend.app.tools.weather
import backend.app.tools.time_info
import backend.app.tools.search

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info("Starting ClanVox Multilingual Assistant Backend", version=settings.APP_VERSION, debug=settings.DEBUG)
    yield
    logger.info("Shutting down ClanVox Assistant Backend")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Production-oriented real-time multilingual voice and chat AI assistant.",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(auth_router)
app.include_router(session_router)
app.include_router(chat_router)
app.include_router(ws_router)

@app.get("/health", tags=["health"])
async def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "default_language": settings.DEFAULT_LANGUAGE
    }

# Mount static web frontend if available
frontend_dir = Path(__file__).resolve().parent.parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/app", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")
