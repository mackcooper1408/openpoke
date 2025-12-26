from __future__ import annotations

from fastapi import APIRouter

from .chat import router as chat_router
from .gmail import router as gmail_router
from .meta import router as meta_router
from .whoop import router as whoop_router
from .hevy import router as hevy_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(meta_router)
api_router.include_router(chat_router)
api_router.include_router(gmail_router)
api_router.include_router(whoop_router)
api_router.include_router(hevy_router)

__all__ = ["api_router"]
