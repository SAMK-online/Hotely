# 🏨 Hotely - Multi-Agent AI Hotel Operations System

A comprehensive multi-agent AI system for hotel operations featuring voice interactions, dynamic pricing, guest communications, and automated booking management.

## 🌟 Features

### Multi-Agent Architecture
- **🎯 Ops Copilot**: Operations supervisor coordinating all hotel activities
- **📊 Demand Manager**: Dynamic pricing based on flight signals and occupancy
- **✉️ Guest Lifecycle**: Automated guest communications and journey management
- **🧹 Housekeeping**: Room operations scheduling and optimization
- **💳 Billing Recovery**: Smart payment recovery with tiered strategies

### Communication Channels
- **💬 Web Chat Interface**: Multi-agent chat with real-time responses
- **🎤 Voice Interface**: Browser-based voice interactions with wake word detection
- **📞 Phone Agent**: Retell AI integration for handling phone call bookings
- **🔗 Webhook System**: Real-time event processing for call handling

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Google Gemini API key
- Retell AI API key (for phone features)
- ngrok (for webhook tunneling)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/hotely.git
cd hotely
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment**
```bash
# Edit hotely/.env
GOOGLE_AI_API_KEY=your_gemini_api_key_here
RETELL_API_KEY=your_retell_api_key_here  # Optional for phone features
RETELL_AGENT_ID=agent_xxxxx  # Will be created if not provided
```

4. **Run the launcher**
```bash
python run_hotel.py
```

Choose from:
- Option 1: Web Chat Interface (port 8080)
- Option 2: Voice Interface (browser-based)
- Option 3: Phone Agent (Retell AI)
- Option 6: Test All Agents

## 📱 System Architecture

```
┌─────────────────────────────────────────────────┐
│                   User Interfaces                │
├────────────┬──────────┬──────────┬──────────────┤
│  Web Chat  │  Voice   │  Phone   │   Webhook    │
│   (8080)   │  (8080)  │ (Retell) │    (5001)    │
└────────────┴──────────┴──────────┴──────────────┘
                         │
┌─────────────────────────────────────────────────┐
│              Multi-Agent System                  │
├──────────────────────────────────────────────────┤
│  Ops Copilot → Demand Manager → Guest Lifecycle │
│       ↓              ↓               ↓          │
│  Housekeeping ← Billing Recovery ← Comms Agent  │
└─────────────────────────────────────────────────┘
                         │
┌─────────────────────────────────────────────────┐
│               Google Gemini AI                   │
│            (gemini-2.5-flash model)              │
└─────────────────────────────────────────────────┘
```

## 🎤 Voice & Phone Features

### Browser Voice Interface
Access at `http://localhost:8080/voice`

**Features:**
- Wake word activation: "Hey Hotel"
- Natural language processing
- Text-to-speech responses
- Real-time agent switching

**Voice Commands:**
- "Hey Hotel" - Activate assistant
- "What are today's rates?"
- "I need to book a room"
- "Check availability for tomorrow"

### Phone Agent (Retell AI)

**Setup:**
1. Sign up at [Retell AI](https://retell.ai)
2. Add API key to `.env`
3. Configure ngrok for webhooks:
```bash
ngrok config add-authtoken YOUR_TOKEN
ngrok http 5001
```
4. Add webhook URL to Retell Dashboard

**Webhook Events:**
- `call_started`: Greeting and initial response
- `tool_call`: Availability checks, bookings, pricing
- `transcript_update`: Real-time conversation tracking
- `call_ended`: Call summary and logging

## 💬 Web Chat Interface

Access at `http://localhost:8080`

**Features:**
- Agent selection sidebar
- Quick scenario buttons
- Real-time metrics display
- Conversation history

**Sample Scenarios:**
- Dynamic Pricing Analysis
- Guest Welcome Messages
- Housekeeping Schedules
- Payment Recovery Strategies
- Operations Summaries

## 🏢 Hotel Configuration

**Arlington Hotel** (Demo Property)
- 120 rooms total
- Room types:
  - Standard: 40 rooms @ $129/night
  - Deluxe: 60 rooms @ $189/night
  - Suite: 20 rooms @ $299/night
- Location: Near DCA Airport, Arlington, VA
- Check-in: 3:00 PM
- Check-out: 11:00 AM

## 🔧 API Endpoints

### Retell Webhook
- `POST /retell/webhook` - Handle Retell AI events
- `GET /retell/test` - Status page
- `GET /retell/setup` - Initialize agent

### Web App
- `GET /` - Main chat interface
- `GET /voice` - Voice interface
- `POST /api/process` - Process agent requests
- `GET /api/agents` - List available agents
- `GET /api/scenarios` - Get predefined scenarios

## 🧪 Testing

### Test All Agents
```bash
python run_hotel.py
# Select option 6
```

### Test Retell Connection
```bash
python test_retell.py
```

### Test Phone Webhook
```bash
curl -X POST https://your-ngrok-url.ngrok.io/retell/webhook \
  -H "Content-Type: application/json" \
  -d '{"event_type": "call_started"}'
```

## 📊 Agent Capabilities

### Ops Copilot
- Coordinate all operations
- Provide strategic oversight
- Generate daily summaries
- Handle escalations

### Demand Manager
- Calculate dynamic pricing
- Analyze flight demand signals
- Apply rate caps and adjustments
- Optimize revenue

### Guest Lifecycle
- Pre-arrival communications
- Check-in/checkout messages
- Guest preference tracking
- Feedback collection

### Housekeeping
- Schedule room cleanings
- Prioritize by urgency
- Coordinate with arrivals/departures
- Track cleaning times

### Billing Recovery
- Automated retry strategies
- Tiered recovery approach
- VIP handling
- Payment plan offers

## 🚀 Deployment

### Local Development
```bash
# Run all services
python run_hotel.py

# Individual services
python app_simple.py      # Web interface
python retell_agent.py    # Phone webhook
python voice_server.py    # Voice WebSocket
```

### Production Considerations
- Use production WSGI server (Gunicorn/uWSGI)
- Set up proper SSL certificates
- Configure production database
- Implement rate limiting
- Add monitoring and logging

## 📝 Configuration Files

- `hotelpilot/.env` - Environment variables
- `hotelpilot/config/settings.py` - System configuration
- `CLAUDE.md` - Development guidelines
- `setup_retell.md` - Retell AI setup guide

## 🛠️ Technologies Used

- **Backend**: Python, Flask, Flask-CORS
- **AI/ML**: Google Gemini AI (gemini-2.5-flash)
- **Voice**: Web Speech API, Retell AI
- **Real-time**: WebSockets, ngrok
- **Frontend**: HTML5, JavaScript, CSS3

## 📄 License

MIT License - See LICENSE file for details

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a pull request

## 📞 Support

For issues or questions:
- Open an issue on GitHub
- Check documentation in `/docs`
- Review CLAUDE.md for development guidelines

## 🎯 Roadmap

- [ ] Database integration for persistent storage
- [ ] Advanced analytics dashboard
- [ ] Multi-property support
- [ ] Integration with PMS systems
- [ ] SMS notification support
- [ ] Email automation
- [ ] Revenue optimization ML models
- [ ] Mobile app integration

---

**Built with ❤️ using Google Gemini AI and Retell AI**

*Last Updated: October 2025*
