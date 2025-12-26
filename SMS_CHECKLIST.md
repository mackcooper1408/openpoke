# SMS Integration Checklist

Use this checklist to set up SMS text messaging for your OpenPoke assistant.

## ✅ Pre-Setup

- [ ] Backend server running (`python -m server.server`)
- [ ] Frontend running (`npm run dev --prefix web`)
- [ ] Basic OpenPoke setup complete (OpenRouter API key configured)

## ✅ Installation

- [ ] Install Twilio SDK: `pip install twilio`
- [ ] Verify installation: `python -c "import twilio; print('OK')"`

## ✅ Twilio Account Setup

- [ ] Sign up at [twilio.com/try-twilio](https://www.twilio.com/try-twilio)
- [ ] Get free trial credit (usually $15-20)
- [ ] Navigate to [console.twilio.com](https://console.twilio.com)
- [ ] Copy **Account SID** (starts with "AC")
- [ ] Copy **Auth Token** (show/hide button)
- [ ] Purchase or get trial phone number:
  - [ ] Go to Phone Numbers → Manage → Buy a number
  - [ ] Select number with SMS capability
  - [ ] Complete purchase
  - [ ] Note your number (format: +1234567890)

## ✅ Configuration

Choose ONE option:

### Option A: Environment Variables (Recommended)

- [ ] Add to `.env` file:
  ```bash
  TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
  TWILIO_AUTH_TOKEN=your_auth_token_here
  TWILIO_PHONE_NUMBER=+1234567890
  ```
- [ ] Restart backend server

### Option B: Web Interface

- [ ] Open [http://localhost:3000](http://localhost:3000)
- [ ] Click Settings (gear icon)
- [ ] Scroll to "SMS Text Messaging" section
- [ ] Enter Account SID
- [ ] Enter Auth Token
- [ ] Enter Phone Number
- [ ] Click "Connect SMS"
- [ ] Verify status shows "Connected"

## ✅ Webhook Setup (Local Development)

- [ ] Install ngrok: `brew install ngrok` (macOS) or download from [ngrok.com](https://ngrok.com)
- [ ] Start ngrok: `ngrok http 8001`
- [ ] Copy ngrok HTTPS URL (e.g., `https://abc123.ngrok.io`)
- [ ] Go to [console.twilio.com/phone-numbers](https://console.twilio.com/us1/develop/phone-numbers/manage/incoming)
- [ ] Click your phone number
- [ ] Scroll to "Messaging Configuration"
- [ ] Find "A MESSAGE COMES IN"
- [ ] Set Webhook to: `https://YOUR-NGROK-URL.ngrok.io/api/v1/sms/webhook`
- [ ] Set HTTP Method to: `POST`
- [ ] Click "Save"

## ✅ Testing

- [ ] Send test message to your Twilio number
- [ ] Verify message received on phone
- [ ] Check server logs for processing:
  ```bash
  # Look for "SMS webhook received" and "Incoming SMS"
  ```
- [ ] Verify response received on phone
- [ ] Test conversation flow with multiple messages

## ✅ Verification Commands

Run these to verify setup:

- [ ] Backend status:

  ```bash
  curl http://localhost:8001/api/v1/sms/status | python3 -m json.tool
  ```

  Should show: `"connected": true`

- [ ] Frontend proxy status:

  ```bash
  curl http://localhost:3000/api/sms/status | python3 -m json.tool
  ```

  Should show: `"connected": true`

- [ ] Manual webhook test:
  ```bash
  curl -X POST http://localhost:8001/api/v1/sms/webhook \
    -d "From=+1234567890" \
    -d "Body=Test message" \
    -d "MessageSid=SM123"
  ```
  Should return: XML response

## ✅ Production Setup (When Ready)

- [ ] Deploy backend to production server
- [ ] Get production server public URL
- [ ] Update Twilio webhook to production URL:
  ```
  https://yourdomain.com/api/v1/sms/webhook
  ```
- [ ] Test from phone
- [ ] Monitor Twilio usage/costs in console
- [ ] Set up billing alerts in Twilio console

## 🐛 Troubleshooting Checklist

If SMS not working:

- [ ] Verify Twilio credentials are correct
- [ ] Restart backend server after adding credentials
- [ ] Check ngrok is still running (URLs expire)
- [ ] Verify webhook URL matches ngrok URL exactly
- [ ] Check Twilio console → Monitor → Logs for errors
- [ ] Verify sufficient Twilio account balance
- [ ] Check server logs for errors
- [ ] Test backend directly (bypass ngrok):
  ```bash
  curl -X POST http://localhost:8001/api/v1/sms/webhook \
    -d "From=+1234567890" -d "Body=Test"
  ```
- [ ] Verify phone number format includes country code (+1)
- [ ] Check firewall/network allows Twilio webhooks

## 📋 Quick Reference

| What                 | Where                                                                                                    |
| -------------------- | -------------------------------------------------------------------------------------------------------- |
| Backend SMS API      | `http://localhost:8001/api/v1/sms/*`                                                                     |
| Frontend Proxy       | `http://localhost:3000/api/sms/*`                                                                        |
| Webhook Endpoint     | `/api/v1/sms/webhook`                                                                                    |
| Twilio Console       | [console.twilio.com](https://console.twilio.com)                                                         |
| Twilio Phone Numbers | [console.twilio.com/phone-numbers](https://console.twilio.com/us1/develop/phone-numbers/manage/incoming) |
| ngrok Dashboard      | [dashboard.ngrok.com](https://dashboard.ngrok.com)                                                       |

## 📚 Documentation

- [ ] Read [SMS_QUICKSTART.md](SMS_QUICKSTART.md) - 5-minute guide
- [ ] Read [SMS_SETUP_GUIDE.md](SMS_SETUP_GUIDE.md) - Detailed instructions
- [ ] Review [SMS_ARCHITECTURE.md](SMS_ARCHITECTURE.md) - System overview
- [ ] Check [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - Implementation details

## ✨ Success!

When complete, you should be able to:

- ✅ Text your Twilio number
- ✅ Receive AI assistant responses
- ✅ Have full conversations via SMS
- ✅ Access all agent capabilities (Gmail, Whoop, Hevy, etc.)
- ✅ Maintain conversation context across messages

---

**Need Help?** See [SMS_SETUP_GUIDE.md](SMS_SETUP_GUIDE.md) for detailed troubleshooting.
