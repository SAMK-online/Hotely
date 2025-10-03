#!/usr/bin/env python
"""
HotelPilot Quick Start Launcher
================================
Choose which interface to run.
"""

import os
import sys
import subprocess
import time

def print_banner():
    print("""
    ╔═══════════════════════════════════════╗
    ║      🏨 HotelPilot Launcher 🏨        ║
    ║   Multi-Agent Hotel Operations AI     ║
    ╚═══════════════════════════════════════╝
    """)

def check_dependencies():
    """Check if required packages are installed"""
    required = ['flask', 'flask-cors', 'google-generativeai', 'python-dotenv']
    missing = []

    for package in required:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing.append(package)

    if missing:
        print(f"⚠️  Missing packages: {', '.join(missing)}")
        print("\nInstalling missing packages...")
        subprocess.run([sys.executable, "-m", "pip", "install"] + missing)
        print("✅ Dependencies installed!\n")
    else:
        print("✅ All dependencies installed!\n")

def check_api_key():
    """Check if Gemini API key is configured"""
    from dotenv import load_dotenv
    load_dotenv('hotelpilot/.env')

    api_key = os.getenv('GOOGLE_AI_API_KEY', '')
    if not api_key or api_key == 'your_api_key_here':
        print("⚠️  Please add your Gemini API key to hotelpilot/.env")
        print("   Get one at: https://aistudio.google.com/app/apikey")
        return False
    return True

def run_option(choice):
    """Run the selected option"""
    try:
        if choice == '1':
            print("\n🌐 Starting Web Interface...")
            print("   Opening: http://localhost:8080")
            print("   Press Ctrl+C to stop\n")
            subprocess.run([sys.executable, "app_simple.py"])

        elif choice == '2':
            print("\n🎤 Starting Voice Interface...")
            print("   Opening: http://localhost:8080/voice")
            print("   Wake word: 'Hey Hotel'")
            print("   Press Ctrl+C to stop\n")
            subprocess.run([sys.executable, "app_simple.py"])
            print("\nOpen http://localhost:8080/voice in your browser")

        elif choice == '3':
            print("\n📞 Starting Retell Phone Agent...")
            retell_key = os.getenv('RETELL_API_KEY', '')
            if not retell_key or retell_key == 'your_retell_api_key_here':
                print("⚠️  Please add your Retell API key to hotelpilot/.env")
                print("   Sign up at: https://retell.ai")
                print("\n📖 See setup_retell.md for detailed instructions")
                return
            print("   Starting on port 5001")
            print("   Press Ctrl+C to stop\n")
            subprocess.run([sys.executable, "retell_agent.py"])

        elif choice == '4':
            print("\n🔧 Starting Advanced Web Interface (with ADK attempt)...")
            print("   Opening: http://localhost:8080")
            print("   Note: This version attempted ADK integration")
            print("   Press Ctrl+C to stop\n")
            subprocess.run([sys.executable, "app.py"])

        elif choice == '5':
            print("\n🚀 Starting Voice WebSocket Server...")
            # First check if flask-socketio is installed
            try:
                import flask_socketio
            except ImportError:
                print("Installing flask-socketio...")
                subprocess.run([sys.executable, "-m", "pip", "install", "flask-socketio"])
            print("   Starting on port 5555")
            print("   Press Ctrl+C to stop\n")
            subprocess.run([sys.executable, "voice_server.py"])

        elif choice == '6':
            print("\n📋 Testing all agents with sample queries...\n")
            test_agents()

    except KeyboardInterrupt:
        print("\n\n👋 Shutting down gracefully...")
    except Exception as e:
        print(f"\n❌ Error: {e}")

def test_agents():
    """Test all agents with sample queries"""
    import google.generativeai as genai
    from dotenv import load_dotenv

    load_dotenv('hotelpilot/.env')
    genai.configure(api_key=os.getenv('GOOGLE_AI_API_KEY'))
    model = genai.GenerativeModel('gemini-2.5-flash')

    test_cases = [
        ("Ops Copilot", "Give me a quick operations summary for 75% occupancy"),
        ("Demand Manager", "Calculate pricing for tomorrow with 20% increased flight demand"),
        ("Guest Lifecycle", "Create a welcome message for John Smith checking in tomorrow"),
        ("Housekeeping", "Schedule 18 checkouts and 22 arrivals with 4 staff"),
        ("Billing", "Create recovery strategy for failed $599 VIP payment")
    ]

    for agent_name, query in test_cases:
        print(f"🤖 {agent_name}:")
        print(f"   Query: {query}")
        try:
            response = model.generate_content(f"As a hotel {agent_name}, briefly answer: {query}")
            print(f"   Response: {response.text[:200]}...")
        except Exception as e:
            print(f"   Error: {e}")
        print()

def main():
    print_banner()
    check_dependencies()

    if not check_api_key():
        print("\n❌ Cannot proceed without API key")
        return

    print("Choose an interface to run:\n")
    print("1️⃣  Web Chat Interface (Recommended)")
    print("   Clean multi-agent chat with all 5 agents")
    print()
    print("2️⃣  Voice Interface (Browser-based)")
    print("   Speak naturally with 'Hey Hotel' wake word")
    print()
    print("3️⃣  Phone Agent (Retell AI)")
    print("   Handle real phone call bookings")
    print()
    print("4️⃣  Advanced Interface (Original)")
    print("   First version with ADK attempts")
    print()
    print("5️⃣  Voice WebSocket Server")
    print("   Real-time voice streaming server")
    print()
    print("6️⃣  Test All Agents")
    print("   Quick functionality test")
    print()
    print("0️⃣  Exit")
    print()

    while True:
        choice = input("Select option (1-6, 0 to exit): ").strip()

        if choice == '0':
            print("\n👋 Goodbye!")
            break
        elif choice in ['1', '2', '3', '4', '5', '6']:
            run_option(choice)
            print("\n" + "="*40 + "\n")
            print("Returned to launcher. Choose another option or 0 to exit.\n")
        else:
            print("Invalid option. Please choose 1-6 or 0 to exit.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")