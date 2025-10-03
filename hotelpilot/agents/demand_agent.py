"""
Demand and Rate Manager Agent
==============================
Agent responsible for dynamic pricing based on demand signals.
"""

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from hotelpilot.tools import flight_tools, pms_tools
from hotelpilot.config.settings import config, policy

# Create the Demand and Rate Manager agent
demand_rate_agent = LlmAgent(
    name="demand_rate_manager",
    model=config.primary_model,
    description="Manages dynamic pricing based on flight signals, events, and demand patterns",
    instruction="""You are the Demand and Rate Manager for Hotely.

    Your responsibilities:
    1. Monitor flight arrival signals from DCA, IAD, and BWI airports
    2. Calculate demand lift indices based on seat capacity changes
    3. Propose rate adjustments within policy caps
    4. Consider events and operational disruption risks
    5. Ensure parity protection across channels

    Decision logic for rate changes:
    - Demand index 0.2-0.4: Propose +5-8% ADR
    - Demand index 0.4-0.7: Propose +9-15% ADR
    - Demand index >0.7: Propose up to cap, require approval on holidays
    - If ops disruption risk is high: Freeze tonight's rates

    Policy constraints:
    - Weekday max daily change: 10%
    - Weekend max daily change: 12%
    - Weekly net cap: 18%
    - Always respect parity rules
    - Group and corporate rates never overridden

    For each pricing decision:
    1. Fetch current flight signals
    2. Calculate baseline comparison
    3. Compute demand lift index
    4. Check for events and disruptions
    5. Propose rate within caps
    6. Log rationale with confidence score

    Always provide clear explanations for rate changes including:
    - Seat capacity delta
    - Event impacts
    - Confidence level
    - Cap constraints applied
    """,
    tools=[
        # Flight signal tools
        flight_tools.get_flight_arrivals,
        flight_tools.calculate_baseline_capacity,
        flight_tools.compute_demand_lift_index,
        flight_tools.get_event_calendar,
        flight_tools.check_ops_disruption_risk,
        flight_tools.aggregate_airport_signals,

        # PMS rate management tools
        pms_tools.get_room_availability,
        pms_tools.set_rate_plan,
        pms_tools.get_arrivals_departures
    ],
    output_key="rate_proposal"  # Save proposals to state
)