# SMS Text Messaging Setup Guide

This guide will help you set up SMS text messaging so you can interact with your OpenPoke AI assistant via text messages.

## Overview

The SMS integration uses Twilio to enable two-way text messaging with your AI assistant. When you text your Twilio number, the message is processed by your interaction agent and a response is sent back automatically.

## Prerequisites

1. A Twilio account (free trial available at [twilio.com/try-twilio](https://www.twilio.com/try-twilio))
2. A Twilio phone number (can be purchased or use trial number)
3. Python package `twilio` installed
4. A public webhook URL (required for production; use ngrok for local development)

## Setup Steps

### 1. Install Twilio Python SDK

```bash
cd /path/to/openpoke
pip install twilio
```

Or add to `server/requirements.txt`:
```
twilio>=8.0.0
```

### 2. Get Twilio Credentials

1. Sign up at [twilio.com](https://www.twilio.com)
2. Go to the [Twilio Console](https://console.twilio.com)
3. Find your **Account SID** and **Auth Token** on the dashboard
4. Get or purchase a phone number:
   - Navigate to Phone Numbers → Manage → Buy a number
   - Choose a number with SMS capability
   - Complete purchase (free trial includes credit)

### 3. Configure Credentials

**Option A: Environment Variables (Recommended)**

Add to your `.env` file in the project root:

```bash
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+1234567890
```

**Option B: Settings Modal**

1. Start the application
2. Open the Settings modal in the web interface
3. Navigate to the "SMS Text Messaging" section
4. Enter your Twilio credentials
5. Click "Connect SMS"

### 4. Set Up Webhook (Required)

Twilio needs a public URL to send incoming messages to your application.

#### For Local Development (using ngrok):

1. Install ngrok: `brew install ngrok` (macOS) or download from [ngrok.com](https://ngrok.com)

2. Start your backend server:
```bash
cd /path/to/openpoke
python -m server.server
```

3. In a new terminal, start ngrok:
```bash
ngrok http 8001
```

4. Copy the HTTPS forwarding URL (e.g., `https://abc123.ngrok.io`)

5. Configure Twilio webhook:
   - Go to [Twilio Console → Phone Numbers](https://console.twilio.com/us1/develop/phone-numbers/manage/incoming)
   - Click on your phone number
   - Scroll to "Messaging Configuration"
   - Under "A MESSAGE COMES IN":
     - Webhook: `https://abc123.ngrok.io/api/v1/sms/webhook`
     - HTTP Method: `POST`
   - Click "Save"

#### For Production:

Use your actual server URL:
```
https://yourdomain.com/api/v1/sms/webhook
```

### 5. Test the Integration

1. Send a text message to your Twilio phone number
2. Your AI assistant should process the message and respond
3. Check the server logs for message processing details

## Usage

Once configured, simply text your Twilio phone number as you would chat in the web interface. Your messages will be processed through the same interaction agent and you'll receive responses automatically.

**Example conversation:**
- You: "What's my workout schedule today?"
- Assistant: "Let me check your Hevy workouts for today..."

## Verification

### Check Connection Status

**Via Web Interface:**
1. Open Settings modal
2. Look for "SMS Text Messaging" section
3. Status should show "Connected" with your phone number

**Via API:**
```bash
curl http://localhost:3000/api/sms/status | python3 -m json.tool
```

Expected response:
```json
{
  "connected": true,
  "phone_number": "+1234567890",
  "source": "environment"
}
```

### Test Backend Directly

```bash
curl http://localhost:8001/api/v1/sms/status | python3 -m json.tool
```

## Troubleshooting

### "Twilio SDK not installed"
```bash
pip install twilio
```

### "Invalid credentials or connection error"
- Verify Account SID starts with "AC"
- Check Auth Token is correct (regenerate if needed)
- Restart backend server after adding credentials to `.env`

### Messages not received
1. Check webhook URL is correct in Twilio console
2. Verify webhook URL is publicly accessible
3. Check server logs for webhook errors: `tail -f server/logs/*.log`
4. Test webhook manually:
```bash
curl -X POST http://localhost:8001/api/v1/sms/webhook \
  -d "From=%2B1234567890" \
  -d "Body=Test message" \
  -d "MessageSid=SM123"
```

### No response sent
- Check interaction agent is working (test via web interface)
- Verify Twilio phone number is correct
- Check server logs for errors during message processing
- Ensure sufficient Twilio account balance

### ngrok URL keeps changing
- Free ngrok URLs change on restart
- Update Twilio webhook URL each time ngrok restarts
- Consider ngrok paid plan for persistent URLs, or deploy to production

## File Locations

- **Backend Service**: `server/services/sms/client.py`
- **API Routes**: `server/routes/sms.py`
- **Frontend API Proxy**: `web/app/api/sms/*/route.ts`
- **Settings UI**: `web/components/SettingsModal.tsx`
- **Configuration**: `server/config.py`
- **Stored Credentials**: `~/.openpoke/sms_config.json` (if not using env vars)

## Security Notes

- **Never commit credentials** to version control
- Use environment variables for production
- Twilio validates webhook signatures (consider enabling for production)
- Credentials stored in `~/.openpoke/` are in plaintext
- Auth tokens should be treated as passwords

## Cost Considerations

- **Free Trial**: Twilio provides trial credit for testing
- **SMS Pricing**: ~$0.0075 per SMS in the US (varies by country)
- **Phone Number**: ~$1-2/month rental fee
- Check current pricing at [twilio.com/pricing](https://www.twilio.com/pricing)

## Advanced Configuration

### Webhook Signature Validation (Production)

For enhanced security, validate Twilio webhook signatures:

```python
from twilio.request_validator import RequestValidator

validator = RequestValidator(auth_token)
is_valid = validator.validate(url, post_vars, signature)
```

### Custom Phone Number Whitelist

Restrict which numbers can interact with your assistant by adding validation in `handle_incoming_sms()`:

```python
ALLOWED_NUMBERS = ["+1234567890", "+0987654321"]

if from_number not in ALLOWED_NUMBERS:
    return "Unauthorized"
```

### Rate Limiting

Consider adding rate limiting to prevent abuse:
```python
from fastapi_limiter import FastAPILimiter
```

## Resources

- [Twilio Python SDK Documentation](https://www.twilio.com/docs/libraries/python)
- [Twilio Webhooks Guide](https://www.twilio.com/docs/usage/webhooks)
- [ngrok Documentation](https://ngrok.com/docs)
- [OpenPoke Development Guide](./DEVELOPMENT_GUIDE.md)

## Support

For issues or questions:
1. Check server logs for error messages
2. Verify Twilio console shows message delivery
3. Test webhook endpoint manually
4. Review OpenPoke development guide for integration patterns
