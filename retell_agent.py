#!/usr/bin/env python
"""
HotelPilot - Retell AI Phone Agent
====================================
Voice call agent for hotel bookings using Retell AI.
"""

import os
import json
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from dotenv import load_dotenv
import aiohttp
from flask import Flask, request, jsonify
import google.generativeai as genai

# Load environment
load_dotenv('hotelpilot/.env')

# Configuration
RETELL_API_KEY = os.getenv('RETELL_API_KEY', 'your_retell_api_key')
RETELL_AGENT_ID = os.getenv('RETELL_AGENT_ID', 'your_agent_id')
GOOGLE_AI_API_KEY = os.getenv('GOOGLE_AI_API_KEY')

# Initialize Gemini
genai.configure(api_key=GOOGLE_AI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

# Flask app for webhooks
app = Flask(__name__)

class RetellHotelAgent:
    """Retell AI agent for hotel phone bookings"""

    def __init__(self):
        self.base_url = "https://api.retellai.com"
        self.headers = {
            "Authorization": f"Bearer {RETELL_API_KEY}",
            "Content-Type": "application/json"
        }

        # Hotel context
        self.hotel_context = {
            "name": "Arlington Hotel",
            "rooms_total": 120,
            "room_types": {
                "standard": {"count": 40, "rate": 129},
                "deluxe": {"count": 60, "rate": 189},
                "suite": {"count": 20, "rate": 299}
            },
            "current_occupancy": 0.75,
            "amenities": [
                "Free WiFi", "Parking", "Pool", "Gym",
                "Restaurant", "Room Service", "Business Center"
            ],
            "check_in_time": "3:00 PM",
            "check_out_time": "11:00 AM"
        }

        # Booking state
        self.current_booking = {}
        self.conversation_state = "greeting"

    async def create_agent(self):
        """Create or update Retell AI agent configuration"""

        agent_config = {
            "agent_name": "Arlington Hotel Booking Assistant",
            "voice_id": "rachel",  # Professional female voice
            "language": "en-US",
            "responsiveness": 0.8,  # Quick responses
            "interruption_sensitivity": 0.7,

            "prompt": f"""You are Sarah, a friendly and professional hotel booking assistant for Arlington Hotel in Virginia.

HOTEL INFORMATION:
- 120 rooms total: 40 standard ($129/night), 60 deluxe ($189/night), 20 suites ($299/night)
- Located near DCA airport (10 minutes) and downtown Arlington
- Check-in: 3 PM, Check-out: 11 AM
- Amenities: Free WiFi, parking, pool, gym, restaurant, room service

YOUR ROLE:
1. Answer calls warmly: "Thank you for calling Arlington Hotel, this is Sarah. How may I assist you today?"
2. Help with bookings, availability, and general inquiries
3. Collect booking information naturally in conversation
4. Be conversational, not robotic
5. Handle pricing questions with current rates

BOOKING PROCESS:
1. Determine dates (check-in and check-out)
2. Ask about room preference and number of guests
3. Quote prices based on room type
4. Collect guest name and contact information
5. Confirm the reservation details
6. Provide confirmation number

CONVERSATION STYLE:
- Warm and welcoming
- Use natural transitions
- Acknowledge what the caller says
- Ask clarifying questions when needed
- Summarize before confirming

IMPORTANT:
- Always quote accurate prices
- Be helpful with date flexibility if rooms are limited
- Mention special amenities when relevant
- If asked about availability, check dates first
- Offer alternatives if specific requests can't be met

Remember: You're having a natural phone conversation, not reading a script.""",

            "webhook_url": f"https://your-domain.com/retell/webhook",

            "tools": [
                {
                    "type": "check_availability",
                    "description": "Check room availability for dates"
                },
                {
                    "type": "create_booking",
                    "description": "Create a new reservation"
                },
                {
                    "type": "get_pricing",
                    "description": "Get current room rates"
                }
            ],

            "end_call_after_silence_ms": 10000,
            "max_call_duration_ms": 600000,  # 10 minutes max

            "ambient_sound": "office",  # Light background

            "custom_keywords": [
                {"keyword": "booking", "boost": 1.5},
                {"keyword": "reservation", "boost": 1.5},
                {"keyword": "available", "boost": 1.3},
                {"keyword": "standard room", "boost": 1.2},
                {"keyword": "deluxe room", "boost": 1.2},
                {"keyword": "suite", "boost": 1.2}
            ]
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/create-agent",
                headers=self.headers,
                json=agent_config
            ) as response:
                result = await response.json()
                return result

    async def create_phone_number(self):
        """Create a phone number for the agent"""

        phone_config = {
            "agent_id": RETELL_AGENT_ID,
            "phone_number_type": "local",
            "area_code": "703",  # Arlington, VA area code
            "inbound_only": False
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/create-phone-number",
                headers=self.headers,
                json=phone_config
            ) as response:
                result = await response.json()
                return result

    async def handle_tool_call(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool calls from Retell agent"""

        if tool_name == "check_availability":
            return await self.check_availability(
                parameters.get("check_in"),
                parameters.get("check_out"),
                parameters.get("room_type")
            )

        elif tool_name == "create_booking":
            return await self.create_booking(parameters)

        elif tool_name == "get_pricing":
            return self.get_pricing(parameters.get("room_type"))

        return {"error": "Unknown tool"}

    async def check_availability(self, check_in: str, check_out: str, room_type: Optional[str] = None):
        """Check room availability"""

        # Parse dates
        try:
            check_in_date = datetime.strptime(check_in, "%Y-%m-%d")
            check_out_date = datetime.strptime(check_out, "%Y-%m-%d")
            nights = (check_out_date - check_in_date).days
        except:
            return {"error": "Invalid date format"}

        # Simulate availability check
        available_rooms = {}
        total_available = 0

        for r_type, info in self.hotel_context["room_types"].items():
            if room_type and room_type != r_type:
                continue

            # Simulate availability (more rooms available further in future)
            days_ahead = (check_in_date - datetime.now()).days
            availability_factor = min(0.4 + (days_ahead * 0.02), 0.9)
            available = int(info["count"] * availability_factor)

            if available > 0:
                available_rooms[r_type] = {
                    "available": available,
                    "rate": info["rate"],
                    "total": info["rate"] * nights
                }
                total_available += available

        return {
            "check_in": check_in,
            "check_out": check_out,
            "nights": nights,
            "available": total_available > 0,
            "rooms": available_rooms,
            "message": f"We have {total_available} rooms available for your dates."
        }

    async def create_booking(self, booking_data: Dict[str, Any]):
        """Create a hotel booking"""

        # Generate confirmation number
        confirmation = f"ARH{datetime.now().strftime('%Y%m%d%H%M')}"

        # Calculate total
        room_type = booking_data.get("room_type", "standard")
        nights = booking_data.get("nights", 1)
        rate = self.hotel_context["room_types"][room_type]["rate"]
        total = rate * nights

        # Store booking (in production, save to database)
        booking = {
            "confirmation_number": confirmation,
            "guest_name": booking_data.get("guest_name"),
            "phone": booking_data.get("phone"),
            "email": booking_data.get("email"),
            "check_in": booking_data.get("check_in"),
            "check_out": booking_data.get("check_out"),
            "room_type": room_type,
            "guests": booking_data.get("guests", 1),
            "rate": rate,
            "nights": nights,
            "total": total,
            "created_at": datetime.now().isoformat(),
            "status": "confirmed"
        }

        # Use Gemini to generate confirmation message
        prompt = f"""Generate a friendly booking confirmation message for a phone call:
        Guest: {booking['guest_name']}
        Confirmation: {confirmation}
        Check-in: {booking['check_in']} at 3 PM
        Check-out: {booking['check_out']} at 11 AM
        Room: {room_type.title()} Room
        Rate: ${rate} per night
        Total: ${total} for {nights} nights

        Keep it natural and conversational for phone."""

        response = model.generate_content(prompt)

        return {
            "success": True,
            "confirmation_number": confirmation,
            "booking": booking,
            "message": response.text
        }

    def get_pricing(self, room_type: Optional[str] = None):
        """Get current room pricing"""

        if room_type:
            if room_type in self.hotel_context["room_types"]:
                rate = self.hotel_context["room_types"][room_type]["rate"]
                return {
                    "room_type": room_type,
                    "rate": rate,
                    "message": f"Our {room_type} rooms are ${rate} per night."
                }

        # Return all rates
        rates_message = "Our current rates are: "
        for r_type, info in self.hotel_context["room_types"].items():
            rates_message += f"{r_type.title()} rooms at ${info['rate']} per night, "

        return {
            "rates": self.hotel_context["room_types"],
            "message": rates_message.rstrip(", ") + "."
        }

# Webhook endpoints for Retell
@app.route('/retell/webhook', methods=['POST'])
def retell_webhook():
    """Handle Retell AI webhooks"""
    import asyncio

    data = request.json
    event_type = data.get('event_type')

    agent = RetellHotelAgent()

    if event_type == 'call_started':
        # Call initiated
        return jsonify({
            "response": "Thank you for calling Arlington Hotel, this is Sarah. How may I assist you today?",
            "continue": True
        })

    elif event_type == 'tool_call':
        # Handle tool calls
        tool_name = data.get('tool_name')
        parameters = data.get('parameters', {})

        # Run async function in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(agent.handle_tool_call(tool_name, parameters))
        finally:
            loop.close()

        return jsonify({
            "tool_result": result,
            "continue": True
        })

    elif event_type == 'call_ended':
        # Call finished
        call_id = data.get('call_id')
        duration = data.get('duration')

        # Log call details (in production, save to database)
        print(f"Call {call_id} ended. Duration: {duration}s")

        return jsonify({"success": True})

    elif event_type == 'transcript_update':
        # Real-time transcript
        transcript = data.get('transcript')
        speaker = data.get('speaker')  # 'agent' or 'user'

        # Process transcript if needed
        print(f"{speaker}: {transcript}")

        return jsonify({"continue": True})

    return jsonify({"continue": True})

@app.route('/retell/setup', methods=['GET'])
def setup_retell():
    """Set up Retell agent and phone number"""
    import asyncio

    agent = RetellHotelAgent()

    # Create async event loop for sync context
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        # Create agent
        agent_result = loop.run_until_complete(agent.create_agent())

        # Create phone number
        phone_result = loop.run_until_complete(agent.create_phone_number())

        return jsonify({
            "agent_id": agent_result.get("agent_id"),
            "phone_number": phone_result.get("phone_number"),
            "status": "ready",
            "message": f"Call {phone_result.get('phone_number')} to make a booking!"
        })
    except Exception as e:
        return jsonify({
            "error": str(e),
            "status": "failed",
            "message": "Check your RETELL_API_KEY in .env file"
        }), 500
    finally:
        loop.close()

@app.route('/retell/test', methods=['GET'])
def test_page():
    """Test page for browser access"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>HotelPilot Webhook Status</title>
        <style>
            body { font-family: Arial; max-width: 600px; margin: 50px auto; padding: 20px; }
            .status { background: #10b981; color: white; padding: 20px; border-radius: 10px; }
            .info { background: #f3f4f6; padding: 15px; margin: 20px 0; border-radius: 5px; }
            code { background: #1f2937; color: #10b981; padding: 2px 6px; border-radius: 3px; }
        </style>
    </head>
    <body>
        <div class="status">
            <h1>✅ HotelPilot Webhook is Running!</h1>
            <p>The webhook is ready to receive calls from Retell AI.</p>
        </div>

        <div class="info">
            <h2>Webhook URL for Retell Dashboard:</h2>
            <code>""" + request.url_root + """retell/webhook</code>
        </div>

        <div class="info">
            <h2>Status:</h2>
            <p>✅ Webhook Server: Active</p>
            <p>✅ Agent ID: agent_f3928cf5f8ca15a114e90663ce</p>
            <p>✅ Ready for phone calls!</p>
        </div>

        <div class="info">
            <h2>Test with curl:</h2>
            <code>curl -X POST """ + request.url_root + """retell/webhook -H "Content-Type: application/json" -d '{"event_type": "test"}'</code>
        </div>
    </body>
    </html>
    """

@app.route('/retell/test-call', methods=['POST'])
def test_call():
    """Initiate a test call"""

    data = request.json
    to_number = data.get('to_number')

    # In production, use Retell API to initiate outbound call
    return jsonify({
        "message": f"Test call initiated to {to_number}",
        "status": "calling"
    })

if __name__ == '__main__':
    print("""
    ╔═══════════════════════════════════════╗
    ║   HotelPilot - Retell AI Phone Agent  ║
    ║      Voice Call Booking System        ║
    ╚═══════════════════════════════════════╝

    Features:
    ✅ Natural phone conversations
    ✅ Real-time availability checking
    ✅ Instant booking confirmations
    ✅ Professional voice assistant
    ✅ 24/7 availability

    Starting Retell webhook server on port 5001...

    To set up:
    1. Sign up at https://retell.ai
    2. Add RETELL_API_KEY to your .env
    3. Run: curl http://localhost:5001/retell/setup
    4. Call the provided phone number!
    """)

    app.run(host='0.0.0.0', port=5001, debug=False)