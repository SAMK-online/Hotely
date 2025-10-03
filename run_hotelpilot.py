#!/usr/bin/env python3
"""
Hotely - Simple Working Demo
============================
A working demo of the Hotely multi-agent system.
"""

import os
import asyncio
from datetime import datetime, date
from dotenv import load_dotenv

# Load environment
load_dotenv('hotelpilot/.env')

# Set up environment
os.environ['GOOGLE_AI_API_KEY'] = os.getenv('GOOGLE_AI_API_KEY', '')

def print_header():
    """Print the application header"""
    print("""
    ╔═══════════════════════════════════════╗
    ║         Hotely System             ║
    ║   Multi-Agent Hotel Operations AI     ║
    ╚═══════════════════════════════════════╝
    """)

async def test_with_adk():
    """Test using Google ADK agents"""
    try:
        from google.adk.agents import LlmAgent
        
        # Create a simple ops copilot agent
        ops_copilot = LlmAgent(
            name="ops_copilot",
            model="gemini-2.5-flash",
            description="Hotel operations supervisor",
            instruction="""You are the Ops Copilot for Arlington Suites, a 120-room hotel in Arlington, VA.

            You coordinate hotel operations including:
            1. Dynamic pricing based on demand signals
            2. Guest communications and service
            3. Housekeeping scheduling
            4. Payment processing and recovery

            For pricing decisions:
            - Current base rate: $129 for standard rooms
            - Rate caps: weekday 10%, weekend 12%, weekly 18%
            - Consider flight signals from DCA and IAD airports

            For housekeeping:
            - Standard clean time: 24.5 minutes per room
            - Rush cleans for early check-ins get priority
            - VIP rooms require inspection

            For payments:
            - Recovery strategy: retry at T+1h, T+6h, T+24h
            - Generate payment links for failures
            - Target 65% recovery rate

            Be professional, concise, and provide actionable recommendations."""
        )

        print("✅ Google ADK agent created successfully")
        return ops_copilot
        
    except Exception as e:
        print(f"❌ ADK Error: {e}")
        return None

def test_with_genai():
    """Test using Google GenerativeAI directly"""
    try:
        import google.generativeai as genai
        
        api_key = os.environ.get('GOOGLE_AI_API_KEY')
        if not api_key:
            print("❌ No API key found")
            return None
            
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        print("✅ Google GenerativeAI configured successfully")
        return model
        
    except Exception as e:
        print(f"❌ GenAI Error: {e}")
        return None

async def run_scenario(agent_or_model, scenario_num):
    """Run a specific scenario"""
    
    scenarios = {
        1: {
            "title": "Dynamic Pricing Analysis",
            "prompt": """Analyze this hotel pricing scenario:

            Arlington Suites (120 rooms)
            Current rate: $129 standard, $189 deluxe
            Date: Tomorrow (Friday, December 20, 2024)
            Current occupancy: 78%

            Flight data shows:
            - DCA airport: +18% capacity (1,200 extra seats)
            - IAD airport: +12% capacity (1,500 extra seats)
            - No major events scheduled

            Policy constraints:
            - Max weekday increase: 10%
            - Max weekend increase: 12%
            - Weekly net cap: 18%

            Provide pricing recommendations with rationale."""
        },
        
        2: {
            "title": "Guest Communication Flow",
            "prompt": """Handle this guest communication scenario:

            Guest: John Smith (john@example.com, +1-555-0123)
            Reservation: RES-2024-1220
            Check-in: December 20, Check-out: December 22
            Room: Deluxe King, Rate: $189/night
            Status: Confirmed, deposit pending

            Tasks:
            1. Create pre-arrival welcome message
            2. Offer early check-in (if available)
            3. Request deposit collection
            4. Provide check-in instructions

            Keep messages warm, professional, and under 160 characters each."""
        },
        
        3: {
            "title": "Housekeeping Coordination",
            "prompt": """Optimize today's housekeeping schedule:

            Situation:
            - 15 checkouts by 11 AM
            - 18 arrivals starting 3 PM (2 are VIP guests)
            - 32 stayovers (no cleaning needed)
            - 3 housekeeping staff available (8-hour shifts)
            - Guest in room 305 requested early check-in by 1 PM

            Constraints:
            - Standard clean: 24.5 minutes per room
            - VIP rooms require inspection (+10 minutes)
            - Rush clean for early check-in: 30-minute window

            Create optimized schedule with staff assignments."""
        },
        
        4: {
            "title": "Payment Recovery Strategy",
            "prompt": """Develop payment recovery plan:

            Failed Payment Details:
            - Reservation: RES-2024-1218
            - Guest: Sarah Johnson (sarah@example.com)
            - Amount: $378 (2 nights + taxes)
            - Failure code: insufficient_funds
            - Failed at: 9:15 AM today
            - Guest history: 4 previous stays, usually pays on time

            Recovery Strategy:
            - T+1 hour: Automated retry
            - T+6 hours: Retry with notification
            - T+24 hours: 3DS payment link
            - Target: 65% recovery rate

            Create timeline and communication plan."""
        },
        
        5: {
            "title": "Daily Operations Summary",
            "prompt": """Generate daily operations report for December 19, 2024:

            Occupancy Data:
            - Rooms sold: 95/120 (79.2%)
            - ADR: $142.50
            - RevPAR: $112.88
            - Arrivals: 22, Departures: 18

            Operations Status:
            - Housekeeping: 2 rooms pending, 1 maintenance issue
            - Failed payments: 3 totaling $847
            - Guest complaints: 1 (noise complaint, resolved)
            - Upsells: 4 late checkouts, 2 room upgrades

            Provide comprehensive summary with key metrics and action items."""
        }
    }
    
    if scenario_num not in scenarios:
        print("❌ Invalid scenario number")
        return
        
    scenario = scenarios[scenario_num]
    print(f"\n📋 {scenario['title']}")
    print("=" * 60)
    
    try:
        # Check if it's an ADK agent or GenAI model
        if hasattr(agent_or_model, 'run_async'):
            # ADK agent
            response = await agent_or_model.run_async(scenario['prompt'])
        elif hasattr(agent_or_model, 'generate_content'):
            # GenAI model
            response = agent_or_model.generate_content(scenario['prompt'])
            response = response.text
        else:
            print("❌ Unknown agent/model type")
            return

                print("\n💡 Response:")
                print("-" * 60)
                print(response)
        print("\n" + "=" * 60)

            except Exception as e:
        print(f"❌ Error running scenario: {e}")

async def main():
    """Main application"""
    print_header()
    
    # Check API key
    api_key = os.environ.get('GOOGLE_AI_API_KEY')
    if not api_key:
        print("❌ ERROR: GOOGLE_AI_API_KEY not found in environment")
        print("Please check your hotelpilot/.env file")
        return
        
    print(f"✅ API Key configured: {api_key[:10]}...")
    
    # Try to initialize agent/model
    print("\n🔄 Initializing Hotely system...")
    
    # First try ADK
    agent = await test_with_adk()
    
    # If ADK fails, try GenAI directly
    if agent is None:
        print("🔄 Falling back to Google GenerativeAI...")
        agent = test_with_genai()
        
    if agent is None:
        print("❌ Failed to initialize any AI system")
        return
    
    # Show menu
    print("\n📋 Select a scenario to demonstrate:")
    print("-" * 40)
    print("1. Dynamic Pricing Analysis")
    print("2. Guest Communication Flow")
    print("3. Housekeeping Coordination")
    print("4. Payment Recovery Strategy")
    print("5. Daily Operations Summary")
    print("0. Exit")
    
    while True:
        try:
            choice = input("\nEnter your choice (0-5): ").strip()
            
            if choice == "0":
                print("\n👋 Exiting Hotely...")
                break
            elif choice in ["1", "2", "3", "4", "5"]:
                await run_scenario(agent, int(choice))
        else:
                print("❌ Invalid choice. Please enter 0-5.")

    except KeyboardInterrupt:
            print("\n\n👋 Exiting Hotely...")
            break
    except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())