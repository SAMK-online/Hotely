"""
HotelPilot Test Runner
======================
Simple test script to demonstrate the multi-agent system.
"""

import os
import sys
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from google.adk.agents import LlmAgent
from config.settings import config
from tools import pms_tools, flight_tools, payment_tools, messaging_tools, housekeeping_tools

def test_basic_agent():
    """Test a simple agent interaction"""
    print("\n" + "="*60)
    print("HotelPilot Multi-Agent System Test")
    print("="*60)

    # Check API key
    if not config.google_ai_api_key:
        print("❌ ERROR: GOOGLE_AI_API_KEY not configured in .env")
        return
    else:
        print(f"✅ API Key configured")
        print(f"✅ Using model: {config.primary_model}")

    # Create a simple test agent
    test_agent = LlmAgent(
        name="test_agent",
        model=config.primary_model,
        description="Test agent for HotelPilot system",
        instruction="""You are a helpful hotel operations assistant.

        When asked about pricing, mention that rates can be adjusted based on demand.
        When asked about housekeeping, explain the cleaning schedule.
        When asked about payments, describe the recovery process.

        Be concise and professional.""",
        tools=[
            pms_tools.get_room_availability,
            flight_tools.get_flight_arrivals,
            payment_tools.create_payment_link,
            messaging_tools.send_sms,
            housekeeping_tools.get_daily_housekeeping_plan
        ]
    )

    print("\n" + "-"*60)
    print("Available Workflows:")
    print("1. Check room availability and pricing")
    print("2. View flight signals for tomorrow")
    print("3. Generate housekeeping plan")
    print("4. Create payment recovery link")
    print("5. Test all tools")

    choice = input("\nSelect workflow (1-5): ")

    workflows = {
        "1": "Check room availability for tomorrow and suggest pricing based on current demand.",
        "2": "Get flight arrival signals from DCA airport for tomorrow and calculate demand impact.",
        "3": "Generate a housekeeping plan for today with 10 checkouts and 15 arrivals.",
        "4": "Create a payment recovery link for $299 failed payment for reservation RES123.",
        "5": "Run a comprehensive test: check availability, get flight signals, and suggest optimal pricing."
    }

    if choice in workflows:
        prompt = workflows[choice]
        print(f"\n📋 Running: {prompt}\n")
        print("-"*60)

        try:
            # Run the agent
            result = test_agent.run(prompt)
            print("\n✅ Result:")
            print(result)
        except Exception as e:
            print(f"\n❌ Error: {e}")
    else:
        print("Invalid choice")

def test_tools_directly():
    """Test tools directly without agents"""
    print("\n" + "="*60)
    print("Testing HotelPilot Tools Directly")
    print("="*60)

    # Test PMS tool
    print("\n1. Testing PMS Tool - Room Availability:")
    result = pms_tools.get_room_availability(
        check_in="2024-12-20",
        check_out="2024-12-22",
        property_id="prop_001"
    )
    print(f"   Available rooms: {result['rooms']}")

    # Test Flight tool
    print("\n2. Testing Flight Tool - Airport Signals:")
    result = flight_tools.get_flight_arrivals(
        airport_code="DCA",
        date="2024-12-20"
    )
    print(f"   Total flights: {result['total_flights']}, Total seats: {result['total_seats']}")

    # Test Payment tool
    print("\n3. Testing Payment Tool - Create Payment Link:")
    result = payment_tools.create_payment_link(
        amount=299.00,
        reservation_id="RES123",
        guest_email="test@example.com"
    )
    print(f"   Payment link: {result['url']}")

    # Test Housekeeping tool
    print("\n4. Testing Housekeeping Tool - Daily Plan:")
    result = housekeeping_tools.get_daily_housekeeping_plan(
        date="2024-12-19"
    )
    print(f"   Total tasks: {result['total_tasks']}, Staff assigned: {result['total_staff']}")

    # Test Messaging tool sentiment
    print("\n5. Testing Messaging Tool - Sentiment Analysis:")
    result = messaging_tools.analyze_sentiment(
        text="The room was absolutely terrible and the service was awful!"
    )
    print(f"   Sentiment: {result['sentiment']}, Score: {result['score']}")

def main():
    print("""
    ╔═══════════════════════════════════════╗
    ║     HotelPilot System Test Runner     ║
    ║   Multi-Agent Hotel Operations AI     ║
    ╚═══════════════════════════════════════╝
    """)

    print("\nSelect test mode:")
    print("1. Test with AI Agent (uses Gemini)")
    print("2. Test tools directly (no AI needed)")
    print("0. Exit")

    choice = input("\nEnter choice (0-2): ")

    if choice == "1":
        test_basic_agent()
    elif choice == "2":
        test_tools_directly()
    elif choice == "0":
        print("Exiting...")
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()