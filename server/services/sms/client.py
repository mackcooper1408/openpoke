"""Twilio SMS client for text message integration."""

import json
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi.responses import JSONResponse

from ...config import Settings, get_settings
from ...logging_config import logger

# Storage paths for SMS configuration
_CONFIG_FILE = Path.home() / ".openpoke" / "sms_config.json"


def _ensure_storage_dir() -> None:
    """Ensure the storage directory exists."""
    _CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)


def _load_config() -> Dict[str, Any]:
    """Load SMS configuration from file."""
    _ensure_storage_dir()
    if not _CONFIG_FILE.exists():
        return {}
    try:
        return json.loads(_CONFIG_FILE.read_text())
    except Exception as e:
        logger.error("failed to load SMS config", extra={"error": str(e)})
        return {}


def _save_config(config: Dict[str, Any]) -> None:
    """Save SMS configuration to file."""
    _ensure_storage_dir()
    try:
        _CONFIG_FILE.write_text(json.dumps(config, indent=2))
        logger.info("SMS config saved")
    except Exception as e:
        logger.error("failed to save SMS config", extra={"error": str(e)})


def _get_twilio_client():
    """Get Twilio client instance."""
    try:
        from twilio.rest import Client
    except ImportError:
        raise ImportError(
            "Twilio SDK not installed. Run: pip install twilio"
        )

    settings = get_settings()
    config = _load_config()

    # Prefer environment variables over stored config
    account_sid = settings.twilio_account_sid or config.get("account_sid")
    auth_token = settings.twilio_auth_token or config.get("auth_token")
    
    if not account_sid or not auth_token:
        raise ValueError("Twilio credentials not configured")

    return Client(account_sid, auth_token)


def get_sms_status() -> JSONResponse:
    """Check if SMS is configured and connected."""
    settings = get_settings()
    config = _load_config()

    # Check if credentials are available
    has_credentials = bool(
        (settings.twilio_account_sid or config.get("account_sid"))
        and (settings.twilio_auth_token or config.get("auth_token"))
    )

    phone_number = settings.twilio_phone_number or config.get("phone_number")

    if has_credentials:
        try:
            # Verify credentials by making a test API call
            client = _get_twilio_client()
            # Try to fetch account details to verify credentials
            client.api.accounts(client.account_sid).fetch()
            
            return JSONResponse(
                content={
                    "connected": True,
                    "phone_number": phone_number,
                    "source": "environment" if settings.twilio_account_sid else "stored",
                }
            )
        except Exception as e:
            logger.error("Twilio connection failed", extra={"error": str(e)})
            return JSONResponse(
                content={
                    "connected": False,
                    "error": "Invalid credentials or connection error",
                }
            )

    return JSONResponse(content={"connected": False})


def connect_sms(
    account_sid: str, auth_token: str, phone_number: str
) -> JSONResponse:
    """
    Connect to Twilio SMS service with provided credentials.
    
    Args:
        account_sid: Twilio Account SID
        auth_token: Twilio Auth Token
        phone_number: Twilio phone number (format: +1234567890)
    """
    try:
        from twilio.rest import Client
    except ImportError:
        return JSONResponse(
            content={
                "ok": False,
                "error": "Twilio SDK not installed. Run: pip install twilio",
            },
            status_code=500,
        )

    # Validate credentials by testing connection
    try:
        client = Client(account_sid, auth_token)
        # Verify credentials
        client.api.accounts(account_sid).fetch()
        
        # Verify phone number belongs to account
        try:
            incoming_numbers = client.incoming_phone_numbers.list(
                phone_number=phone_number
            )
            if not incoming_numbers:
                return JSONResponse(
                    content={
                        "ok": False,
                        "error": "Phone number not found in your Twilio account",
                    },
                    status_code=400,
                )
        except Exception as e:
            logger.warning("Could not verify phone number", extra={"error": str(e)})

        # Save credentials
        config = {
            "account_sid": account_sid,
            "auth_token": auth_token,
            "phone_number": phone_number,
        }
        _save_config(config)

        logger.info("SMS connected successfully")
        return JSONResponse(
            content={"ok": True, "phone_number": phone_number}
        )

    except Exception as e:
        logger.error("Twilio connection failed", extra={"error": str(e)})
        return JSONResponse(
            content={
                "ok": False,
                "error": f"Failed to connect to Twilio: {str(e)}",
            },
            status_code=400,
        )


def disconnect_sms() -> JSONResponse:
    """Disconnect SMS by clearing stored credentials."""
    try:
        if _CONFIG_FILE.exists():
            _CONFIG_FILE.unlink()
        logger.info("SMS disconnected")
        return JSONResponse(content={"ok": True})
    except Exception as e:
        logger.error("Failed to disconnect SMS", extra={"error": str(e)})
        return JSONResponse(
            content={"ok": False, "error": str(e)}, status_code=500
        )


def send_sms(to_number: str, message: str) -> Dict[str, Any]:
    """
    Send an SMS message.
    
    Args:
        to_number: Recipient phone number (format: +1234567890)
        message: Message text to send
        
    Returns:
        Dict with success status and message details
    """
    settings = get_settings()
    config = _load_config()

    from_number = settings.twilio_phone_number or config.get("phone_number")
    if not from_number:
        raise ValueError("Twilio phone number not configured")

    try:
        client = _get_twilio_client()
        
        # Send message
        sms = client.messages.create(
            to=to_number,
            from_=from_number,
            body=message
        )
        
        logger.info(
            "SMS sent",
            extra={
                "to": to_number,
                "sid": sms.sid,
                "status": sms.status,
            },
        )
        
        return {
            "success": True,
            "sid": sms.sid,
            "status": sms.status,
            "to": to_number,
        }
        
    except Exception as e:
        logger.error("Failed to send SMS", extra={"error": str(e), "to": to_number})
        return {
            "success": False,
            "error": str(e),
        }


async def handle_incoming_sms(from_number: str, message_body: str) -> str:
    """
    Handle an incoming SMS message by routing it to the chat handler.
    
    Args:
        from_number: Sender's phone number
        message_body: Message text content
        
    Returns:
        Response message to send back
    """
    from ...services.conversation.chat_handler import handle_chat_request
    from ...models import ChatMessage, ChatRequest

    logger.info(
        "Incoming SMS",
        extra={"from": from_number, "message_length": len(message_body)},
    )

    try:
        # Create a chat request from the SMS
        chat_message = ChatMessage(role="user", content=message_body)
        chat_request = ChatRequest(messages=[chat_message])

        # Process through the chat handler
        # Note: We'll need to modify chat_handler to support SMS responses
        from ...agents.interaction_agent.runtime import InteractionAgentRuntime

        runtime = InteractionAgentRuntime()
        
        # Execute and get response
        # For SMS, we need a synchronous response
        response = await runtime.execute_sync(user_message=message_body)
        
        # Send the response back via SMS
        send_sms(to_number=from_number, message=response)
        
        return "Message processed"
        
    except Exception as e:
        logger.error("Failed to process incoming SMS", extra={"error": str(e)})
        error_msg = "Sorry, I encountered an error processing your message."
        send_sms(to_number=from_number, message=error_msg)
        return f"Error: {str(e)}"
