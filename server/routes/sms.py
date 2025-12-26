"""SMS routes for text message integration."""

from typing import Dict

from fastapi import APIRouter, Form, Request
from fastapi.responses import JSONResponse, Response

from ..services.sms import (
    connect_sms,
    disconnect_sms,
    get_sms_status,
    handle_incoming_sms,
)
from ..logging_config import logger

router = APIRouter(prefix="/sms", tags=["sms"])


@router.get("/status")
async def status() -> JSONResponse:
    """Check SMS connection status."""
    return get_sms_status()


@router.post("/connect")
async def connect(
    account_sid: str = Form(...),
    auth_token: str = Form(...),
    phone_number: str = Form(...),
) -> JSONResponse:
    """
    Connect to Twilio SMS service.

    Args:
        account_sid: Twilio Account SID
        auth_token: Twilio Auth Token
        phone_number: Twilio phone number (format: +1234567890)
    """
    return connect_sms(account_sid, auth_token, phone_number)


@router.post("/disconnect")
async def disconnect() -> JSONResponse:
    """Disconnect SMS service."""
    return disconnect_sms()


@router.post("/webhook")
async def webhook(request: Request) -> Response:
    """
    Webhook endpoint for receiving incoming SMS messages from Twilio.

    Twilio will POST to this endpoint when a message is received.
    """
    try:
        # Parse form data from Twilio
        form_data = await request.form()

        from_number = form_data.get("From", "")
        message_body = form_data.get("Body", "")
        message_sid = form_data.get("MessageSid", "")

        logger.info(
            "SMS webhook received",
            extra={
                "from": from_number,
                "sid": message_sid,
                "body_length": len(message_body),
            },
        )

        # Process the message asynchronously
        import asyncio

        asyncio.create_task(handle_incoming_sms(from_number, message_body))

        # Return empty TwiML response (Twilio expects XML)
        # Since we'll send the response separately, we don't need to include it here
        return Response(
            content='<?xml version="1.0" encoding="UTF-8"?><Response></Response>',
            media_type="application/xml",
        )

    except Exception as e:
        logger.error("SMS webhook error", extra={"error": str(e)})
        # Still return valid TwiML even on error
        return Response(
            content='<?xml version="1.0" encoding="UTF-8"?><Response></Response>',
            media_type="application/xml",
        )


__all__ = ["router"]
