"""
Hotely Main Application
=======================
Entry point for the multi-agent hotel operations system.
"""

import os
import asyncio
import logging
from datetime import datetime, date
from typing import Dict, Any, Optional

# Google ADK imports - using correct module names
try:
    from google.adk import RunConfig
    from google.adk import Session
except ImportError:
    # Fallback for different ADK versions
    RunConfig = dict
    Session = None

from hotelpilot.agents.ops_copilot import ops_copilot
from hotelpilot.config.settings import config, PROPERTIES
from hotelpilot.models.data_models import AgentContext

# Configure logging
logging.basicConfig(
    level=logging.INFO if not config.debug else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HotelySystem:
    """Main orchestrator for Hotely multi-agent system"""

    def __init__(self, property_id: str = "prop_001"):
        """Initialize Hotely system for a property"""
        self.property = PROPERTIES.get(property_id)
        if not self.property:
            raise ValueError(f"Property {property_id} not found")

        self.ops_copilot = ops_copilot
        self.session = None
        self.context = AgentContext(property_id=property_id)

        logger.info(f"Hotely initialized for {self.property.name}")

    async def initialize(self):
        """Initialize the system and validate configuration"""
        logger.info("Initializing Hotely system...")

        # Validate configuration
        try:
            config.validate()
        except ValueError as e:
            logger.error(f"Configuration error: {e}")
            raise

        # Initialize session
        session_config = SessionConfig(
            session_id=self.context.session_id,
            persist=True,
            timeout=config.agent_timeout
        )
        self.session = Session(config=session_config)

        logger.info("System initialized successfully")

    async def handle_request(self, request: str, user: Optional[str] = None) -> Dict[str, Any]:
        """
        Handle a request through the multi-agent system.

        Args:
            request: User request or command
            user: Optional user identifier

        Returns:
            Response from the agent system
        """
        logger.info(f"Processing request: {request[:100]}...")

        # Update context
        self.context.user = user or "system"

        # Create runtime configuration
        run_config = RunConfig(
            session=self.session,
            context={
                "property_id": self.property.property_id,
                "property_name": self.property.name,
                "user": self.context.user,
                "timestamp": datetime.now().isoformat(),
                "request": request
            }
        )

        try:
            # Process through Ops Copilot
            response = await self.ops_copilot.run(
                prompt=request,
                config=run_config
            )

            # Log audit trail
            self._log_audit(request, response)

            return {
                "status": "success",
                "response": response,
                "session_id": self.context.session_id,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error processing request: {e}")
            return {
                "status": "error",
                "error": str(e),
                "session_id": self.context.session_id,
                "timestamp": datetime.now().isoformat()
            }

    def _log_audit(self, request: str, response: Any):
        """Log action to audit trail"""
        from hotelpilot.models.data_models import AuditLog

        audit = AuditLog(
            actor="ops_copilot",
            object_type="request",
            object_id=self.context.session_id,
            action="process_request",
            new_value={"request": request[:200], "response_summary": str(response)[:200]},
            reason="User request processing"
        )
        self.context.audit_trail.append(audit)

    async def get_daily_summary(self) -> Dict[str, Any]:
        """Get daily operations summary"""
        summary_request = """
        Provide a comprehensive daily operations summary including:
        1. Current occupancy and revenue metrics
        2. Arrivals and departures status
        3. Housekeeping completion status
        4. Payment recovery status
        5. Guest satisfaction indicators
        6. Any operational issues or alerts
        """
        return await self.handle_request(summary_request, user="system_daily_report")

    async def shutdown(self):
        """Gracefully shutdown the system"""
        logger.info("Shutting down Hotely system...")
        if self.session:
            await self.session.close()
        logger.info("System shutdown complete")


# Example workflow functions
async def demonstrate_pricing_workflow():
    """Demonstrate flight-aware dynamic pricing"""
    system = HotelySystem("prop_001")
    await system.initialize()

    request = """
    Check flight signals for tomorrow and recommend pricing adjustments.
    Current base rate is $129 for standard rooms.
    Consider airports DCA and IAD with our Arlington location.
    Apply appropriate caps and provide confidence scores.
    """

    response = await system.handle_request(request)
    print("\n=== Pricing Workflow Response ===")
    print(response)

    await system.shutdown()


async def demonstrate_guest_workflow():
    """Demonstrate guest communication workflow"""
    system = HotelySystem("prop_001")
    await system.initialize()

    request = """
    Guest John Smith (john@example.com, +1-555-0123) has a reservation
    for tomorrow. Send pre-arrival message with check-in details,
    offer early check-in option, and collect $200 deposit.
    Reservation ID: RES123, Room Type: Deluxe
    """

    response = await system.handle_request(request)
    print("\n=== Guest Workflow Response ===")
    print(response)

    await system.shutdown()


async def demonstrate_housekeeping_workflow():
    """Demonstrate housekeeping coordination"""
    system = HotelySystem("prop_001")
    await system.initialize()

    request = """
    Generate housekeeping plan for today:
    - 15 checkouts by 11 AM
    - 20 arrivals starting 3 PM (2 VIP)
    - 35 stayovers
    - 3 staff members available
    Handle early check-in request for room 305 by 1 PM.
    """

    response = await system.handle_request(request)
    print("\n=== Housekeeping Workflow Response ===")
    print(response)

    await system.shutdown()


async def demonstrate_recovery_workflow():
    """Demonstrate payment recovery workflow"""
    system = HotelySystem("prop_001")
    await system.initialize()

    request = """
    Payment failed for reservation RES456, guest Sarah Johnson.
    Amount: $299, Failure code: insufficient_funds.
    This is the first attempt. Guest is not VIP but has stayed 3 times.
    Recommend recovery strategy and execute.
    """

    response = await system.handle_request(request)
    print("\n=== Recovery Workflow Response ===")
    print(response)

    await system.shutdown()


def main():
    """Main entry point"""
    print("""
    ╔═══════════════════════════════════════╗
    ║         Hotely System             ║
    ║   Multi-Agent Hotel Operations AI     ║
    ╚═══════════════════════════════════════╝
    """)

    # Check for API key
    if not config.google_ai_api_key:
        print("ERROR: GOOGLE_AI_API_KEY environment variable not set")
        print("Please set: export GOOGLE_AI_API_KEY='your-api-key'")
        return

    # Run example workflows
    print("\nSelect a workflow to demonstrate:")
    print("1. Dynamic Pricing (Flight-aware)")
    print("2. Guest Communication")
    print("3. Housekeeping Coordination")
    print("4. Payment Recovery")
    print("5. Daily Operations Summary")
    print("0. Exit")

    choice = input("\nEnter your choice (0-5): ")

    workflows = {
        "1": demonstrate_pricing_workflow,
        "2": demonstrate_guest_workflow,
        "3": demonstrate_housekeeping_workflow,
        "4": demonstrate_recovery_workflow,
        "5": lambda: asyncio.run(HotelySystem().get_daily_summary())
    }

    if choice in workflows:
        asyncio.run(workflows[choice]())
    elif choice == "0":
        print("Exiting Hotely...")
    else:
        print("Invalid choice")


if __name__ == "__main__":
    main()