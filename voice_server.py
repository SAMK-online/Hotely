#!/usr/bin/env python
"""
HotelPilot Voice Server
=======================
WebSocket server for real-time voice processing with streaming responses.
"""

import os
import asyncio
import json
import base64
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from dotenv import load_dotenv
import google.generativeai as genai
from google.cloud import speech_v1
from google.cloud import texttospeech_v1
import numpy as np

# Load environment
load_dotenv('hotelpilot/.env')

# Initialize Flask with SocketIO
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
socketio = SocketIO(app, cors_allowed_origins="*")

# Configure Gemini
genai.configure(api_key=os.getenv('GOOGLE_AI_API_KEY'))
model = genai.GenerativeModel('gemini-2.5-flash')

# Google Cloud Speech clients (optional - for better accuracy)
USE_GOOGLE_CLOUD = os.getenv('GOOGLE_CLOUD_CREDENTIALS') is not None

if USE_GOOGLE_CLOUD:
    speech_client = speech_v1.SpeechClient()
    tts_client = texttospeech_v1.TextToSpeechClient()
else:
    speech_client = None
    tts_client = None

# Agent configurations
AGENTS = {
    "ops_copilot": {
        "name": "Ops Copilot",
        "voice": "en-US-Wavenet-F",  # Professional female voice
        "personality": "professional and efficient",
        "prompt": """You are the Operations Supervisor for Arlington Hotel.
        Speak naturally and conversationally. Keep responses brief for voice."""
    },
    "demand_manager": {
        "name": "Revenue Manager",
        "voice": "en-US-Wavenet-D",  # Analytical male voice
        "personality": "analytical and precise",
        "prompt": """You are the Revenue Manager. Speak clearly about pricing
        and numbers. Round to nearest dollar for voice clarity."""
    },
    "guest_lifecycle": {
        "name": "Guest Relations",
        "voice": "en-US-Wavenet-C",  # Warm female voice
        "personality": "warm and welcoming",
        "prompt": """You are Guest Relations. Be warm and personable.
        Speak as if talking directly to the guest."""
    }
}

# Current context
current_context = {
    "agent": "ops_copilot",
    "conversation": [],
    "wake_word_active": False
}

@app.route('/')
def index():
    """Serve voice interface page"""
    return render_template('voice.html')

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('Client connected')
    emit('status', {'message': 'Connected to HotelPilot Voice'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected')

@socketio.on('audio_stream')
def handle_audio_stream(data):
    """Handle incoming audio stream for real-time processing"""
    try:
        # Decode base64 audio data
        audio_data = base64.b64decode(data['audio'])

        # Process with speech recognition
        if USE_GOOGLE_CLOUD:
            transcript = process_with_google_speech(audio_data)
        else:
            # Use browser's recognition result
            transcript = data.get('transcript', '')

        if transcript:
            # Check for wake word
            if check_wake_word(transcript):
                current_context['wake_word_active'] = True
                emit('wake_word_detected', {'status': 'listening'})
                return

            # Process if wake word was detected
            if current_context['wake_word_active']:
                process_voice_command(transcript)
                current_context['wake_word_active'] = False

    except Exception as e:
        emit('error', {'message': str(e)})

def check_wake_word(transcript):
    """Check if wake word is present"""
    wake_words = ['hey hotel', 'okay hotel', 'hello hotel', 'hi hotel']
    text_lower = transcript.lower()
    return any(wake in text_lower for wake in wake_words)

def process_with_google_speech(audio_data):
    """Process audio with Google Cloud Speech-to-Text"""
    if not speech_client:
        return None

    config = speech_v1.RecognitionConfig(
        encoding=speech_v1.RecognitionConfig.AudioEncoding.WEBM_OPUS,
        sample_rate_hertz=48000,
        language_code="en-US",
        enable_automatic_punctuation=True,
        model="latest_short"
    )

    audio = speech_v1.RecognitionAudio(content=audio_data)
    response = speech_client.recognize(config=config, audio=audio)

    if response.results:
        return response.results[0].alternatives[0].transcript
    return None

@socketio.on('voice_command')
def process_voice_command(transcript):
    """Process voice command and generate response"""
    try:
        # Check for agent switch
        agent = detect_agent_switch(transcript)
        if agent:
            current_context['agent'] = agent
            emit('agent_switched', {'agent': AGENTS[agent]['name']})
            response = f"Switched to {AGENTS[agent]['name']}"
        else:
            # Process with current agent
            agent_config = AGENTS[current_context['agent']]

            # Build prompt
            prompt = f"""{agent_config['prompt']}

User said: {transcript}

Respond conversationally in 2-3 sentences maximum:"""

            # Generate response
            response = model.generate_content(prompt).text

        # Add to conversation
        current_context['conversation'].append({
            'user': transcript,
            'agent': current_context['agent'],
            'response': response
        })

        # Generate speech if Google Cloud TTS available
        if USE_GOOGLE_CLOUD:
            audio_response = generate_speech(response, current_context['agent'])
            emit('voice_response', {
                'text': response,
                'audio': audio_response,
                'agent': current_context['agent']
            })
        else:
            # Send text for browser TTS
            emit('voice_response', {
                'text': response,
                'agent': current_context['agent']
            })

    except Exception as e:
        emit('error', {'message': str(e)})

def detect_agent_switch(transcript):
    """Detect if user wants to switch agents"""
    text_lower = transcript.lower()

    if 'pricing' in text_lower or 'revenue' in text_lower or 'rates' in text_lower:
        return 'demand_manager'
    elif 'guest' in text_lower or 'welcome' in text_lower or 'message' in text_lower:
        return 'guest_lifecycle'
    elif 'operations' in text_lower or 'status' in text_lower:
        return 'ops_copilot'

    return None

def generate_speech(text, agent_key):
    """Generate speech using Google Cloud Text-to-Speech"""
    if not tts_client:
        return None

    agent_config = AGENTS[agent_key]

    synthesis_input = texttospeech_v1.SynthesisInput(text=text)

    voice = texttospeech_v1.VoiceSelectionParams(
        language_code="en-US",
        name=agent_config['voice']
    )

    audio_config = texttospeech_v1.AudioConfig(
        audio_encoding=texttospeech_v1.AudioEncoding.MP3,
        speaking_rate=1.0,
        pitch=0.0
    )

    response = tts_client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config
    )

    # Return base64 encoded audio
    return base64.b64encode(response.audio_content).decode('utf-8')

@socketio.on('get_status')
def handle_status_request():
    """Return current system status"""
    emit('status', {
        'current_agent': current_context['agent'],
        'agent_name': AGENTS[current_context['agent']]['name'],
        'conversation_length': len(current_context['conversation']),
        'google_cloud_enabled': USE_GOOGLE_CLOUD
    })

if __name__ == '__main__':
    print("""
    ╔═══════════════════════════════════════╗
    ║   HotelPilot Voice Server             ║
    ║   Real-time Voice Processing          ║
    ╚═══════════════════════════════════════╝

    Starting voice server on http://localhost:5555

    Features:
    - Wake word: "Hey Hotel"
    - Real-time speech recognition
    - Natural voice responses
    - Agent switching by context

    Note: For best results, set up Google Cloud credentials
    """)

    socketio.run(app, host='0.0.0.0', port=5555, debug=False)