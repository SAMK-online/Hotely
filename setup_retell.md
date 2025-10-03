# Retell AI Phone Agent Setup Guide

## Quick Start

### 1. Get Retell AI Credentials

1. Sign up at https://retell.ai
2. Go to Dashboard → API Keys
3. Copy your API key
4. Go to Agents → Create Agent to get an agent ID (or let the setup create one)

### 2. Update .env File

Add these to your `hotelpilot/.env` file:

```bash
# Retell AI Configuration
RETELL_API_KEY=your_retell_api_key_here
RETELL_AGENT_ID=agent_xxxxx  # Optional - will be created if not provided

# Your existing Gemini key
GOOGLE_AI_API_KEY=your_existing_key
```

### 3. Install Dependencies

```bash
pip install aiohttp
```

### 4. Run the Retell Agent

```bash
python retell_agent.py
```

The server will start on port 5001.

### 5. Set Up Webhook (for production)

For local testing, use ngrok to expose your webhook:

```bash
# Install ngrok if you haven't
brew install ngrok  # On Mac

# Expose your local server
ngrok http 5001

# Copy the HTTPS URL (e.g., https://abc123.ngrok.io)
```

Update the webhook URL in retell_agent.py line 114:
```python
"webhook_url": "https://your-ngrok-url.ngrok.io/retell/webhook"
```

### 6. Initialize Your Agent

Once the server is running, create your agent and phone number:

```bash
curl http://localhost:5001/retell/setup
```

This will return:
- Your agent ID
- Your phone number to call
- Confirmation that the system is ready

## Testing Your Phone Agent

### Make a Test Call

Call the phone number provided and try these scenarios:

1. **Basic Booking:**
   - "Hi, I'd like to make a reservation"
   - "I need a room for tomorrow night"
   - "What rooms do you have available?"

2. **Price Inquiry:**
   - "What are your rates?"
   - "How much is a suite?"
   - "Do you have any deals for next weekend?"

3. **Availability Check:**
   - "Do you have any rooms for December 15th?"
   - "I need to stay for 3 nights starting Friday"
   - "What's available next week?"

4. **Complete Booking Flow:**
   - "I'd like to book a deluxe room"
   - "Check-in tomorrow, checkout Sunday"
   - "My name is John Smith"
   - "My phone number is 555-0123"

## How It Works

### Call Flow

1. **Incoming Call** → Retell answers with Sarah's greeting
2. **Speech Recognition** → Converts caller's speech to text
3. **Intent Processing** → Gemini AI understands the request
4. **Tool Execution** → Checks availability, creates bookings
5. **Response Generation** → Natural language response
6. **Text-to-Speech** → Sarah speaks the response

### Available Tools

- **check_availability**: Real-time room availability
- **create_booking**: Complete reservation creation
- **get_pricing**: Current rate information

### Conversation Features

- Natural, conversational tone
- Handles interruptions gracefully
- Remembers context throughout call
- Professional voice (Rachel/Sarah)
- Confirms details before booking

## Configuration Options

### Voice Settings

In retell_agent.py, you can adjust:

```python
"voice_id": "rachel",  # Options: rachel, matthew, amy, brian
"responsiveness": 0.8,  # 0-1, higher = quicker responses
"interruption_sensitivity": 0.7,  # 0-1, higher = easier to interrupt
```

### Call Settings

```python
"end_call_after_silence_ms": 10000,  # End call after 10s silence
"max_call_duration_ms": 600000,  # Max 10 minute calls
"ambient_sound": "office",  # Background ambiance
```

## Monitoring Calls

### Real-time Logs

The server prints:
- Call start/end events
- Real-time transcripts
- Tool executions
- Booking confirmations

### Webhook Events

Your server receives:
- `call_started`: New call initiated
- `tool_call`: Availability/booking requests
- `transcript_update`: Real-time conversation
- `call_ended`: Call completed with duration

## Troubleshooting

### Common Issues

1. **"Invalid API Key"**
   - Check RETELL_API_KEY in .env
   - Ensure no extra spaces

2. **"Agent not found"**
   - Run /retell/setup first
   - Or remove RETELL_AGENT_ID from .env

3. **"Webhook not responding"**
   - Check ngrok is running
   - Update webhook_url in code
   - Ensure port 5001 is free

4. **Poor speech recognition**
   - Ask callers to speak clearly
   - Reduce background noise
   - Adjust interruption_sensitivity

## Production Deployment

For production:

1. Deploy to a cloud service (AWS, GCP, etc.)
2. Use a proper domain with SSL
3. Set up monitoring and logging
4. Configure Retell dashboard with production webhook
5. Add error handling and retry logic
6. Set up database for booking storage

## Cost Estimation

Retell AI pricing (approximate):
- $0.07 per minute of calls
- $0.004 per API request
- Phone number: $2/month

For Arlington Hotel (120 rooms):
- Estimated 50 calls/day × 3 min average = $10.50/day
- Monthly: ~$315 + phone number

## Next Steps

1. Test with various booking scenarios
2. Fine-tune the conversation prompt
3. Add more sophisticated availability logic
4. Integrate with real PMS system
5. Add SMS confirmation capability
6. Implement call recording for quality

---

**Support:**
- Retell Documentation: https://docs.retell.ai
- Dashboard: https://dashboard.retell.ai
- Our Implementation: retell_agent.py