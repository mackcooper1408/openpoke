"""Hevy tool schemas and actions for the execution agent."""

from __future__ import annotations

from typing import Any, Callable, Dict, List

from server.services.hevy import (
    get_workouts,
    get_workout_details,
    get_routines,
    get_routine_details,
    create_routine,
    log_workout,
)
from ....logging_config import logger


_SCHEMAS: List[Dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "hevy_get_workouts",
            "description": "Fetch workout history from Hevy to see what exercises the user has completed, including sets, reps, and weights.",
            "parameters": {
                "type": "object",
                "properties": {
                    "page": {
                        "type": "integer",
                        "description": "Page number for pagination (default: 1).",
                        "default": 1,
                    },
                    "page_size": {
                        "type": "integer",
                        "description": "Number of workouts per page (default: 10).",
                        "default": 10,
                    },
                    "start_date": {
                        "type": "string",
                        "description": "Start date in YYYY-MM-DD format to filter workouts.",
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date in YYYY-MM-DD format to filter workouts.",
                    },
                },
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "hevy_get_workout_details",
            "description": "Fetch detailed information for a specific workout including all exercises, sets, reps, weights, and notes.",
            "parameters": {
                "type": "object",
                "properties": {
                    "workout_id": {
                        "type": "string",
                        "description": "Unique identifier for the workout.",
                    },
                },
                "required": ["workout_id"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "hevy_get_routines",
            "description": "Fetch all saved workout routines from Hevy to see planned workouts and templates.",
            "parameters": {
                "type": "object",
                "properties": {
                    "page": {
                        "type": "integer",
                        "description": "Page number for pagination (default: 1).",
                        "default": 1,
                    },
                    "page_size": {
                        "type": "integer",
                        "description": "Number of routines per page (default: 50).",
                        "default": 50,
                    },
                },
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "hevy_get_routine_details",
            "description": "Fetch detailed information for a specific workout routine including all planned exercises and structure.",
            "parameters": {
                "type": "object",
                "properties": {
                    "routine_id": {
                        "type": "string",
                        "description": "Unique identifier for the routine.",
                    },
                },
                "required": ["routine_id"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "hevy_create_routine",
            "description": "Create a new workout routine in Hevy with specified exercises, sets, and reps. Use this to design workout plans for the user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Name/title of the workout routine (e.g., 'Upper Body Strength').",
                    },
                    "exercises": {
                        "type": "array",
                        "description": "List of exercises in the routine. Each exercise needs exercise_template_id and sets array.",
                        "items": {
                            "type": "object",
                            "properties": {
                                "exercise_template_id": {
                                    "type": "string",
                                    "description": "Hevy exercise template identifier (get from exercise_templates endpoint).",
                                },
                                "superset_id": {
                                    "type": "integer",
                                    "description": "Optional superset grouping ID for exercises performed together.",
                                },
                                "rest_seconds": {
                                    "type": "integer",
                                    "description": "Rest time between sets in seconds.",
                                },
                                "sets": {
                                    "type": "array",
                                    "description": "Array of sets for this exercise.",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "type": {
                                                "type": "string",
                                                "description": "Set type: 'normal', 'warmup', 'dropset', or 'failure'.",
                                                "enum": [
                                                    "normal",
                                                    "warmup",
                                                    "dropset",
                                                    "failure",
                                                ],
                                            },
                                            "weight_kg": {
                                                "type": "number",
                                                "description": "Target weight in kilograms.",
                                            },
                                            "reps": {
                                                "type": "integer",
                                                "description": "Target number of reps.",
                                            },
                                            "distance_meters": {
                                                "type": "number",
                                                "description": "Distance in meters (for cardio exercises).",
                                            },
                                            "duration_seconds": {
                                                "type": "integer",
                                                "description": "Duration in seconds (for timed exercises).",
                                            },
                                        },
                                        "required": ["type"],
                                    },
                                },
                            },
                            "required": ["exercise_template_id", "sets"],
                        },
                    },
                    "folder_id": {
                        "type": "string",
                        "description": "Optional folder ID to organize this routine.",
                    },
                },
                "required": ["title", "exercises"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "hevy_log_workout",
            "description": "Log a completed workout in Hevy with exercises, sets, reps, and weights. Use this to track the user's training progress.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Workout title (e.g., 'Morning Chest Day').",
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional workout description or notes.",
                    },
                    "start_time": {
                        "type": "string",
                        "description": "ISO format datetime when workout started.",
                    },
                    "end_time": {
                        "type": "string",
                        "description": "ISO format datetime when workout ended.",
                    },
                    "exercises": {
                        "type": "array",
                        "description": "List of exercises performed.",
                        "items": {
                            "type": "object",
                            "properties": {
                                "exercise_id": {
                                    "type": "string",
                                    "description": "Hevy exercise identifier.",
                                },
                                "sets": {
                                    "type": "array",
                                    "description": "List of sets performed.",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "reps": {"type": "integer"},
                                            "weight_kg": {"type": "number"},
                                        },
                                        "required": ["reps", "weight_kg"],
                                    },
                                },
                            },
                            "required": ["exercise_id", "sets"],
                        },
                    },
                },
                "required": ["title", "start_time", "end_time", "exercises"],
                "additionalProperties": False,
            },
        },
    },
]


def _hevy_get_workouts(
    page: int = 1,
    page_size: int = 10,
    start_date: str = None,
    end_date: str = None,
) -> str:
    """Fetch workout history from Hevy."""
    try:
        data = get_workouts(page, page_size, start_date, end_date)
        logger.info(f"Retrieved Hevy workouts (page {page}, size {page_size})")
        return str(data)
    except Exception as exc:
        logger.error(f"Failed to get Hevy workouts: {exc}")
        return f"Error fetching workouts: {str(exc)}"


def _hevy_get_workout_details(workout_id: str) -> str:
    """Fetch details for a specific workout."""
    try:
        data = get_workout_details(workout_id)
        logger.info(f"Retrieved Hevy workout details for {workout_id}")
        return str(data)
    except Exception as exc:
        logger.error(f"Failed to get Hevy workout details: {exc}")
        return f"Error fetching workout details: {str(exc)}"


def _hevy_get_routines(page: int = 1, page_size: int = 50) -> str:
    """Fetch all workout routines."""
    try:
        data = get_routines(page, page_size)
        logger.info(f"Retrieved Hevy routines (page {page}, size {page_size})")
        return str(data)
    except Exception as exc:
        logger.error(f"Failed to get Hevy routines: {exc}")
        return f"Error fetching routines: {str(exc)}"


def _hevy_get_routine_details(routine_id: str) -> str:
    """Fetch details for a specific routine."""
    try:
        data = get_routine_details(routine_id)
        logger.info(f"Retrieved Hevy routine details for {routine_id}")
        return str(data)
    except Exception as exc:
        logger.error(f"Failed to get Hevy routine details: {exc}")
        return f"Error fetching routine details: {str(exc)}"


def _hevy_create_routine(
    title: str, exercises: List[Dict[str, Any]], folder_id: str = None
) -> str:
    """Create a new workout routine."""
    try:
        data = create_routine(title, exercises, folder_id)
        logger.info(f"Created Hevy routine: {title}")
        return str(data)
    except Exception as exc:
        logger.error(f"Failed to create Hevy routine: {exc}")
        return f"Error creating routine: {str(exc)}"


def _hevy_log_workout(
    title: str,
    start_time: str,
    end_time: str,
    exercises: List[Dict[str, Any]],
    description: str = None,
) -> str:
    """Log a completed workout."""
    try:
        workout_data = {
            "title": title,
            "start_time": start_time,
            "end_time": end_time,
            "exercises": exercises,
        }
        if description:
            workout_data["description"] = description

        data = log_workout(workout_data)
        logger.info(f"Logged Hevy workout: {title}")
        return str(data)
    except Exception as exc:
        logger.error(f"Failed to log Hevy workout: {exc}")
        return f"Error logging workout: {str(exc)}"


def get_schemas() -> List[Dict[str, Any]]:
    """Return Hevy tool schemas for the LLM."""
    return _SCHEMAS


def build_registry(agent_name: str) -> Dict[str, Callable[..., Any]]:
    """Build registry mapping tool names to callable functions."""
    return {
        "hevy_get_workouts": _hevy_get_workouts,
        "hevy_get_workout_details": _hevy_get_workout_details,
        "hevy_get_routines": _hevy_get_routines,
        "hevy_get_routine_details": _hevy_get_routine_details,
        "hevy_create_routine": _hevy_create_routine,
        "hevy_log_workout": _hevy_log_workout,
    }


__all__ = [
    "get_schemas",
    "build_registry",
]
