#!/usr/bin/env python
"""
HotelPilot - Simple Orchestration Version
==========================================
A cleaner multi-agent system without complex ADK dependencies.
"""

import os
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment
load_dotenv('hotelpilot/.env')
genai.configure(api_key=os.getenv('GOOGLE_AI_API_KEY'))

# Agent Types
class AgentType(Enum):
    OPS_COPILOT = "ops_copilot"
    DEMAND_MANAGER = "demand_manager"
    GUEST_LIFECYCLE = "guest_lifecycle"
    HOUSEKEEPING = "housekeeping"
    BILLING_RECOVERY = "billing_recovery"

@dataclass
class Agent:
    """Simple agent definition"""
    name: str
    type: AgentType
    description: str
    system_prompt: str
    tools: List[str] = None

class HotelPilotOrchestrator:
    """Simple orchestrator for multi-agent hotel system"""

    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        self.agents = self._initialize_agents()
        self.context = {
            "hotel_name": "Arlington Hotel",
            "rooms": 120,
            "current_occupancy": 0.75,
            "base_rates": {
                "standard": 129,
                "deluxe": 189,
                "suite": 299
            }
        }

    def _initialize_agents(self) -> Dict[AgentType, Agent]:
        """Initialize all agents with their prompts"""
        return {
            AgentType.OPS_COPILOT: Agent(
                name="Ops Copilot",
                type=AgentType.OPS_COPILOT,
                description="Main hotel operations supervisor",
                system_prompt="""You are the Operations Supervisor for Arlington Hotel.
                You coordinate all hotel operations including pricing, guest services,
                housekeeping, and payments. Provide strategic oversight and decisions.
                Hotel: 120 rooms, 75% avg occupancy, $129/$189/$299 rates."""
            ),

            AgentType.DEMAND_MANAGER: Agent(
                name="Demand Manager",
                type=AgentType.DEMAND_MANAGER,
                description="Dynamic pricing specialist",
                system_prompt="""You are the Revenue Manager for Arlington Hotel.
                Analyze demand signals (flight data, events, occupancy) and recommend pricing.
                Rules: Weekday cap +10%, Weekend cap +12%, Weekly cap +18%.
                Airport weights: DCA 60%, IAD 30%, BWI 10%.
                Calculate demand lift index and show your reasoning."""
            ),

            AgentType.GUEST_LIFECYCLE: Agent(
                name="Guest Lifecycle Manager",
                type=AgentType.GUEST_LIFECYCLE,
                description="Guest communication specialist",
                system_prompt="""You manage all guest communications for Arlington Hotel.
                Create warm, professional messages for pre-arrival, check-in, stay, and checkout.
                Keep messages concise (under 160 chars for SMS). Respect quiet hours 9PM-8AM.
                Personalize for VIP guests. Maximum 3 messages per day per guest."""
            ),

            AgentType.HOUSEKEEPING: Agent(
                name="Housekeeping Coordinator",
                type=AgentType.HOUSEKEEPING,
                description="Room operations optimizer",
                system_prompt="""You coordinate housekeeping for Arlington Hotel.
                Standards: Standard clean 24.5min, Rush clean 30min window, Deep clean 45min.
                VIP rooms require inspection. Create optimized schedules with staff assignments.
                Prioritize: Checkouts before arrivals, VIP rooms, early check-ins."""
            ),

            AgentType.BILLING_RECOVERY: Agent(
                name="Billing Recovery Specialist",
                type=AgentType.BILLING_RECOVERY,
                description="Payment recovery expert",
                system_prompt="""You handle payment recovery for Arlington Hotel.
                Recovery timeline: T+1hr silent retry, T+6hr email, T+24hr multi-channel.
                Target 65% recovery within 48 hours. Be understanding with loyal guests.
                Offer payment plans when appropriate. VIP guests get personal attention."""
            )
        }

    def route_request(self, user_input: str) -> AgentType:
        """Route user request to appropriate agent"""
        routing_prompt = f"""Determine which hotel agent should handle this request:

        User request: {user_input}

        Available agents:
        1. OPS_COPILOT - General operations, strategy, overall status
        2. DEMAND_MANAGER - Pricing, rates, revenue optimization
        3. GUEST_LIFECYCLE - Guest messages, communications, welcome/thank you
        4. HOUSEKEEPING - Cleaning schedules, room readiness, staff assignments
        5. BILLING_RECOVERY - Payment issues, failed transactions, recovery

        Respond with ONLY the agent name (e.g., OPS_COPILOT)"""

        response = self.model.generate_content(routing_prompt)
        agent_name = response.text.strip().upper()

        # Default to OPS_COPILOT if unclear
        try:
            return AgentType[agent_name]
        except:
            return AgentType.OPS_COPILOT

    def process_with_agent(self, agent_type: AgentType, user_input: str) -> str:
        """Process request with specific agent"""
        agent = self.agents[agent_type]

        # Build the full prompt
        prompt = f"""{agent.system_prompt}

        Current Context:
        - Date: Today (for demo purposes)
        - Occupancy: {self.context['current_occupancy']*100:.0f}%
        - Available Rooms: {int(self.context['rooms'] * (1-self.context['current_occupancy']))}

        User Request: {user_input}

        Provide a helpful, professional response:"""

        response = self.model.generate_content(prompt)
        return response.text

    def process(self, user_input: str, agent_type: Optional[AgentType] = None) -> Dict[str, Any]:
        """Main processing method"""

        # Route to agent if not specified
        if agent_type is None:
            agent_type = self.route_request(user_input)

        # Process with agent
        agent = self.agents[agent_type]
        response_text = self.process_with_agent(agent_type, user_input)

        return {
            "agent": agent.name,
            "agent_type": agent_type.value,
            "response": response_text,
            "context": self.context
        }

    def handoff(self, from_agent: AgentType, to_agent: AgentType, context: str) -> str:
        """Hand off task from one agent to another"""
        handoff_prompt = f"""Agent handoff from {self.agents[from_agent].name} to {self.agents[to_agent].name}.

        Context from previous agent: {context}

        Continue handling this task with your specialized expertise."""

        return self.process_with_agent(to_agent, handoff_prompt)

    def collaborate(self, user_input: str, agents: List[AgentType]) -> Dict[str, Any]:
        """Multiple agents collaborate on a task"""
        results = {}

        for agent_type in agents:
            agent = self.agents[agent_type]
            response = self.process_with_agent(agent_type, user_input)
            results[agent.name] = response

        # Ops Copilot summarizes
        summary_prompt = f"""As Ops Copilot, summarize the following multi-agent responses to: {user_input}

        {json.dumps(results, indent=2)}

        Provide a cohesive action plan based on all inputs:"""

        final_response = self.model.generate_content(summary_prompt)

        return {
            "individual_responses": results,
            "summary": final_response.text
        }

# Simple command-line interface
def main():
    """Run the simple orchestrator"""
    orchestrator = HotelPilotOrchestrator()

    print("""
    ╔═══════════════════════════════════════╗
    ║   HotelPilot - Simple Orchestration   ║
    ║      Multi-Agent Hotel System         ║
    ╚═══════════════════════════════════════╝
    """)

    # Example: Simple single agent
    print("Example 1: Single Agent")
    print("-" * 40)
    result = orchestrator.process("What should our rates be for tomorrow with high flight demand?")
    print(f"Agent: {result['agent']}")
    print(f"Response: {result['response'][:300]}...")

    # Example: Collaboration
    print("\n\nExample 2: Multi-Agent Collaboration")
    print("-" * 40)
    result = orchestrator.collaborate(
        "Prepare for VIP guest arrival tomorrow",
        [AgentType.GUEST_LIFECYCLE, AgentType.HOUSEKEEPING, AgentType.OPS_COPILOT]
    )
    print(f"Summary: {result['summary'][:300]}...")

    # Interactive mode
    print("\n\nInteractive Mode (type 'quit' to exit)")
    print("-" * 40)
    while True:
        user_input = input("\n> ")
        if user_input.lower() == 'quit':
            break

        result = orchestrator.process(user_input)
        print(f"\n[{result['agent']}]: {result['response']}")

if __name__ == "__main__":
    main()