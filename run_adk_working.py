#!/usr/bin/env python
"""
HotelPilot - Working ADK Demo
==============================
Properly handles ADK's async generator pattern.
"""

import os
import asyncio
from dotenv import load_dotenv
from google.adk.agents import LlmAgent

# Load environment
load_dotenv('hotelpilot/.env')
os.environ['GOOGLE_AI_API_KEY'] = os.getenv('GOOGLE_AI_API_KEY', '')

async def test_adk_agent():
    """Test ADK agent with proper async handling"""

    print("""
    ╔═══════════════════════════════════════╗
    ║     HotelPilot ADK Working Demo       ║
    ║   Multi-Agent Hotel Operations AI     ║
    ╚═══════════════════════════════════════╝
    """)

    api_key = os.environ.get('GOOGLE_AI_API_KEY')
    if not api_key:
        print("❌ No API key found")
        return

    print(f"✅ API Key configured: {api_key[:10]}...")

    try:
        # Create agent
        agent = LlmAgent(
            name="ops_copilot",
            model="gemini-2.0-flash-exp",
            description="Hotel operations supervisor",
            instruction="""You are the Ops Copilot for Arlington Hotel.

            Hotel: 120 rooms, $129 standard, $189 deluxe
            Rate caps: weekday 10%, weekend 12%
            Current occupancy: 75%

            Provide concise, actionable recommendations."""
        )

        print("✅ Agent created successfully\n")

        # Test scenario
        prompt = """Analyze pricing for Friday:
        - DCA airport: +13% capacity (1000 extra seats)
        - IAD airport: +8% capacity (800 extra seats)
        - Current occupancy: 75%

        Recommend pricing adjustment."""

        print("=" * 60)
        print("📊 Dynamic Pricing Analysis")
        print("=" * 60)
        print("Request:", prompt[:100] + "...")
        print("-" * 40)

        # THIS IS THE FIX: Properly iterate over async generator
        response = ""
        async for chunk in agent.run_async(prompt):
            # Each chunk is the response chunk from the agent
            response += str(chunk)

        print("\n💡 Response:")
        print(response)

        print("\n" + "=" * 60)
        print("✅ ADK Test Successful!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run the async test"""
    try:
        asyncio.run(test_adk_agent())
    except KeyboardInterrupt:
        print("\n\nExiting...")

if __name__ == "__main__":
    main()