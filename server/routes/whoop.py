"""Whoop API routes for OAuth flow."""

from __future__ import annotations

import secrets

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse, RedirectResponse

from ..config import Settings, get_settings
from ..services.whoop import (
    connect_whoop,
    disconnect_whoop,
    get_whoop_status,
    save_oauth_state,
)

router = APIRouter(prefix="/whoop", tags=["whoop"])


@router.get("/connect")
async def whoop_connect(settings: Settings = Depends(get_settings)) -> RedirectResponse:
    """Initiate Whoop OAuth flow by redirecting to Whoop authorization page."""
    if not settings.whoop_client_id:
        raise ValueError("Whoop client credentials not configured")

    # Generate a secure random state for CSRF protection (min 8 characters required by Whoop)
    state = secrets.token_urlsafe(32)
    save_oauth_state(state)

    # Redirect URI should point to the Next.js callback handler
    redirect_uri = (
        settings.whoop_redirect_uri or "http://localhost:3000/api/whoop/callback"
    )

    auth_url = (
        f"https://api.prod.whoop.com/oauth/oauth2/auth"
        f"?client_id={settings.whoop_client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&response_type=code"
        f"&scope=read:recovery read:sleep read:workout read:cycles read:body_measurement"
        f"&state={state}"
    )

    return RedirectResponse(url=auth_url)


@router.get("/callback")
async def whoop_callback(
    code: str = Query(..., description="Authorization code from Whoop"),
    state: str = Query(..., description="OAuth state parameter for CSRF protection"),
    settings: Settings = Depends(get_settings),
) -> JSONResponse:
    """Handle OAuth callback from Whoop and exchange code for access token."""
    return connect_whoop(code, state, settings)


@router.get("/status")
async def whoop_status() -> JSONResponse:
    """Check if Whoop is connected and token is valid."""
    print("Checking Whoop status...")
    return get_whoop_status()


@router.post("/disconnect")
async def whoop_disconnect() -> JSONResponse:
    """Disconnect Whoop account by clearing stored token."""
    return disconnect_whoop()
