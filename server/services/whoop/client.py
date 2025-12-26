"""Whoop API client for fitness tracking integration."""

from __future__ import annotations

import json
import os
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional

import requests
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse

from ...config import Settings, get_settings
from ...logging_config import logger
from ...utils import error_response


_TOKEN_LOCK = threading.Lock()
_TOKEN_FILE = Path.home() / ".openpoke" / "whoop_token.json"
_STATE_FILE = Path.home() / ".openpoke" / "whoop_oauth_state.txt"


def _ensure_token_directory():
    """Ensure the token storage directory exists."""
    _TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)


def _save_token(token_data: Dict[str, Any]) -> None:
    """Save OAuth token to local file."""
    _ensure_token_directory()
    with _TOKEN_LOCK:
        try:
            with open(_TOKEN_FILE, "w") as f:
                json.dump(token_data, f, indent=2)
        except Exception as exc:
            logger.error(f"Failed to save Whoop token: {exc}")


def _load_token() -> Optional[Dict[str, Any]]:
    """Load OAuth token from local file."""
    print("Loading Whoop token from file:", _TOKEN_FILE)
    with _TOKEN_LOCK:
        if not _TOKEN_FILE.exists():
            return None
        try:
            with open(_TOKEN_FILE, "r") as f:
                return json.load(f)
        except Exception as exc:
            logger.error(f"Failed to load Whoop token: {exc}")
            return None


def _clear_token() -> None:
    """Clear saved OAuth token."""
    with _TOKEN_LOCK:
        if _TOKEN_FILE.exists():
            try:
                _TOKEN_FILE.unlink()
            except Exception as exc:
                logger.error(f"Failed to clear Whoop token: {exc}")


def _save_oauth_state(state: str) -> None:
    """Save OAuth state for CSRF validation."""
    _ensure_token_directory()
    try:
        with open(_STATE_FILE, "w") as f:
            f.write(state)
    except Exception as exc:
        logger.error(f"Failed to save OAuth state: {exc}")


def _validate_and_clear_state(state: str) -> bool:
    """Validate OAuth state and clear it."""
    try:
        if not _STATE_FILE.exists():
            logger.error("OAuth state file not found")
            return False

        with open(_STATE_FILE, "r") as f:
            saved_state = f.read().strip()

        # Clear state file after reading
        _STATE_FILE.unlink()

        return saved_state == state
    except Exception as exc:
        logger.error(f"Failed to validate OAuth state: {exc}")
        return False


def _is_token_expired(token_data: Dict[str, Any]) -> bool:
    """Check if token is expired or about to expire."""
    if not token_data.get("access_token"):
        return True

    expires_at = token_data.get("expires_at")
    if not expires_at:
        return True

    # Consider token expired if it expires within 5 minutes
    expiry_time = datetime.fromisoformat(expires_at)
    return datetime.utcnow() + timedelta(minutes=5) >= expiry_time


def _refresh_token(settings: Settings) -> Optional[Dict[str, Any]]:
    """Refresh the OAuth access token."""
    token_data = _load_token()
    if not token_data or not token_data.get("refresh_token"):
        return None

    if not settings.whoop_client_id or not settings.whoop_client_secret:
        logger.error("Whoop client credentials not configured")
        return None

    try:
        response = requests.post(
            "https://api.prod.whoop.com/oauth/oauth2/token",
            data={
                "grant_type": "refresh_token",
                "refresh_token": token_data["refresh_token"],
                "client_id": settings.whoop_client_id,
                "client_secret": settings.whoop_client_secret,
            },
        )
        response.raise_for_status()

        new_token_data = response.json()
        # Calculate expiry time
        expires_in = new_token_data.get("expires_in", 3600)
        new_token_data["expires_at"] = (
            datetime.utcnow() + timedelta(seconds=expires_in)
        ).isoformat()

        # Preserve refresh token if not provided in response
        if "refresh_token" not in new_token_data:
            new_token_data["refresh_token"] = token_data["refresh_token"]

        _save_token(new_token_data)
        logger.info("Successfully refreshed Whoop access token")
        return new_token_data

    except Exception as exc:
        logger.error(f"Failed to refresh Whoop token: {exc}")
        return None


def _get_valid_token(settings: Optional[Settings] = None) -> Optional[str]:
    """Get a valid access token, refreshing if necessary."""
    resolved_settings = settings or get_settings()
    token_data = _load_token()

    if not token_data:
        return None

    if _is_token_expired(token_data):
        token_data = _refresh_token(resolved_settings)
        if not token_data:
            return None

    return token_data.get("access_token")


def _make_whoop_request(
    endpoint: str, params: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Make an authenticated request to Whoop API."""
    access_token = _get_valid_token()
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Whoop not connected. Please connect your Whoop account first.",
        )

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
    }

    url = f"https://api.prod.whoop.com/developer/v2/{endpoint}"

    try:
        response = requests.get(url, headers=headers, params=params or {})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as exc:
        logger.error(f"Whoop API request failed: {exc}")
        if exc.response.status_code == 401:
            # Token might be invalid, try refreshing
            _clear_token()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Whoop authentication expired. Please reconnect.",
            )
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=f"Whoop API error: {exc.response.text}",
        )
    except Exception as exc:
        logger.error(f"Whoop API request error: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch Whoop data: {str(exc)}",
        )


# Public API functions


def save_oauth_state(state: str) -> None:
    """Save OAuth state for CSRF validation (public wrapper)."""
    _save_oauth_state(state)


def connect_whoop(
    code: str, state: str, settings: Optional[Settings] = None
) -> JSONResponse:
    """Exchange authorization code for access token."""
    resolved_settings = settings or get_settings()

    # Validate state parameter for CSRF protection
    if not _validate_and_clear_state(state):
        return error_response(
            "Invalid OAuth state - possible CSRF attack", status.HTTP_400_BAD_REQUEST
        )

    if (
        not resolved_settings.whoop_client_id
        or not resolved_settings.whoop_client_secret
    ):
        return error_response(
            "Whoop client credentials not configured",
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    try:
        response = requests.post(
            "https://api.prod.whoop.com/oauth/oauth2/token",
            data={
                "grant_type": "authorization_code",
                "code": code,
                "client_id": resolved_settings.whoop_client_id,
                "client_secret": resolved_settings.whoop_client_secret,
                "redirect_uri": resolved_settings.whoop_redirect_uri,
            },
        )
        response.raise_for_status()

        token_data = response.json()

        # Calculate expiry time
        expires_in = token_data.get("expires_in", 3600)
        token_data["expires_at"] = (
            datetime.utcnow() + timedelta(seconds=expires_in)
        ).isoformat()

        _save_token(token_data)
        logger.info("Successfully connected Whoop account")

        return JSONResponse(
            content={"success": True, "message": "Whoop connected successfully"},
            status_code=status.HTTP_200_OK,
        )

    except requests.exceptions.HTTPError as exc:
        logger.error(f"Whoop OAuth exchange failed: {exc}")
        return error_response(
            f"Failed to connect Whoop: {exc.response.text}",
            status.HTTP_400_BAD_REQUEST,
        )
    except Exception as exc:
        logger.error(f"Whoop connection error: {exc}")
        return error_response(
            f"Failed to connect Whoop: {str(exc)}",
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


def disconnect_whoop() -> JSONResponse:
    """Disconnect Whoop account by clearing stored token."""
    _clear_token()
    logger.info("Whoop account disconnected")
    return JSONResponse(
        content={"success": True, "message": "Whoop disconnected successfully"},
        status_code=status.HTTP_200_OK,
    )


def get_whoop_status() -> JSONResponse:
    """Check if Whoop is connected and token is valid."""
    token_data = _load_token()

    if not token_data or not token_data.get("access_token"):
        print("Whoop not connected: no token data")
        return JSONResponse(
            content={"connected": False},
            status_code=status.HTTP_200_OK,
        )

    # Check if token needs refresh
    if _is_token_expired(token_data):
        refreshed = _refresh_token(get_settings())
        print("Whoop token refreshed:", bool(refreshed))
        if not refreshed:
            return JSONResponse(
                content={"connected": False},
                status_code=status.HTTP_200_OK,
            )

    return JSONResponse(
        content={"connected": True},
        status_code=status.HTTP_200_OK,
    )


def get_recovery_data(
    start_date: Optional[str] = None, end_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Fetch recovery data from Whoop.

    Args:
        start_date: ISO format datetime string (YYYY-MM-DDTHH:MM:SS.SSSZ)
        end_date: ISO format datetime string (YYYY-MM-DDTHH:MM:SS.SSSZ)

    Returns:
        Dictionary containing recovery data
    """
    params = {}
    if start_date:
        # Convert date to datetime if needed
        if len(start_date) == 10:  # YYYY-MM-DD format
            params["start"] = f"{start_date}T00:00:00.000Z"
        else:
            params["start"] = start_date
    if end_date:
        if len(end_date) == 10:  # YYYY-MM-DD format
            params["end"] = f"{end_date}T23:59:59.999Z"
        else:
            params["end"] = end_date

    return _make_whoop_request("recovery", params)


def get_sleep_data(
    start_date: Optional[str] = None, end_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Fetch sleep data from Whoop.

    Args:
        start_date: ISO format datetime string (YYYY-MM-DDTHH:MM:SS.SSSZ)
        end_date: ISO format datetime string (YYYY-MM-DDTHH:MM:SS.SSSZ)

    Returns:
        Dictionary containing sleep data
    """
    params = {}
    if start_date:
        # Convert date to datetime if needed
        if len(start_date) == 10:  # YYYY-MM-DD format
            params["start"] = f"{start_date}T00:00:00.000Z"
        else:
            params["start"] = start_date
    if end_date:
        if len(end_date) == 10:  # YYYY-MM-DD format
            params["end"] = f"{end_date}T23:59:59.999Z"
        else:
            params["end"] = end_date

    return _make_whoop_request("activity/sleep", params)


def get_strain_data(
    start_date: Optional[str] = None, end_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Fetch strain data from Whoop (day strain scores).

    Args:
        start_date: ISO format date string (YYYY-MM-DD)
        end_date: ISO format date string (YYYY-MM-DD)

    Returns:
        Dictionary containing strain data
    """
    params = {}
    if start_date:
        params["start"] = start_date
    if end_date:
        params["end"] = end_date

    return _make_whoop_request("cycle", params)


def get_workout_data(
    start_date: Optional[str] = None, end_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Fetch workout data from Whoop.

    Args:
        start_date: ISO format datetime string (YYYY-MM-DDTHH:MM:SS.SSSZ)
        end_date: ISO format datetime string (YYYY-MM-DDTHH:MM:SS.SSSZ)

    Returns:
        Dictionary containing workout data
    """
    params = {}
    if start_date:
        # Convert date to datetime if needed
        if len(start_date) == 10:  # YYYY-MM-DD format
            params["start"] = f"{start_date}T00:00:00.000Z"
        else:
            params["start"] = start_date
    if end_date:
        if len(end_date) == 10:  # YYYY-MM-DD format
            params["end"] = f"{end_date}T23:59:59.999Z"
        else:
            params["end"] = end_date

    return _make_whoop_request("activity/workout", params)


def get_cycles_data(
    start_date: Optional[str] = None, end_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Fetch physiological cycle data from Whoop.

    Args:
        start_date: ISO format datetime string (YYYY-MM-DDTHH:MM:SS.SSSZ)
        end_date: ISO format datetime string (YYYY-MM-DDTHH:MM:SS.SSSZ)

    Returns:
        Dictionary containing cycle data
    """
    params = {}
    if start_date:
        # Convert date to datetime if needed
        if len(start_date) == 10:  # YYYY-MM-DD format
            params["start"] = f"{start_date}T00:00:00.000Z"
        else:
            params["start"] = start_date
    if end_date:
        if len(end_date) == 10:  # YYYY-MM-DD format
            params["end"] = f"{end_date}T23:59:59.999Z"
        else:
            params["end"] = end_date

    return _make_whoop_request("cycle", params)
