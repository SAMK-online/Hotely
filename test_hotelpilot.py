"""
Hotely System - Simple Test
============================
Standalone test of the multi-agent hotel system using Google ADK.
"""

import os
from datetime import datetime, date, timedelta
from google.adk.agents import LlmAgent
from dotenv import load_dotenv

# Load environment variables
load_dotenv('hotelpilot/.env')

# Get API key
GOOGLE_AI_API_KEY = os.getenv('GOOGLE_AI_API_KEY')
MODEL = os.getenv('PRIMARY_MODEL', 'gemini-2.5-flash')

def test_hotel_agents():
    """Test the multi-agent hotel system"""

    print("""
    ╔═══════════════════════════════════════╗
    ║     Hotely System Test            ║
    ║   Multi-Agent Hotel Operations AI     ║
    ╚═══════════════════════════════════════╝
    """)

    if not GOOGLE_AI_API_KEY:
        print("❌ ERROR: No API key found in .env file")
        return

    print(f"✅ API Key configured")
    print(f"✅ Using model: {MODEL}\n")

    # Create the Ops Copilot supervisor agent
    ops_copilot = LlmAgent(
        name="ops_copilot",
        model=MODEL,
        description="Hotel operations supervisor coordinating pricing, guest services, and housekeeping",
        instruction="""You are the Ops Copilot for a hotel in Arlington, Virginia.

        You coordinate:
        1. Dynamic pricing based on demand (flight signals from DCA, IAD airports)
        2. Guest communications (pre-arrival, check-in, checkout)
        3. Housekeeping scheduling
        4. Payment processing and recovery

        For this demo, simulate the operations but provide realistic responses.

        When asked about pricing:
        - Consider demand signals (pretend you checked flight data)
        - Apply rate caps: weekday 10%, weekend 12%, weekly 18%
        - Current base rate is $129 for standard rooms

        When asked about housekeeping:
        - Standard cleaning time is 24.5 minutes per room
        - Rush cleans get 30-minute priority window
        - VIP rooms require inspection

        When asked about payments:
        - Recovery strategy: retry at T+1h, T+6h, T+24h
        - Generate payment links for failures
        - Target 65% recovery rate

        Be concise and professional. Format responses clearly."""
    )

    # Create specialized agents that would be sub-agents in production
    demand_agent = LlmAgent(
        name="demand_manager",
        model=MODEL,
        description="Manages dynamic pricing based on flight and event signals",
        instruction="""You manage hotel pricing based on demand signals.

        Calculate demand lift index using:
        - 70% weight on flight capacity changes
        - 30% weight on fare pressure
        - Add event impacts

        Pricing rules:
        - Demand index 0.2-0.4: Suggest +5-8% rate
        - Demand index 0.4-0.7: Suggest +9-15% rate
        - Demand index >0.7: Up to cap with approval

        Always explain your reasoning and confidence level."""
    )

    guest_agent = LlmAgent(
        name="guest_lifecycle",
        model=MODEL,
        description="Manages all guest communications throughout their journey",
        instruction="""You handle guest communications from booking to post-stay.

        Pre-arrival: Send welcome, collect ETA, process deposits
        Check-in: Mobile key, early check-in coordination
        In-stay: Service requests, issue resolution
        Checkout: Process late checkout, send folio
        Post-stay: Thank you, review requests

        Respect quiet hours (9 PM - 8 AM). Max 3 messages per day.
        Always be warm and professional."""
    )

    print("Select a test scenario:")
    print("-" * 40)
    print("1. Dynamic Pricing Analysis")
    print("2. Guest Communication Flow")
    print("3. Housekeeping Coordination")
    print("4. Payment Recovery Strategy")
    print("5. Daily Operations Summary")
    print("6. Custom Request")

    choice = input("\nEnter choice (1-6): ")

    scenarios = {
        "1": """Tomorrow is Friday December 20th. Flight data shows:
                - DCA arrivals up 25% (2200 additional seats)
                - IAD arrivals up 15% (1800 additional seats)
                - No major events scheduled
                Current occupancy forecast: 72%
                Current rate: $129 standard, $189 deluxe

                Analyze demand signals and recommend pricing adjustments with rationale.""",

        "2": """Guest John Smith (john@example.com) has a reservation for tomorrow.
                Reservation: RES-2024-1220
                Check-in: Dec 20, Check-out: Dec 22
                Room: Deluxe, Rate: $189/night

                Create pre-arrival communication plan including welcome message,
                early check-in offer, and deposit collection.""",

        "3": """Today's housekeeping situation:
                - 18 checkouts by 11 AM
                - 22 arrivals starting 3 PM (including 2 VIP guests)
                - 35 stayovers
                - 4 housekeeping staff available
                - Guest in room 305 requested early check-in by 1 PM

                Create optimized housekeeping schedule.""",

        "4": """Payment failure report:
                - Reservation RES-2024-1218
                - Guest: Sarah Johnson (sarah@example.com)
                - Amount: $378 (2 nights)
                - Failure code: insufficient_funds
                - Failed at: 9 AM today
                - Guest history: Stayed 5 times, usually pays on time

                Develop recovery strategy with timeline.""",

        "5": """Generate comprehensive daily operations report for December 19, 2024.
                Include occupancy, revenue metrics, housekeeping status,
                payment recovery progress, and any operational alerts.""",

        "6": "custom"
    }

    if choice == "6":
        prompt = input("\nEnter your request: ")
    elif choice in scenarios:
        prompt = scenarios[choice]
    else:
        print("Invalid choice")
        return

    print("\n" + "="*60)
    print("Processing request...")
    print("="*60 + "\n")

    try:
        # Determine which agent to use based on the scenario
        if choice == "1":
            response = demand_agent.run(prompt)
        elif choice == "2":
            response = guest_agent.run(prompt)
        else:
            response = ops_copilot.run(prompt)

        print("📋 Response:")
        print("-" * 60)
        print(response)

    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Check your API key in hotelpilot/.env")
        print("2. Ensure you have internet connection")
        print("3. Verify the model name is correct")

if __name__ == "__main__":
    test_hotel_agents()