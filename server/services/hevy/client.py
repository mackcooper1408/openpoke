"""Hevy API client for workout tracking integration."""

from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse

from ...config import Settings, get_settings
from ...logging_config import logger
from ...utils import error_response


_API_KEY_LOCK = threading.Lock()
_API_KEY_FILE = Path.home() / ".openpoke" / "hevy_api_key.json"


def _ensure_api_key_directory():
    """Ensure the API key storage directory exists."""
    _API_KEY_FILE.parent.mkdir(parents=True, exist_ok=True)


def _save_api_key_to_file(api_key: str) -> None:
    """Save Hevy API key to local file."""
    _ensure_api_key_directory()
    with _API_KEY_LOCK:
        try:
            with open(_API_KEY_FILE, "w") as f:
                json.dump({"api_key": api_key}, f, indent=2)
        except Exception as exc:
            logger.error(f"Failed to save Hevy API key: {exc}")


def _load_api_key_from_file() -> Optional[str]:
    """Load Hevy API key from local file."""
    with _API_KEY_LOCK:
        if not _API_KEY_FILE.exists():
            return None
        try:
            with open(_API_KEY_FILE, "r") as f:
                data = json.load(f)
                return data.get("api_key")
        except Exception as exc:
            logger.error(f"Failed to load Hevy API key: {exc}")
            return None


def _clear_api_key_file() -> None:
    """Clear saved Hevy API key."""
    with _API_KEY_LOCK:
        if _API_KEY_FILE.exists():
            try:
                _API_KEY_FILE.unlink()
            except Exception as exc:
                logger.error(f"Failed to clear Hevy API key: {exc}")


def _get_api_key(settings: Optional[Settings] = None) -> Optional[str]:
    """Get Hevy API key from file or environment."""
    resolved_settings = settings or get_settings()

    # First try from file (user-provided)
    api_key = _load_api_key_from_file()
    if api_key:
        return api_key

    # Fall back to environment variable
    return resolved_settings.hevy_api_key


def _make_hevy_request(
    endpoint: str,
    method: str = "GET",
    params: Optional[Dict[str, Any]] = None,
    json_data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Make an authenticated request to Hevy API."""
    api_key = _get_api_key()
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Hevy not connected. Please add your Hevy API key first.",
        )

    headers = {
        "api-key": api_key,
        "Accept": "application/json",
    }

    if json_data:
        headers["Content-Type"] = "application/json"

    url = f"https://api.hevyapp.com/v1/{endpoint}"

    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=params or {})
        elif method == "POST":
            response = requests.post(
                url, headers=headers, json=json_data, params=params or {}
            )
        elif method == "PUT":
            response = requests.put(
                url, headers=headers, json=json_data, params=params or {}
            )
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, params=params or {})
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        response.raise_for_status()
        return response.json()

    except requests.exceptions.HTTPError as exc:
        logger.error(f"Hevy API request failed: {exc}")
        if exc.response.status_code == 401:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Hevy API key is invalid. Please update your API key.",
            )
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=f"Hevy API error: {exc.response.text}",
        )
    except Exception as exc:
        logger.error(f"Hevy API request error: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch Hevy data: {str(exc)}",
        )


# Public API functions


def save_hevy_api_key(api_key: str) -> JSONResponse:
    """Save Hevy API key."""
    if not api_key or not api_key.strip():
        return error_response("API key cannot be empty", status.HTTP_400_BAD_REQUEST)

    try:
        # Validate API key by making a test request
        headers = {
            "X-API-Key": api_key.strip(),
            "Accept": "application/json",
        }
        response = requests.get(
            "https://api.hevyapp.com/v1/workouts",
            headers=headers,
            params={"page": 1, "pageSize": 1},
            timeout=5,
        )
        response.raise_for_status()

        _save_api_key_to_file(api_key.strip())
        logger.info("Successfully saved Hevy API key")

        return JSONResponse(
            content={"success": True, "message": "Hevy API key saved successfully"},
            status_code=status.HTTP_200_OK,
        )

    except requests.exceptions.HTTPError as exc:
        logger.error(f"Hevy API key validation failed: {exc}")
        return error_response(
            "Invalid Hevy API key. Please check your API key and try again.",
            status.HTTP_400_BAD_REQUEST,
        )
    except Exception as exc:
        logger.error(f"Failed to save Hevy API key: {exc}")
        return error_response(
            f"Failed to save Hevy API key: {str(exc)}",
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


def clear_hevy_api_key() -> JSONResponse:
    """Clear saved Hevy API key."""
    _clear_api_key_file()
    logger.info("Hevy API key cleared")
    return JSONResponse(
        content={"success": True, "message": "Hevy disconnected successfully"},
        status_code=status.HTTP_200_OK,
    )


def get_hevy_status() -> JSONResponse:
    """Check if Hevy API key is configured."""
    api_key = _get_api_key()

    if not api_key:
        return JSONResponse(
            content={"connected": False},
            status_code=status.HTTP_200_OK,
        )

    # Check if API key is from environment variable (trusted)
    settings = get_settings()
    if api_key == settings.hevy_api_key and settings.hevy_api_key:
        # API key from environment is trusted, skip validation
        return JSONResponse(
            content={"connected": True, "source": "environment"},
            status_code=status.HTTP_200_OK,
        )

    # Validate user-provided keys by making a test request
    try:
        headers = {
            "X-API-Key": api_key,
            "Accept": "application/json",
        }
        response = requests.get(
            "https://api.hevyapp.com/v1/workouts",
            headers=headers,
            timeout=5,
            params={"page": 1, "pageSize": 1},
        )
        response.raise_for_status()

        return JSONResponse(
            content={"connected": True, "source": "validated"},
            status_code=status.HTTP_200_OK,
        )
    except Exception as e:
        logger.warning(f"Hevy API key validation failed: {e}")
        return JSONResponse(
            content={"connected": False},
            status_code=status.HTTP_200_OK,
        )


def get_workouts(
    page: int = 1,
    page_size: int = 10,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Fetch workout history from Hevy.

    Args:
        page: Page number (1-indexed)
        page_size: Number of workouts per page
        start_date: ISO format date string (YYYY-MM-DD)
        end_date: ISO format date string (YYYY-MM-DD)

    Returns:
        Dictionary containing workout data
    """
    params = {
        "page": page,
        "pageSize": page_size,
    }
    if start_date:
        params["start_date"] = start_date
    if end_date:
        params["end_date"] = end_date

    return _make_hevy_request("workouts", params=params)


def get_workout_details(workout_id: str) -> Dict[str, Any]:
    """
    Fetch details for a specific workout.

    Args:
        workout_id: Unique identifier for the workout

    Returns:
        Dictionary containing detailed workout data
    """
    return _make_hevy_request(f"workouts/{workout_id}")


def get_routines(
    page: int = 1,
    page_size: int = 50,
) -> Dict[str, Any]:
    """
    Fetch workout routines from Hevy.

    Args:
        page: Page number (1-indexed)
        page_size: Number of routines per page

    Returns:
        Dictionary containing routine data with 'routines' key
    """
    params = {
        "page": page,
        "pageSize": page_size,
    }
    return _make_hevy_request("routines", params=params)


def get_routine_details(routine_id: str) -> Dict[str, Any]:
    """
    Fetch details for a specific routine.

    Args:
        routine_id: Unique identifier for the routine

    Returns:
        Dictionary containing detailed routine data
    """
    return _make_hevy_request(f"routines/{routine_id}")


def create_routine(
    title: str, exercises: List[Dict[str, Any]], folder_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a new workout routine in Hevy.

    Args:
        title: Routine name/title
        exercises: List of exercises with structure:
            - exercise_template_id: str - Exercise template ID
            - superset_id: Optional[int] - Superset grouping
            - rest_seconds: Optional[int] - Rest time
            - sets: List of sets with type and weight_kg/reps/distance_meters/duration_seconds
        folder_id: Optional folder ID to organize the routine

    Returns:
        Dictionary containing created routine data
    """
    # Wrap in 'routine' object as per Hevy API requirements
    # folder_id=null inserts into default "My Routines" folder
    request_body = {
        "routine": {
            "title": title,
            "exercises": exercises,
            "folder_id": folder_id,  # null/None = default "My Routines" folder
        }
    }

    return _make_hevy_request("routines", method="POST", json_data=request_body)


def log_workout(workout_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Log a new workout in Hevy.

    Args:
        workout_data: Dictionary containing workout information
            - title: Workout title
            - description: Optional description
            - exercises: List of exercises with sets, reps, and weights
            - start_time: ISO format datetime
            - end_time: ISO format datetime

    Returns:
        Dictionary containing logged workout data
    """
    return _make_hevy_request("workouts", method="POST", json_data=workout_data)
