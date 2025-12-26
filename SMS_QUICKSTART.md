# 📱 SMS Quick Setup

Text with your AI assistant in 5 minutes!

## 1. Install Twilio SDK
```bash
pip install twilio
```

## 2. Get Twilio Credentials
1. Sign up at [twilio.com](https://www.twilio.com/try-twilio) (free trial)
2. Get your Account SID & Auth Token from dashboard
3. Get a phone number (trial includes free number)

## 3. Add to `.env`
```bash
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890
```

## 4. Setup Webhook (Local Dev)
```bash
# Terminal 1: Start server
python -m server.server

# Terminal 2: Start ngrok
brew install ngrok  # if needed
ngrok http 8001
```

Copy ngrok URL (e.g., `https://abc123.ngrok.io`)

## 5. Configure Twilio
1. Go to [console.twilio.com/phone-numbers](https://console.twilio.com/us1/develop/phone-numbers/manage/incoming)
2. Click your phone number
3. Under "A MESSAGE COMES IN", set:
   - **Webhook**: `https://abc123.ngrok.io/api/v1/sms/webhook`
   - **Method**: POST
4. Save

## 6. Test!
Text your Twilio number and get a response! 🎉

---

**Troubleshooting**: See [SMS_SETUP_GUIDE.md](./SMS_SETUP_GUIDE.md) for detailed help.

**Production**: Replace ngrok URL with your actual server URL.
