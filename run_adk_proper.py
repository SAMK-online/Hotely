#!/usr/bin/env python
"""
HotelPilot with ADK Runner
===========================
Proper way to run ADK agents using the Runner class.
"""

import os
import asyncio
from dotenv import load_dotenv
from google.adk import Runner
from google.adk.agents import LlmAgent

# Load environment
load_dotenv('hotelpilot/.env')
os.environ['GOOGLE_AI_API_KEY'] = os.getenv('GOOGLE_AI_API_KEY', '')

def create_ops_copilot():
    """Create the main Ops Copilot agent"""
    return LlmAgent(
        name="ops_copilot",
        model="gemini-2.0-flash-exp",
        description="Hotel operations supervisor for Arlington Hotel",
        instruction="""You are the Ops Copilot for Arlington Hotel, a 120-room property in Arlington, Virginia.

        HOTEL DETAILS:
        - 120 rooms: 40 standard ($129), 60 deluxe ($189), 20 suites ($299)
        - Current occupancy: 75% average
        - Location weights: DCA 60%, IAD 30%, BWI 10%

        PRICING RULES:
        - Weekday cap: +10%
        - Weekend cap: +12%
        - Weekly cap: +18%

        OPERATIONAL STANDARDS:
        - Quiet hours: 9 PM - 8 AM
        - Housekeeping: 24.5 min standard
        - Payment recovery: T+1h, T+6h, T+24h

        Provide concise, data-driven responses."""
    )

async def run_with_runner():
    """Run HotelPilot using ADK Runner"""

    print("""
    ╔═══════════════════════════════════════╗
    ║     HotelPilot with ADK Runner        ║
    ║   Multi-Agent Hotel Operations AI     ║
    ╚═══════════════════════════════════════╝
    """)

    if not os.environ.get('GOOGLE_AI_API_KEY'):
        print("❌ No API key found in hotelpilot/.env")
        return

    print("✅ API Key configured")

    try:
        # Create the agent
        agent = create_ops_copilot()
        print("✅ Agent created: ops_copilot")

        # Create runner with the agent
        runner = Runner(
            app_name="HotelPilot",
            agent=agent
        )
        print("✅ Runner initialized\n")

        # Test scenarios
        scenarios = [
            {
                "title": "Dynamic Pricing Analysis",
                "prompt": """Analyze pricing for Friday, December 20:
                - DCA airport: +13% capacity (1000 extra seats)
                - IAD airport: +8% capacity (800 extra seats)
                - Current occupancy: 75%
                Calculate demand lift and recommend pricing adjustments."""
            },
            {
                "title": "Guest Communication",
                "prompt": """Create a brief welcome message for:
                Guest: John Smith
                Check-in: Tomorrow 3 PM
                Room: Deluxe #305 ($189/night)
                Keep it warm but professional."""
            }
        ]

        for i, scenario in enumerate(scenarios, 1):
            print("=" * 60)
            print(f"DEMO {i}: {scenario['title']}")
            print("=" * 60)
            print(f"📝 Request: {scenario['prompt'][:100]}...")
            print("-" * 40)

            # Run the agent with Runner
            response = ""
            async for event in runner.run(scenario['prompt']):
                # Extract text from the event
                if hasattr(event, 'text'):
                    response += event.text
                elif hasattr(event, 'content'):
                    response += str(event.content)
                else:
                    response += str(event)

            print("\n💡 Response:")
            print(response[:500] + "..." if len(response) > 500 else response)
            print()

        print("=" * 60)
        print("✅ ALL DEMOS COMPLETE")
        print("=" * 60)
        print("\nHotelPilot is working with Google ADK!")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_with_runner())