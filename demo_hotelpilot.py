#!/usr/bin/env python3
"""
Hotely - Automated Demo
=======================
Runs all scenarios automatically without user input.
"""

import os
import asyncio
from datetime import datetime
from dotenv import load_dotenv

# Load environment
load_dotenv('hotelpilot/.env')
os.environ['GOOGLE_AI_API_KEY'] = os.getenv('GOOGLE_AI_API_KEY', '')

def print_header():
    """Print the application header"""
    print("""
    ╔═══════════════════════════════════════╗
    ║         Hotely System             ║
    ║   Multi-Agent Hotel Operations AI     ║
    ║            Automated Demo             ║
    ╚═══════════════════════════════════════╝
    """)

def get_scenarios():
    """Get all demo scenarios"""
    return {
        1: {
            "title": "🏷️  Dynamic Pricing Analysis",
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

Provide pricing recommendations with rationale. Be concise."""
        },
        
        2: {
            "title": "💬 Guest Communication Flow",
            "prompt": """Create guest communication for this scenario:

Guest: John Smith (john@example.com)
Reservation: RES-2024-1220
Check-in: December 20, Check-out: December 22
Room: Deluxe King, Rate: $189/night

Create:
1. Pre-arrival welcome message
2. Early check-in offer
3. Deposit collection request

Keep messages professional and concise."""
        },
        
        3: {
            "title": "🧹 Housekeeping Coordination",
            "prompt": """Optimize today's housekeeping schedule:

- 15 checkouts by 11 AM
- 18 arrivals starting 3 PM (2 VIP guests)
- 32 stayovers
- 3 housekeeping staff available
- Room 305 needs early check-in by 1 PM

Standard clean: 24.5 minutes, VIP rooms +10 minutes
Create optimized schedule with staff assignments."""
        },
        
        4: {
            "title": "💳 Payment Recovery Strategy",
            "prompt": """Develop payment recovery plan:

Failed Payment:
- Guest: Sarah Johnson
- Amount: $378
- Failure: insufficient_funds
- Time: 9:15 AM today
- History: 4 previous stays, reliable payer

Create recovery timeline and communication strategy."""
        }
    }

async def run_scenario_adk(agent, scenario):
    """Run scenario with ADK agent"""
    try:
        # ADK run_async returns an async generator, not awaitable
        response = ""
        async for chunk in agent.run_async(scenario['prompt']):
            response += str(chunk)
        return response
    except Exception as e:
        return f"ADK Error: {e}"

def run_scenario_genai(model, scenario):
    """Run scenario with GenAI model"""
    try:
        response = model.generate_content(scenario['prompt'])
        return response.text
    except Exception as e:
        return f"GenAI Error: {e}"

async def test_adk():
    """Test ADK implementation"""
    try:
        from google.adk.agents import LlmAgent
        
        agent = LlmAgent(
            name="ops_copilot",
            model="gemini-2.5-flash",
            description="Hotel operations supervisor",
            instruction="""You are the Ops Copilot for Arlington Suites hotel.
            Provide concise, professional responses for hotel operations including
            pricing, guest services, housekeeping, and payments."""
        )
        
        print("✅ Google ADK initialized successfully")
        return agent, "adk"
        
    except Exception as e:
        print(f"⚠️  ADK not available: {e}")
        return None, None

def test_genai():
    """Test GenAI implementation"""
    try:
        import google.generativeai as genai
        
        api_key = os.environ.get('GOOGLE_AI_API_KEY')
        if not api_key:
            return None, None
            
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        print("✅ Google GenerativeAI initialized successfully")
        return model, "genai"
        
    except Exception as e:
        print(f"❌ GenAI Error: {e}")
        return None, None

async def main():
    """Main demo function"""
    print_header()
    
    # Check API key
    api_key = os.environ.get('GOOGLE_AI_API_KEY')
    if not api_key:
        print("❌ ERROR: GOOGLE_AI_API_KEY not found")
        print("Please check your hotelpilot/.env file")
        return
        
    print(f"✅ API Key configured: {api_key[:10]}...")
    
    # Try to initialize AI system
    print("\n🔄 Initializing Hotely AI system...")
    
    # Skip ADK due to InvocationContext requirement, use GenAI directly
    print("🔄 Using Google GenerativeAI for demo...")
    agent, agent_type = test_genai()
        
    if agent is None:
        print("❌ Failed to initialize AI system")
        return
    
    print(f"✅ Using {agent_type.upper()} for AI processing")
    
    # Run all scenarios
    scenarios = get_scenarios()
    
    print(f"\n🚀 Running {len(scenarios)} Hotely scenarios...\n")
    
    for i, scenario in scenarios.items():
        print(f"{scenario['title']}")
        print("=" * 60)
        
        try:
            if agent_type == "adk":
                response = await run_scenario_adk(agent, scenario)
            else:
                response = run_scenario_genai(agent, scenario)
                
            print("\n💡 AI Response:")
            print("-" * 40)
            print(response)
            print("\n" + "=" * 60 + "\n")
            
            # Small delay between scenarios
            await asyncio.sleep(1)
            
        except Exception as e:
            print(f"❌ Error in scenario {i}: {e}\n")
    
    print("🎉 Hotely demo completed successfully!")
    print("\nThe system demonstrated:")
    print("• Dynamic pricing based on flight demand")
    print("• Guest communication workflows")
    print("• Housekeeping optimization")
    print("• Payment recovery strategies")
    print("\n✨ Hotely is ready for hotel operations!")

if __name__ == "__main__":
    asyncio.run(main())