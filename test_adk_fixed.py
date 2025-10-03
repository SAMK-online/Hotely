"""
HotelPilot ADK Test - Fixed Version
====================================
Properly configured ADK test with correct model setup.
"""

import os
import asyncio
from google.adk.agents import LlmAgent
from google.adk import RunConfig
from dotenv import load_dotenv

# Load environment variables
load_dotenv('hotelpilot/.env')

# Set API key in environment
os.environ['GOOGLE_AI_API_KEY'] = os.getenv('GOOGLE_AI_API_KEY', '')

async def test_adk():
    """Test ADK with proper configuration"""

    print("""
    ╔═══════════════════════════════════════╗
    ║     HotelPilot ADK Test               ║
    ║   Multi-Agent Hotel Operations AI     ║
    ╚═══════════════════════════════════════╝
    """)

    api_key = os.environ.get('GOOGLE_AI_API_KEY')
    if not api_key:
        print("❌ ERROR: No API key found")
        return

    print(f"✅ API Key configured: {api_key[:10]}...")

    try:
        # Create RunConfig with the model
        config = RunConfig(
            model="gemini-2.0-flash-exp",  # Use the model from config
        )

        # Create the agent
        agent = LlmAgent(
            name="ops_copilot",
            description="Hotel operations supervisor",
            instruction="""You are the Ops Copilot for Arlington Hotel.

            Current rates: $129 standard, $189 deluxe
            Rate caps: weekday 10%, weekend 12%
            Current occupancy: 75%

            Analyze demand and provide pricing recommendations.""",
            config=config
        )

        # Test prompt
        prompt = """Analyze for Friday Dec 20:
        - DCA airport: +13% capacity (1000 extra seats)
        - IAD airport: +8% capacity
        - Current occupancy: 75%
        Recommend pricing."""

        print("\n📊 Testing Dynamic Pricing...")
        print("-" * 40)

        # Run the agent
        response = ""
        async for chunk in agent.run_async(prompt):
            response += chunk

        print("\n💡 Response:")
        print(response)

        print("\n" + "=" * 60)
        print("✅ ADK test successful!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_adk())