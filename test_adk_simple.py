"""
HotelPilot ADK Test - Simple Synchronous Version
================================================
Easier way to test ADK agents without async complexity.
"""

import os
import asyncio
from google.adk.agents import LlmAgent
from dotenv import load_dotenv

# Load environment variables
load_dotenv('hotelpilot/.env')

GOOGLE_AI_API_KEY = os.getenv('GOOGLE_AI_API_KEY')
MODEL = os.getenv('PRIMARY_MODEL', 'gemini-2.5-flash')

def run_agent_sync(agent, prompt):
    """Helper function to run async agent synchronously"""
    async def _run():
        response = ""
        async for chunk in agent.run_async(prompt):
            response += chunk
        return response

    return asyncio.run(_run())

def test_hotel_agent():
    """Simple test of HotelPilot agent"""

    print("""
    ╔═══════════════════════════════════════╗
    ║     HotelPilot Simple ADK Test        ║
    ║   Multi-Agent Hotel Operations AI     ║
    ╚═══════════════════════════════════════╝
    """)

    if not GOOGLE_AI_API_KEY:
        print("❌ ERROR: No API key found in .env file")
        return

    print(f"✅ API Key configured")
    print(f"✅ Using model: {MODEL}")
    print("-" * 60)

    # Create the Ops Copilot agent
    ops_copilot = LlmAgent(
        name="ops_copilot",
        model=MODEL,
        description="Hotel operations supervisor for Arlington Hotel",
        instruction="""You are the Ops Copilot for Arlington Hotel, a 120-room hotel in Arlington, Virginia.

        Key information:
        - Base rates: $129 standard, $189 deluxe, $299 suite
        - Current occupancy: 75% (90 rooms occupied, 30 available)
        - Location: Near DCA (60% weight) and IAD (30% weight) airports
        - Rate caps: weekday +10%, weekend +12%, weekly +18%

        When analyzing:
        1. Calculate demand lift from flight signals
        2. Apply appropriate rate caps
        3. Consider day of week
        4. Provide clear recommendations with reasoning

        Be concise and data-driven."""
    )

    # Menu-driven test
    while True:
        print("\n" + "=" * 60)
        print("Select a scenario to test:")
        print("-" * 60)
        print("1. 📊 Dynamic Pricing (Flight Signals)")
        print("2. ✉️  Guest Communication")
        print("3. 🧹 Housekeeping Schedule")
        print("4. 💳 Payment Recovery")
        print("5. 📈 Daily Summary")
        print("6. 🎯 Custom Request")
        print("0. Exit")
        print("=" * 60)

        choice = input("\nEnter choice (0-6): ")

        if choice == '0':
            print("\nExiting HotelPilot...")
            break

        scenarios = {
            '1': """Analyze pricing for tomorrow (Friday, Dec 20):
                - DCA: 8,500 arrivals (baseline 7,500) = +13% capacity
                - IAD: 13,000 arrivals (baseline 12,000) = +8% capacity
                - Current occupancy: 75%
                - Weather: Clear
                Calculate demand lift and recommend rates for all room types.""",

            '2': """Create pre-arrival message for:
                Guest: John Smith
                Reservation: RES-2024-1220
                Check-in: Tomorrow 3 PM
                Room: Deluxe #305 ($189/night)
                Include: Welcome, deposit request ($200), early check-in offer ($25)""",

            '3': """Create housekeeping plan for today:
                - 15 checkouts by 11 AM (rooms 201-215)
                - 20 arrivals from 3 PM (2 VIP in suites 501, 502)
                - 35 stayovers
                - Staff: Maria, John, Sarah (8-4), Carlos (12-6)
                - Special: Room 305 needs early check-in by 1 PM""",

            '4': """Handle payment recovery:
                - RES-2024-1218: $378 failed (insufficient_funds)
                - Guest: Sarah Johnson (VIP, 5 previous stays)
                - Failed at: 9 AM today
                Create recovery strategy with timeline and message.""",

            '5': """Generate operations summary for today:
                - Occupancy: 75% (90/120 rooms)
                - ADR: $142 (target: $135)
                - RevPAR: $106.50
                - Arrivals: 22 (2 VIP)
                - Departures: 18
                - Issues: Room 412 AC repair needed
                Create executive summary with highlights and action items.""",

            '6': None  # Custom request
        }

        if choice == '6':
            prompt = input("\nEnter your custom request:\n> ")
        elif choice in scenarios:
            prompt = scenarios[choice]
            print(f"\n📝 Scenario: {['', 'Dynamic Pricing', 'Guest Communication', 'Housekeeping', 'Payment Recovery', 'Daily Summary', 'Custom'][int(choice)]}")
        else:
            print("Invalid choice. Please try again.")
            continue

        print("\n⏳ Processing request...")
        print("-" * 60)

        try:
            # Run the agent and get response
            response = run_agent_sync(ops_copilot, prompt)

            print("\n💡 Agent Response:")
            print("-" * 60)
            print(response)

        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("\nPossible issues:")
            print("1. Check your API key in hotelpilot/.env")
            print("2. Ensure google-adk is installed correctly")
            print("3. Check internet connection")

def quick_test():
    """Quick test without interaction"""

    if not GOOGLE_AI_API_KEY:
        print("❌ No API key found")
        return False

    print("\n🚀 Running quick ADK test...")

    agent = LlmAgent(
        name="test_agent",
        model=MODEL,
        description="Test agent",
        instruction="You are a helpful assistant. Be very brief."
    )

    try:
        response = run_agent_sync(agent, "Say 'HotelPilot ADK is working!' and nothing else.")
        print(f"✅ Response: {response}")
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

if __name__ == "__main__":
    # Run quick test first
    if quick_test():
        print("\n✅ ADK is working! Starting interactive test...\n")
        test_hotel_agent()
    else:
        print("\n⚠️  Please fix the issues above before continuing.")