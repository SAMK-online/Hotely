#!/usr/bin/env python
"""
Test Retell Agent Configuration
"""

import os
import asyncio
import aiohttp
from dotenv import load_dotenv

# Load environment
load_dotenv('hotelpilot/.env')

RETELL_API_KEY = os.getenv('RETELL_API_KEY')
RETELL_AGENT_ID = os.getenv('RETELL_AGENT_ID')

async def test_agent():
    """Test the configured agent"""

    print(f"Testing agent: {RETELL_AGENT_ID}")

    headers = {
        "Authorization": f"Bearer {RETELL_API_KEY}",
        "Content-Type": "application/json"
    }

    async with aiohttp.ClientSession() as session:
        # Get agent details
        try:
            async with session.get(
                f"https://api.retellai.com/get-agent/{RETELL_AGENT_ID}",
                headers=headers
            ) as response:
                if response.status == 200:
                    agent_data = await response.json()
                    print("\n✅ Agent found!")
                    print(f"   Name: {agent_data.get('agent_name', 'N/A')}")
                    print(f"   Voice: {agent_data.get('voice_id', 'N/A')}")
                    print(f"   Language: {agent_data.get('language', 'N/A')}")

                    # Check if webhook is configured
                    if 'webhook_url' in str(agent_data):
                        print(f"   Webhook: Configured")
                    else:
                        print(f"   Webhook: Not configured yet")

                else:
                    text = await response.text()
                    print(f"❌ Error {response.status}: {text}")
        except Exception as e:
            print(f"❌ Failed to get agent: {e}")

if __name__ == "__main__":
    print("""
    ====================================
    Testing Retell Agent Configuration
    ====================================
    """)

    asyncio.run(test_agent())

    print("""

    Next Steps:
    1. Set up ngrok: ngrok config add-authtoken YOUR_TOKEN
    2. Start tunnel: ngrok http 5001
    3. Add webhook URL to Retell dashboard
    4. Test with the "Test Agent" feature in Retell
    """)