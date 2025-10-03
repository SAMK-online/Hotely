"""
HotelPilot Demo - Automated Test
=================================
Demonstrates the multi-agent hotel system capabilities.
"""

import os
import asyncio
from google.adk.agents import LlmAgent
from dotenv import load_dotenv

# Load environment variables
load_dotenv('hotelpilot/.env')

GOOGLE_AI_API_KEY = os.getenv('GOOGLE_AI_API_KEY')
MODEL = os.getenv('PRIMARY_MODEL', 'gemini-2.5-flash')

async def run_demo():
    """Run automated demo of HotelPilot system"""

    print("""
    ╔═══════════════════════════════════════╗
    ║     HotelPilot System Demo            ║
    ║   Multi-Agent Hotel Operations AI     ║
    ╚═══════════════════════════════════════╝
    """)

    if not GOOGLE_AI_API_KEY:
        print("❌ ERROR: No API key found in .env file")
        return

    print(f"✅ API Key configured")
    print(f"✅ Using model: {MODEL}")
    print(f"✅ Starting automated demo...\n")

    # Create the main Ops Copilot agent
    ops_copilot = LlmAgent(
        name="ops_copilot",
        model=MODEL,
        description="Hotel operations supervisor coordinating all aspects of hotel management",
        instruction="""You are the Ops Copilot for Arlington Suites, a 120-room hotel in Arlington, Virginia.

        You coordinate:
        1. Dynamic pricing based on flight signals from DCA and IAD
        2. Guest communications throughout their journey
        3. Housekeeping and maintenance scheduling
        4. Payment processing and recovery
        5. Daily operations reporting

        Current situation:
        - Base rate: $129 standard, $189 deluxe, $299 suite
        - Current occupancy: 75%
        - 4 housekeeping staff on duty
        - Location weights: DCA 60%, IAD 30%, BWI 10%

        Apply these rules:
        - Rate caps: weekday 10%, weekend 12%, weekly 18%
        - Quiet hours: 9 PM - 8 AM
        - Housekeeping: 24.5 min average, 30 min rush
        - Payment recovery: T+1h, T+6h, T+24h

        Be concise and professional. Use clear formatting."""
    )

    # Demo 1: Dynamic Pricing
    print("="*60)
    print("DEMO 1: Dynamic Pricing Analysis")
    print("="*60)

    pricing_request = """
    Analyze demand and recommend pricing for tomorrow (Friday, Dec 20):

    Flight data received:
    - DCA: 8,500 seats arriving (baseline: 7,500) = +13% capacity
    - IAD: 13,000 seats arriving (baseline: 12,000) = +8% capacity
    - No major events scheduled
    - Weather: Clear
    - Current occupancy: 75%
    - Forecast occupancy without changes: 82%

    Calculate demand lift index and recommend rate adjustments for all room types.
    Show your calculations and confidence level.
    """

    print("\n📊 Request: Analyzing flight demand signals...")
    response = await ops_copilot.run_async(pricing_request)
    print("\n💡 Response:")
    print("-"*40)
    print(response)

    # Demo 2: Guest Communication
    print("\n" + "="*60)
    print("DEMO 2: Guest Lifecycle Management")
    print("="*60)

    guest_request = """
    Create a pre-arrival communication plan for:

    Guest: John Smith
    Email: john.smith@example.com
    Phone: +1-703-555-0123
    Reservation: RES-2024-1220
    Check-in: Tomorrow (Dec 20, 3 PM)
    Check-out: Dec 22 (11 AM)
    Room: Deluxe room #305
    Rate: $189/night
    Balance due: $378 + taxes

    Tasks needed:
    1. Send welcome message
    2. Collect $200 deposit
    3. Offer early check-in ($25)
    4. Share parking info ($20/night)

    Draft the message and outline the communication timeline.
    """

    print("\n✉️ Request: Managing guest pre-arrival...")
    response = await ops_copilot.run_async(guest_request)
    print("\n💡 Response:")
    print("-"*40)
    print(response)

    # Demo 3: Housekeeping
    print("\n" + "="*60)
    print("DEMO 3: Housekeeping Coordination")
    print("="*60)

    housekeeping_request = """
    Create today's housekeeping plan:

    Rooms status:
    - 15 checkouts by 11 AM (rooms: 201-215)
    - 20 arrivals from 3 PM (including 2 VIP in suites 501, 502)
    - 35 stayovers (prefer afternoon cleaning)
    - Room 305: Early check-in requested for 1 PM

    Staff available:
    - Maria: Full shift (8 AM - 4 PM)
    - John: Full shift (8 AM - 4 PM)
    - Sarah: Full shift (9 AM - 5 PM)
    - Carlos: Part-time (12 PM - 6 PM)

    Create optimized task assignments and timeline.
    Flag any potential issues.
    """

    print("\n🧹 Request: Optimizing housekeeping schedule...")
    response = await ops_copilot.run_async(housekeeping_request)
    print("\n💡 Response:")
    print("-"*40)
    print(response)

    # Demo 4: Revenue Recovery
    print("\n" + "="*60)
    print("DEMO 4: Payment Recovery Strategy")
    print("="*60)

    payment_request = """
    Handle failed payment recovery:

    Failed payments this morning:
    1. RES-2024-1218: $378, insufficient_funds, Guest: Sarah Johnson (VIP, 5 previous stays)
    2. RES-2024-1219: $129, card_declined, Guest: Mike Wilson (first time)
    3. RES-2024-1217: $567, expired_card, Guest: Group booking (10 rooms)

    Total at risk: $1,074

    For each case:
    - Recommend recovery strategy
    - Set retry schedule
    - Draft communication
    - Estimate recovery probability
    """

    print("\n💳 Request: Creating payment recovery plan...")
    response = await ops_copilot.run_async(payment_request)
    print("\n💡 Response:")
    print("-"*40)
    print(response)

    # Demo 5: Daily Summary
    print("\n" + "="*60)
    print("DEMO 5: Daily Operations Summary")
    print("="*60)

    summary_request = """
    Generate executive summary for today (Dec 19, 2024):

    Key metrics:
    - Occupancy: 75% (90 rooms)
    - ADR: $142 (target: $135)
    - RevPAR: $106.50
    - Arrivals: 22 (2 VIP)
    - Departures: 18
    - Housekeeping: 95% on-time
    - Payments: $2,850 recovered from $3,200 failed
    - Guest satisfaction: 4.6/5 (12 reviews)

    Issues:
    - Maintenance: Room 412 AC repair needed
    - Complaint: Room 308 noise issue (resolved)
    - Staff: 1 housekeeper called out sick

    Create concise summary with highlights, concerns, and recommendations.
    """

    print("\n📈 Request: Generating daily operations report...")
    response = await ops_copilot.run_async(summary_request)
    print("\n💡 Response:")
    print("-"*40)
    print(response)

    print("\n" + "="*60)
    print("✅ DEMO COMPLETE")
    print("="*60)
    print("\nHotelPilot has demonstrated:")
    print("• Dynamic pricing with flight demand analysis")
    print("• Guest lifecycle communication management")
    print("• Housekeeping optimization and scheduling")
    print("• Intelligent payment recovery strategies")
    print("• Comprehensive operations reporting")
    print("\nSystem ready for production deployment! 🚀")

if __name__ == "__main__":
    asyncio.run(run_demo())