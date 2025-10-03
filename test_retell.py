#!/usr/bin/env python
"""
Test Retell AI API Connection
"""

import os
import asyncio
import aiohttp
import json
from dotenv import load_dotenv

# Load environment
load_dotenv('hotelpilot/.env')

RETELL_API_KEY = os.getenv('RETELL_API_KEY')

async def test_retell_api():
    """Test basic Retell API connection"""

    print(f"Testing with API key: key_...{RETELL_API_KEY[-10:]}")

    headers = {
        "Authorization": f"Bearer {RETELL_API_KEY}",
        "Content-Type": "application/json"
    }

    # Test getting agents list
    async with aiohttp.ClientSession() as session:
        print("\n1. Testing API connection...")
        try:
            async with session.get(
                "https://api.retellai.com/list-agents",
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    # Handle both list and dict responses
                    if isinstance(data, list):
                        print(f"✅ API connected! Found {len(data)} existing agents")
                    elif isinstance(data, dict):
                        agents = data.get('agents', data.get('data', []))
                        print(f"✅ API connected! Found {len(agents)} existing agents")
                    else:
                        print(f"✅ API connected! Response: {data}")
                else:
                    text = await response.text()
                    print(f"❌ API Error {response.status}: {text}")
                    return
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return

        print("\n2. Creating test agent...")

        # First, let's create an LLM
        print("   Creating LLM configuration...")
        llm_config = {
            "general_prompt": "You are Sarah, a friendly hotel booking assistant for Arlington Hotel. Keep responses brief and natural. Always be helpful and professional.",
            "begin_message": "Thank you for calling Arlington Hotel, this is Sarah. How may I assist you today?",
            "model": "gpt-4o-mini"
        }

        try:
            async with session.post(
                "https://api.retellai.com/create-retell-llm",
                headers=headers,
                json=llm_config
            ) as response:
                if response.status in [200, 201]:
                    llm_data = await response.json()
                    llm_id = llm_data.get('llm_id')
                    print(f"   ✅ LLM created: {llm_id}")
                else:
                    text = await response.text()
                    print(f"   ❌ Failed to create LLM: {text}")
                    # Try to proceed with default
                    llm_id = None
        except Exception as e:
            print(f"   ❌ LLM creation failed: {e}")
            llm_id = None

        # Now create the agent
        agent_config = {
            "agent_name": "Arlington Hotel Test Agent",
            "voice_id": "rachel",
            "language": "en-US"
        }

        # Add response engine if we have an LLM
        if llm_id:
            agent_config["response_engine"] = {
                "type": "retell-llm",
                "llm_id": llm_id
            }
        else:
            # Try with webhook response
            agent_config["response_engine"] = {
                "type": "webhook",
                "webhook_url": "https://your-webhook.com/response"
            }

        try:
            async with session.post(
                "https://api.retellai.com/create-agent",
                headers=headers,
                json=agent_config
            ) as response:
                if response.status in [200, 201]:
                    data = await response.json()
                    print(f"✅ Agent created!")
                    print(f"   Agent ID: {data.get('agent_id')}")
                    return data.get('agent_id')
                else:
                    text = await response.text()
                    print(f"❌ Failed to create agent {response.status}: {text}")
        except Exception as e:
            print(f"❌ Agent creation failed: {e}")

if __name__ == "__main__":
    print("""
    ====================================
    Testing Retell AI API Connection
    ====================================
    """)

    if not RETELL_API_KEY or RETELL_API_KEY == 'your_retell_api_key_here':
        print("❌ No API key found. Please set RETELL_API_KEY in hotelpilot/.env")
    else:
        agent_id = asyncio.run(test_retell_api())

        if agent_id:
            print(f"""
    ✅ Success! Your Retell AI is working.

    Next steps:
    1. Add this agent ID to your .env file:
       RETELL_AGENT_ID={agent_id}

    2. Get a phone number from Retell dashboard:
       https://dashboard.retellai.com

    3. Set up webhook URL (use ngrok for local testing)
    """)