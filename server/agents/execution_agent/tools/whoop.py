"""Whoop tool schemas and actions for the execution agent."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List

from server.services.whoop import (
    get_recovery_data,
    get_sleep_data,
    get_strain_data,
    get_workout_data,
    get_cycles_data,
)
from ....logging_config import logger


_SCHEMAS: List[Dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "whoop_get_recovery",
            "description": "Fetch recovery data from Whoop to understand the user's readiness for training. Recovery scores indicate how well the body has recovered from previous strain.",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "Start date in YYYY-MM-DD format. Defaults to 7 days ago if not specified.",
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date in YYYY-MM-DD format. Defaults to today if not specified.",
                    },
                },
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "whoop_get_sleep",
            "description": "Fetch sleep data from Whoop including sleep duration, quality, stages, and disturbances.",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "Start date in YYYY-MM-DD format. Defaults to 7 days ago if not specified.",
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date in YYYY-MM-DD format. Defaults to today if not specified.",
                    },
                },
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "whoop_get_strain",
            "description": "Fetch strain data from Whoop showing cardiovascular load and exertion levels throughout the day.",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "Start date in YYYY-MM-DD format. Defaults to 7 days ago if not specified.",
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date in YYYY-MM-DD format. Defaults to today if not specified.",
                    },
                },
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "whoop_get_workouts",
            "description": "Fetch workout activity data from Whoop including workout type, duration, and intensity metrics.",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "Start date in YYYY-MM-DD format. Defaults to 7 days ago if not specified.",
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date in YYYY-MM-DD format. Defaults to today if not specified.",
                    },
                },
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "whoop_get_cycles",
            "description": "Fetch complete physiological cycle data from Whoop combining strain, recovery, and sleep metrics.",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "Start date in YYYY-MM-DD format. Defaults to 7 days ago if not specified.",
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date in YYYY-MM-DD format. Defaults to today if not specified.",
                    },
                },
                "additionalProperties": False,
            },
        },
    },
]


def _get_default_date_range() -> tuple[str, str]:
    """Get default date range (last 7 days)."""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=7)
    return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")


def _whoop_get_recovery(start_date: str = None, end_date: str = None) -> str:
    """Fetch recovery data from Whoop."""
    try:
        if not start_date or not end_date:
            start_date, end_date = _get_default_date_range()

        data = get_recovery_data(start_date, end_date)
        logger.info(f"Retrieved Whoop recovery data from {start_date} to {end_date}")
        return str(data)
    except Exception as exc:
        logger.error(f"Failed to get Whoop recovery data: {exc}")
        return f"Error fetching recovery data: {str(exc)}"


def _whoop_get_sleep(start_date: str = None, end_date: str = None) -> str:
    """Fetch sleep data from Whoop."""
    try:
        if not start_date or not end_date:
            start_date, end_date = _get_default_date_range()

        data = get_sleep_data(start_date, end_date)
        logger.info(f"Retrieved Whoop sleep data from {start_date} to {end_date}")
        return str(data)
    except Exception as exc:
        logger.error(f"Failed to get Whoop sleep data: {exc}")
        return f"Error fetching sleep data: {str(exc)}"


def _whoop_get_strain(start_date: str = None, end_date: str = None) -> str:
    """Fetch strain data from Whoop."""
    try:
        if not start_date or not end_date:
            start_date, end_date = _get_default_date_range()

        data = get_strain_data(start_date, end_date)
        logger.info(f"Retrieved Whoop strain data from {start_date} to {end_date}")
        return str(data)
    except Exception as exc:
        logger.error(f"Failed to get Whoop strain data: {exc}")
        return f"Error fetching strain data: {str(exc)}"


def _whoop_get_workouts(start_date: str = None, end_date: str = None) -> str:
    """Fetch workout data from Whoop."""
    try:
        if not start_date or not end_date:
            start_date, end_date = _get_default_date_range()

        data = get_workout_data(start_date, end_date)
        logger.info(f"Retrieved Whoop workout data from {start_date} to {end_date}")
        return str(data)
    except Exception as exc:
        logger.error(f"Failed to get Whoop workout data: {exc}")
        return f"Error fetching workout data: {str(exc)}"


def _whoop_get_cycles(start_date: str = None, end_date: str = None) -> str:
    """Fetch cycle data from Whoop."""
    try:
        if not start_date or not end_date:
            start_date, end_date = _get_default_date_range()

        data = get_cycles_data(start_date, end_date)
        logger.info(f"Retrieved Whoop cycle data from {start_date} to {end_date}")
        return str(data)
    except Exception as exc:
        logger.error(f"Failed to get Whoop cycle data: {exc}")
        return f"Error fetching cycle data: {str(exc)}"


def get_schemas() -> List[Dict[str, Any]]:
    """Return Whoop tool schemas for the LLM."""
    return _SCHEMAS


def build_registry(agent_name: str) -> Dict[str, Callable[..., Any]]:
    """Build registry mapping tool names to callable functions."""
    return {
        "whoop_get_recovery": _whoop_get_recovery,
        "whoop_get_sleep": _whoop_get_sleep,
        "whoop_get_strain": _whoop_get_strain,
        "whoop_get_workouts": _whoop_get_workouts,
        "whoop_get_cycles": _whoop_get_cycles,
    }


__all__ = [
    "get_schemas",
    "build_registry",
]
