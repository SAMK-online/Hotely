#!/usr/bin/env python
"""
HotelPilot Web App - Simple Version
====================================
Cleaner implementation without ADK complexity.
"""

import os
import json
import time
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from datetime import datetime
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment
load_dotenv('hotelpilot/.env')

# Initialize Flask
app = Flask(__name__)
app.secret_key = os.urandom(24)
CORS(app)

# Configure Gemini
genai.configure(api_key=os.getenv('GOOGLE_AI_API_KEY'))

class HotelAgent:
    """Simple agent class"""
    def __init__(self, name, role, icon, system_prompt):
        self.name = name
        self.role = role
        self.icon = icon
        self.system_prompt = system_prompt
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def process(self, user_input, context=None):
        """Process user input with this agent"""
        prompt = f"{self.system_prompt}\n\n"
        if context:
            prompt += f"Context: {context}\n\n"
        prompt += f"User: {user_input}\n\nAssistant:"

        response = self.model.generate_content(prompt)
        return response.text

# Initialize agents
AGENTS = {
    "ops_copilot": HotelAgent(
        name="Ops Copilot",
        role="Operations Supervisor",
        icon="🎯",
        system_prompt="""You are the Operations Supervisor for Arlington Hotel (120 rooms).
        Current: 75% occupancy, Rates: $129 standard, $189 deluxe, $299 suite.
        Coordinate all operations and provide strategic oversight.
        Be concise and actionable."""
    ),

    "demand_manager": HotelAgent(
        name="Demand Manager",
        role="Revenue Optimization",
        icon="📊",
        system_prompt="""You are the Revenue Manager for Arlington Hotel.
        Base rates: $129/$189/$299. Current occupancy: 75%.
        Rate caps: Weekday +10%, Weekend +12%, Weekly +18%.
        Airport weights: DCA 60%, IAD 30%, BWI 10%.
        Always show calculations and reasoning."""
    ),

    "guest_lifecycle": HotelAgent(
        name="Guest Lifecycle",
        role="Guest Communications",
        icon="✉️",
        system_prompt="""You manage guest communications for Arlington Hotel.
        Create warm, professional messages. Keep SMS under 160 chars.
        Timeline: T-24h welcome, T-2h check-in, T+0 room ready, T+checkout thanks.
        Respect quiet hours 9PM-8AM."""
    ),

    "housekeeping": HotelAgent(
        name="Housekeeping",
        role="Room Operations",
        icon="🧹",
        system_prompt="""You coordinate housekeeping for Arlington Hotel.
        Times: Standard 24.5min, Rush 30min, Deep clean 45min.
        Prioritize: Checkouts, VIPs, early check-ins, stayovers.
        Create specific schedules with times and assignments."""
    ),

    "billing": HotelAgent(
        name="Billing Recovery",
        role="Payment Processing",
        icon="💳",
        system_prompt="""You handle payment recovery for Arlington Hotel.
        Recovery: T+1h silent retry, T+6h email, T+24h call, T+48h final.
        Target 65% recovery in 48 hours. VIPs get personal attention.
        Be understanding and offer payment plans when appropriate."""
    )
}

# Conversation memory (simple in-memory store)
conversations = {}

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/voice')
def voice():
    """Serve the voice interface"""
    return render_template('voice.html')

@app.route('/api/process', methods=['POST'])
def process_request():
    """Process a request with selected agent"""
    start_time = time.time()

    try:
        data = request.json
        agent_id = data.get('agent', 'ops_copilot')
        user_input = data.get('input', '')
        session_id = data.get('session_id', 'default')

        if not user_input:
            return jsonify({'error': 'No input provided'}), 400

        # Get or create conversation memory
        if session_id not in conversations:
            conversations[session_id] = []

        # Get the agent
        agent = AGENTS.get(agent_id, AGENTS['ops_copilot'])

        # Get recent context (last 3 messages)
        context = conversations[session_id][-3:] if conversations[session_id] else []
        context_str = "\n".join([f"{c['role']}: {c['message'][:100]}..." for c in context])

        # Process with agent
        response = agent.process(user_input, context_str)

        # Store in conversation memory
        conversations[session_id].append({
            'role': 'user',
            'message': user_input,
            'timestamp': datetime.now().isoformat()
        })
        conversations[session_id].append({
            'role': agent.name,
            'message': response,
            'timestamp': datetime.now().isoformat()
        })

        # Keep conversation memory limited
        if len(conversations[session_id]) > 20:
            conversations[session_id] = conversations[session_id][-20:]

        # Calculate response time
        response_time = int((time.time() - start_time) * 1000)

        return jsonify({
            'success': True,
            'agent': agent.name,
            'role': agent.role,
            'response': response,
            'response_time': response_time,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/agents')
def get_agents():
    """Get available agents"""
    return jsonify({
        agent_id: {
            'name': agent.name,
            'role': agent.role,
            'icon': agent.icon
        }
        for agent_id, agent in AGENTS.items()
    })

@app.route('/api/scenarios')
def get_scenarios():
    """Get predefined scenarios"""
    scenarios = {
        "pricing": {
            "title": "Dynamic Pricing",
            "agent": "demand_manager",
            "prompt": "Tomorrow is Saturday. Flight data shows DCA +20% capacity, IAD +15%. Current occupancy 75%. Calculate demand lift and recommend pricing."
        },
        "guest": {
            "title": "Guest Welcome",
            "agent": "guest_lifecycle",
            "prompt": "Create pre-arrival messages for John Smith, checking in tomorrow to Deluxe Room 305 for 3 nights."
        },
        "housekeeping": {
            "title": "Daily Schedule",
            "agent": "housekeeping",
            "prompt": "Create housekeeping schedule: 18 checkouts by 11am, 22 arrivals from 3pm, 4 staff members available."
        },
        "payment": {
            "title": "Payment Recovery",
            "agent": "billing",
            "prompt": "Payment failed: $599 for Sarah Johnson (VIP, 8 previous stays), declined due to insufficient funds. Create recovery strategy."
        },
        "summary": {
            "title": "Operations Summary",
            "agent": "ops_copilot",
            "prompt": "Give me today's operations summary: 79% occupancy, ADR $147, 22 arrivals, 18 departures, 2 maintenance issues."
        }
    }
    return jsonify(scenarios)

@app.route('/api/clear', methods=['POST'])
def clear_conversation():
    """Clear conversation memory"""
    data = request.json
    session_id = data.get('session_id', 'default')
    if session_id in conversations:
        del conversations[session_id]
    return jsonify({'success': True})

@app.route('/health')
def health():
    """Health check"""
    return jsonify({
        'status': 'healthy',
        'agents': len(AGENTS),
        'model': 'gemini-2.5-flash'
    })

if __name__ == '__main__':
    print(f"""
    ╔═══════════════════════════════════════╗
    ║   HotelPilot - Simple Web Interface   ║
    ║      Clean Multi-Agent System         ║
    ╚═══════════════════════════════════════╝

    ✅ Starting on http://localhost:8080

    Agents Available:
    {chr(10).join([f'  {a.icon} {a.name} - {a.role}' for a in AGENTS.values()])}

    No complex dependencies - just clean, simple orchestration!
    """)

    app.run(host='0.0.0.0', port=8080, debug=False)