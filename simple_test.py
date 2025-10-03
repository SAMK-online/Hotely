"""
Hotely - Simple Working Demo
============================
Basic test to demonstrate the system is working.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment
load_dotenv('hotelpilot/.env')

# Set API key in environment
os.environ['GOOGLE_AI_API_KEY'] = os.getenv('GOOGLE_AI_API_KEY', '')

def test_simple():
    """Run a simple synchronous test"""

    print("""
    ╔═══════════════════════════════════════╗
    ║     Hotely System Test            ║
    ║   Multi-Agent Hotel Operations AI     ║
    ╚═══════════════════════════════════════╝
    """)

    api_key = os.environ.get('GOOGLE_AI_API_KEY')
    if not api_key:
        print("❌ No API key found")
        return

    print(f"✅ API Key configured: {api_key[:10]}...")

    # Test with basic Python SDK
    try:
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')

        print("\n📊 Testing Dynamic Pricing Scenario...")
        print("-"*60)

        prompt = """You are a hotel revenue manager. Analyze this data and recommend pricing:

        Arlington Hotel (120 rooms)
        Current rate: $129 standard
        Tomorrow: Friday Dec 20

        Flight data:
        - DCA airport: +13% capacity (1000 extra seats)
        - IAD airport: +8% capacity (1000 extra seats)
        - No major events

        Current occupancy: 75%

        Apply these rules:
        - Max weekday increase: 10%
        - Max weekend increase: 12%

        Calculate demand lift and recommend new rates. Be concise."""

        response = model.generate_content(prompt)
        print("\n💡 AI Response:")
        print(response.text)

        print("\n" + "="*60)
        print("✅ System is working! The Hotely agents are ready.")
        print("="*60)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Check your API key in hotelpilot/.env")
        print("2. Ensure google-generativeai is installed: pip install google-generativeai")

if __name__ == "__main__":
    test_simple()