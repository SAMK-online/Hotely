#!/usr/bin/env python
"""
HotelPilot ADK Demo - Complete Working Version
===============================================
Run the HotelPilot multi-agent system with Google ADK.
"""

import os
import asyncio
from dotenv import load_dotenv
from google.adk import Runner
from google.adk.agents import LlmAgent
from google.adk.sessions import InMemorySessionService

# Load environment
load_dotenv('hotelpilot/.env')
os.environ['GOOGLE_AI_API_KEY'] = os.getenv('GOOGLE_AI_API_KEY', '')

def create_hotel_agents():
    """Create all HotelPilot agents"""

    agents = {}

    # Ops Copilot - Main Supervisor
    agents['ops_copilot'] = LlmAgent(
        name="ops_copilot",
        model="gemini-2.0-flash-exp",
        description="Hotel operations supervisor",
        instruction="""You are the Ops Copilot for Arlington Hotel, Virginia.

        Hotel: 120 rooms, 75% average occupancy
        Rates: $129 standard, $189 deluxe, $299 suite
        Rate caps: weekday 10%, weekend 12%

        Analyze situations and provide recommendations."""
    )

    # Demand Manager
    agents['demand_manager'] = LlmAgent(
        name="demand_manager",
        model="gemini-2.0-flash-exp",
        description="Pricing analyst",
        instruction="""You analyze flight signals for pricing.

        Weights: DCA 60%, IAD 30%, BWI 10%
        Calculate demand lift and recommend rates."""
    )

    # Guest Lifecycle
    agents['guest_lifecycle'] = LlmAgent(
        name="guest_lifecycle",
        model="gemini-2.0-flash-exp",
        description="Guest communications manager",
        instruction="""You manage guest communications.

        Be warm, professional, and helpful.
        Keep messages concise."""
    )

    return agents

async def run_demo():
    """Run the HotelPilot demo"""

    print("""
    ╔═══════════════════════════════════════╗
    ║     HotelPilot ADK Demo               ║
    ║   Multi-Agent Hotel Operations AI     ║
    ╚═══════════════════════════════════════╝
    """)

    if not os.environ.get('GOOGLE_AI_API_KEY'):
        print("❌ No API key found")
        return

    print("✅ API Key configured")

    try:
        # Create agents
        agents = create_hotel_agents()
        print(f"✅ Created {len(agents)} agents")

        # Create session service
        session_service = InMemorySessionService()
        print("✅ Session service initialized")

        # Create runner with the main agent
        runner = Runner(
            app_name="HotelPilot",
            agent=agents['ops_copilot'],
            session_service=session_service
        )
        print("✅ Runner initialized\n")

        # Test scenario
        print("=" * 60)
        print("DEMO: Dynamic Pricing Analysis")
        print("=" * 60)

        prompt = """Analyze pricing for Friday:
        - DCA: +13% capacity
        - IAD: +8% capacity
        - Occupancy: 75%
        Recommend pricing."""

        print("📊 Request:", prompt)
        print("-" * 40)

        # Run and collect response
        response = ""
        async for event in runner.run(prompt):
            if hasattr(event, 'text'):
                response += event.text
            elif hasattr(event, 'content'):
                response += str(event.content)

        print("\n💡 Response:")
        print(response[:500] + "..." if len(response) > 500 else response)

        print("\n" + "=" * 60)
        print("✅ HotelPilot ADK Demo Complete!")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_demo())