"""Hevy API routes for API key management."""

from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from ..services.hevy import save_hevy_api_key, clear_hevy_api_key, get_hevy_status

router = APIRouter(prefix="/hevy", tags=["hevy"])


class HevyApiKeyPayload(BaseModel):
    """Payload for saving Hevy API key."""

    api_key: str


@router.post("/connect")
async def hevy_connect(payload: HevyApiKeyPayload) -> JSONResponse:
    """Save and validate Hevy API key."""
    return save_hevy_api_key(payload.api_key)


@router.get("/status")
async def hevy_status() -> JSONResponse:
    """Check if Hevy API key is configured and valid."""
    return get_hevy_status()


@router.post("/disconnect")
async def hevy_disconnect() -> JSONResponse:
    """Clear saved Hevy API key."""
    return clear_hevy_api_key()
