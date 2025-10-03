"""
HotelPilot ADK Test - Working with Async Generators
====================================================
This test properly handles ADK's async generator pattern.
"""

import os
import asyncio
from google.adk.agents import LlmAgent
from dotenv import load_dotenv

# Load environment variables
load_dotenv('hotelpilot/.env')

GOOGLE_AI_API_KEY = os.getenv('GOOGLE_AI_API_KEY')
MODEL = os.getenv('PRIMARY_MODEL', 'gemini-2.5-flash')

async def test_adk_agent():
    """Test ADK agent with proper async generator handling"""

    print("""
    ╔═══════════════════════════════════════╗
    ║     HotelPilot ADK Test               ║
    ║   Multi-Agent Hotel Operations AI     ║
    ╚═══════════════════════════════════════╝
    """)

    if not GOOGLE_AI_API_KEY:
        print("❌ ERROR: No API key found in .env file")
        return

    print(f"✅ API Key configured")
    print(f"✅ Using model: {MODEL}\n")

    # Create the Ops Copilot agent
    ops_copilot = LlmAgent(
        name="ops_copilot",
        model=MODEL,
        description="Hotel operations supervisor",
        instruction="""You are the Ops Copilot for Arlington Hotel, Virginia.

        Current situation:
        - Base rate: $129 standard
        - Current occupancy: 75%
        - Rate caps: weekday 10%, weekend 12%

        When analyzing pricing, provide clear recommendations."""
    )

    # Test prompt
    pricing_request = """
    Analyze demand for Friday, December 20:
    - DCA airport: +13% capacity (1000 extra seats)
    - IAD airport: +8% capacity (1000 extra seats)
    - Current occupancy: 75%

    Recommend pricing adjustment.
    """

    print("📊 Testing Dynamic Pricing with ADK...")
    print("-" * 40)

    try:
        # run_async returns an async generator
        response_generator = ops_copilot.run_async(pricing_request)

        # Collect the full response
        full_response = ""
        async for chunk in response_generator:
            full_response += chunk
            # Optional: print chunks as they arrive for streaming effect
            # print(chunk, end="", flush=True)

        print("\n💡 Agent Response:")
        print(full_response)

        print("\n" + "=" * 60)
        print("✅ ADK Agent test successful!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure google-adk is installed: pip install google-adk")
        print("2. Check your API key in hotelpilot/.env")

async def test_multiple_agents():
    """Test multiple ADK agents working together"""

    print("\n" + "=" * 60)
    print("Testing Multiple Agents")
    print("=" * 60)

    # Create specialized agents
    demand_agent = LlmAgent(
        name="demand_manager",
        model=MODEL,
        description="Analyzes flight signals for pricing",
        instruction="""You analyze flight demand signals.
        Calculate demand lift index:
        - 70% weight on capacity changes
        - 30% weight on timing
        Be precise with percentages."""
    )

    guest_agent = LlmAgent(
        name="guest_lifecycle",
        model=MODEL,
        description="Manages guest communications",
        instruction="""You handle guest communications.
        Be warm and professional.
        Suggest upsells appropriately."""
    )

    # Test demand agent
    print("\n1. Testing Demand Agent:")
    demand_prompt = "Calculate demand lift for: DCA +1500 seats, IAD +800 seats"

    response = ""
    async for chunk in demand_agent.run_async(demand_prompt):
        response += chunk
    print(response[:200] + "..." if len(response) > 200 else response)

    # Test guest agent
    print("\n2. Testing Guest Agent:")
    guest_prompt = "Create welcome message for John Smith, arriving tomorrow, room 305"

    response = ""
    async for chunk in guest_agent.run_async(guest_prompt):
        response += chunk
    print(response[:200] + "..." if len(response) > 200 else response)

async def test_interactive():
    """Interactive test where user can input requests"""

    print("\n" + "=" * 60)
    print("Interactive ADK Agent Test")
    print("=" * 60)

    # Create the main agent
    agent = LlmAgent(
        name="hotel_assistant",
        model=MODEL,
        description="Hotel operations assistant",
        instruction="""You are a helpful hotel operations assistant.
        You can help with:
        - Pricing recommendations
        - Guest services
        - Housekeeping scheduling
        - Payment issues
        Be concise and professional."""
    )

    print("\nAvailable commands:")
    print("1. 'pricing' - Test pricing scenario")
    print("2. 'guest' - Test guest communication")
    print("3. 'housekeeping' - Test housekeeping plan")
    print("4. 'custom' - Enter your own request")
    print("5. 'quit' - Exit")

    while True:
        choice = input("\nEnter command: ").lower().strip()

        if choice == 'quit':
            break

        prompts = {
            'pricing': "Recommend pricing for tomorrow with 20% increased flight capacity",
            'guest': "Create checkout message for guest leaving today",
            'housekeeping': "Plan housekeeping for 10 checkouts and 15 arrivals",
        }

        if choice == 'custom':
            prompt = input("Enter your request: ")
        elif choice in prompts:
            prompt = prompts[choice]
        else:
            print("Invalid command")
            continue

        print(f"\n📝 Processing: {prompt[:50]}...")
        print("-" * 40)

        try:
            response = ""
            async for chunk in agent.run_async(prompt):
                response += chunk
            print(response)
        except Exception as e:
            print(f"Error: {e}")

async def main():
    """Main entry point"""

    print("Select test mode:")
    print("1. Basic ADK agent test")
    print("2. Multiple agents test")
    print("3. Interactive test")
    print("4. Run all tests")

    choice = input("\nEnter choice (1-4): ")

    if choice == '1':
        await test_adk_agent()
    elif choice == '2':
        await test_multiple_agents()
    elif choice == '3':
        await test_interactive()
    elif choice == '4':
        await test_adk_agent()
        await test_multiple_agents()
        await test_interactive()
    else:
        print("Invalid choice")

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())