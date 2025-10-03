#!/usr/bin/env python
"""
Make a Demo Call - Retell calls YOUR phone
"""

import os
import asyncio
import aiohttp
from dotenv import load_dotenv

# Load environment
load_dotenv('hotelpilot/.env')

RETELL_API_KEY = os.getenv('RETELL_API_KEY')
RETELL_AGENT_ID = os.getenv('RETELL_AGENT_ID')

async def make_demo_call(to_phone):
    """Make Retell call your phone number"""

    headers = {
        "Authorization": f"Bearer {RETELL_API_KEY}",
        "Content-Type": "application/json"
    }

    call_data = {
        "agent_id": RETELL_AGENT_ID,
        "to": to_phone,
        "from": "+14155551234",  # Retell will use their number
        "metadata": {
            "demo": True,
            "purpose": "Hotel booking demo"
        }
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                "https://api.retellai.com/v2/create-phone-call",
                headers=headers,
                json=call_data
            ) as response:
                if response.status in [200, 201]:
                    result = await response.json()
                    print(f"✅ Call initiated!")
                    print(f"   Call ID: {result.get('call_id')}")
                    print(f"   Your phone should ring in a few seconds...")
                else:
                    text = await response.text()
                    print(f"❌ Error: {text}")
        except Exception as e:
            print(f"❌ Failed: {e}")

if __name__ == "__main__":
    print("""
    ====================================
    Retell Demo Call Generator
    ====================================

    This will make Retell call YOUR phone!
    """)

    phone = input("Enter your phone number (with country code, e.g., +1234567890): ")

    if not phone.startswith('+'):
        phone = '+1' + phone.replace('-', '').replace(' ', '')

    print(f"\nCalling {phone}...")
    asyncio.run(make_demo_call(phone))