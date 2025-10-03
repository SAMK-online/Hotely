#!/usr/bin/env python
"""
HotelPilot Web Application
===========================
Flask web interface for the multi-agent hotel operations system.
"""

import os
import json
from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from datetime import datetime
from dotenv import load_dotenv
import google.generativeai as genai
import logging

# Load environment
load_dotenv('hotelpilot/.env')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)
CORS(app)

# Configure Gemini
api_key = os.getenv('GOOGLE_AI_API_KEY')
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    logger.info(f"✅ Gemini API configured with key: {api_key[:10]}...")
else:
    model = None
    logger.error("❌ No API key found in environment")

# Agent configurations
AGENTS = {
    "ops_copilot": {
        "name": "Ops Copilot",
        "icon": "🎯",
        "description": "Main operations supervisor",
        "instruction": """You are the Ops Copilot for Arlington Hotel, a 120-room hotel in Arlington, Virginia.

        Hotel details:
        - Rooms: 40 standard ($129), 60 deluxe ($189), 20 suites ($299)
        - Average occupancy: 75%
        - Location: Near DCA (60% weight), IAD (30%), BWI (10%)

        Pricing rules:
        - Weekday cap: +10%
        - Weekend cap: +12%
        - Weekly cap: +18%

        Provide concise, actionable recommendations."""
    },
    "demand_manager": {
        "name": "Demand Manager",
        "icon": "📊",
        "description": "Dynamic pricing analyst",
        "instruction": """You are the Demand Manager for Arlington Hotel.

        Calculate demand lift index:
        - DCA weight: 60%
        - IAD weight: 30%
        - BWI weight: 10%

        Pricing thresholds:
        - DLI 0.2-0.4: Suggest +5-8%
        - DLI 0.4-0.7: Suggest +9-15%
        - DLI >0.7: Up to cap

        Show calculations and confidence level."""
    },
    "guest_lifecycle": {
        "name": "Guest Lifecycle",
        "icon": "✉️",
        "description": "Guest communications manager",
        "instruction": """You manage guest communications for Arlington Hotel.

        Timeline:
        - T-24h: Welcome message
        - T-2h: Mobile check-in
        - T+0: Room ready
        - T+checkout: Thank you

        Rules:
        - Max 3 messages per day
        - Quiet hours: 9 PM - 8 AM
        - Be warm and professional."""
    },
    "housekeeping": {
        "name": "Housekeeping Scheduler",
        "icon": "🧹",
        "description": "Room operations optimizer",
        "instruction": """You manage housekeeping for Arlington Hotel.

        Standards:
        - Standard clean: 24.5 minutes
        - Rush clean: 30-minute window
        - Deep clean: 45 minutes
        - VIP rooms: Require inspection

        Create optimized schedules with staff assignments."""
    },
    "billing": {
        "name": "Billing Recovery",
        "icon": "💳",
        "description": "Payment recovery specialist",
        "instruction": """You handle payment recovery for Arlington Hotel.

        Strategy:
        - T+1h: Silent retry
        - T+6h: Email notification
        - T+24h: Multi-channel contact
        - T+48h: Final notice

        Target: 65% recovery within 48 hours."""
    }
}

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html', agents=AGENTS)

@app.route('/api/process', methods=['POST'])
def process_request():
    """Process a request with the selected agent"""
    try:
        data = request.json
        agent_id = data.get('agent', 'ops_copilot')
        user_input = data.get('input', '')

        if not model:
            return jsonify({
                'error': 'API key not configured',
                'message': 'Please add GOOGLE_AI_API_KEY to hotelpilot/.env'
            }), 500

        if not user_input:
            return jsonify({'error': 'No input provided'}), 400

        # Get agent configuration
        agent_config = AGENTS.get(agent_id, AGENTS['ops_copilot'])

        # Build prompt with agent instruction
        prompt = f"{agent_config['instruction']}\n\nUser request: {user_input}"

        # Generate response
        response = model.generate_content(prompt)

        # Log the interaction
        logger.info(f"Agent: {agent_config['name']}, Request: {user_input[:50]}...")

        return jsonify({
            'success': True,
            'agent': agent_config['name'],
            'response': response.text,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Error processing request: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/scenarios')
def get_scenarios():
    """Get predefined scenarios"""
    scenarios = {
        "pricing": {
            "title": "Dynamic Pricing Analysis",
            "agent": "demand_manager",
            "prompt": """Analyze pricing for tomorrow (Friday, Dec 20):
- DCA airport: +15% capacity (1,200 extra seats)
- IAD airport: +10% capacity (1,000 extra seats)
- Current occupancy: 78%
- No major events

Calculate demand lift and recommend pricing adjustments."""
        },
        "guest": {
            "title": "Guest Communication",
            "agent": "guest_lifecycle",
            "prompt": """Create pre-arrival communication for:
Guest: Sarah Johnson (VIP)
Email: sarah@example.com
Reservation: RES-2024-1220
Check-in: Tomorrow 3 PM
Room: Suite 501 ($299/night)
Preferences: Usually requests late checkout

Create welcome message and upsell opportunities."""
        },
        "housekeeping": {
            "title": "Housekeeping Schedule",
            "agent": "housekeeping",
            "prompt": """Optimize housekeeping for today:
- 18 checkouts by 11 AM
- 22 arrivals from 3 PM (including 2 VIP suites)
- 35 stayovers
- Staff: Maria, John, Sarah (8-4), Carlos (12-6)
- Special: Room 305 needs early check-in by 1 PM

Create optimized schedule."""
        },
        "payment": {
            "title": "Payment Recovery",
            "agent": "billing",
            "prompt": """Handle failed payments:
1. Sarah Johnson: $599, insufficient_funds (VIP, 8 previous stays)
2. Mike Wilson: $129, card_declined (first-time guest)
3. Group Booking: $1,847, expired_card (10 rooms)
Total at risk: $2,575

Create recovery strategy with timeline."""
        },
        "summary": {
            "title": "Daily Operations Summary",
            "agent": "ops_copilot",
            "prompt": """Generate operations summary for today:
- Occupancy: 79% (95/120 rooms)
- ADR: $147 (target: $135)
- RevPAR: $116.13
- Arrivals: 22 (2 VIP)
- Departures: 18
- Housekeeping: 95% on-time
- Payments: $1,890 recovered of $2,200 failed
- Issues: Room 412 AC repair, resolved noise complaint

Create executive summary with action items."""
        }
    }
    return jsonify(scenarios)

@app.route('/api/status')
def status():
    """Check system status"""
    return jsonify({
        'status': 'online',
        'api_configured': bool(api_key),
        'agents_available': len(AGENTS),
        'model': 'gemini-2.5-flash' if model else None
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    debug = os.getenv('FLASK_ENV') == 'development'

    print(f"""
    ╔═══════════════════════════════════════╗
    ║     HotelPilot Web Interface          ║
    ║   Multi-Agent Hotel Operations AI     ║
    ╚═══════════════════════════════════════╝

    ✅ Starting server on http://localhost:{port}

    Available agents:
    {chr(10).join([f"  {agent['icon']} {agent['name']}" for agent in AGENTS.values()])}

    Press Ctrl+C to stop the server
    """)

    app.run(host='0.0.0.0', port=port, debug=debug)