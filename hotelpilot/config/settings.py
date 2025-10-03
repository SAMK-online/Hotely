"""
Hotely Configuration Settings
=============================
Central configuration for the multi-agent hotel operations system.
"""

import os
from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Environment(Enum):
    """Environment types"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

@dataclass
class PropertyConfig:
    """Configuration for a specific hotel property"""
    property_id: str
    name: str
    rooms: int
    location: str
    timezone: str = "America/New_York"

    # Pricing configuration
    max_daily_rate_change: float = 0.10  # 10% max daily change
    max_weekly_rate_change: float = 0.18  # 18% max weekly change
    weekend_rate_cap: float = 0.12  # 12% for weekends

    # Airport weights for Northern Virginia properties
    airport_weights: Dict[str, float] = None

    # Operating hours
    quiet_hours_start: int = 21  # 9 PM
    quiet_hours_end: int = 8     # 8 AM

    # Thresholds
    vip_threshold: float = 1000.0  # VIP spend threshold
    payment_retry_max: int = 3

    def __post_init__(self):
        """Set default airport weights based on location"""
        if self.airport_weights is None:
            if "Arlington" in self.location or "Alexandria" in self.location:
                self.airport_weights = {"DCA": 0.6, "IAD": 0.3, "BWI": 0.1}
            elif "Reston" in self.location or "Tysons" in self.location:
                self.airport_weights = {"IAD": 0.6, "DCA": 0.3, "BWI": 0.1}
            else:
                self.airport_weights = {"DCA": 0.5, "IAD": 0.4, "BWI": 0.1}

@dataclass
class SystemConfig:
    """System-wide configuration"""

    # Environment
    environment: Environment = Environment.DEVELOPMENT
    debug: bool = True

    # API Keys (loaded from environment)
    google_ai_api_key: str = ""
    stripe_api_key: str = ""
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    whatsapp_api_key: str = ""

    # Models
    primary_model: str = "gemini-2.0-flash-exp"
    fast_model: str = "gemini-1.5-flash"

    # Agent settings
    max_agents: int = 10
    agent_timeout: int = 30  # seconds
    parallel_execution: bool = True

    # Integration endpoints
    pms_endpoint: str = ""
    channel_manager_endpoint: str = ""

    # Event bus
    event_retention_days: int = 30
    audit_retention_days: int = 90

    # Performance
    cache_ttl: int = 300  # 5 minutes
    batch_size: int = 100

    @classmethod
    def from_env(cls) -> 'SystemConfig':
        """Load configuration from environment variables"""
        return cls(
            environment=Environment(os.getenv("ENVIRONMENT", "development")),
            debug=os.getenv("DEBUG", "true").lower() == "true",
            google_ai_api_key=os.getenv("GOOGLE_AI_API_KEY", ""),
            stripe_api_key=os.getenv("STRIPE_API_KEY", ""),
            twilio_account_sid=os.getenv("TWILIO_ACCOUNT_SID", ""),
            twilio_auth_token=os.getenv("TWILIO_AUTH_TOKEN", ""),
            whatsapp_api_key=os.getenv("WHATSAPP_API_KEY", ""),
            primary_model=os.getenv("PRIMARY_MODEL", "gemini-2.0-flash-exp"),
            fast_model=os.getenv("FAST_MODEL", "gemini-1.5-flash"),
            pms_endpoint=os.getenv("PMS_ENDPOINT", ""),
            channel_manager_endpoint=os.getenv("CHANNEL_MANAGER_ENDPOINT", "")
        )

    def validate(self) -> None:
        """Validate required configuration"""
        if not self.google_ai_api_key:
            raise ValueError("GOOGLE_AI_API_KEY is required")

        if self.environment == Environment.PRODUCTION:
            if not self.stripe_api_key:
                raise ValueError("STRIPE_API_KEY is required for production")
            if not self.twilio_account_sid:
                raise ValueError("TWILIO_ACCOUNT_SID is required for production")

# Policy configuration
@dataclass
class PolicyConfig:
    """Policy and guardrail configuration"""

    # Rate change caps
    rate_caps = {
        "weekday_max": 0.10,  # 10%
        "weekend_max": 0.12,  # 12%
        "weekly_net": 0.18,   # 18%
        "holiday_multiplier": 1.5
    }

    # Confidence thresholds
    confidence_thresholds = {
        "auto_approve": 0.7,
        "suggest_only": 0.6,
        "min_sample": 10
    }

    # Demand lift thresholds
    demand_lift_actions = {
        "low": (0.2, 0.4, 0.08),     # index range and ADR increase
        "medium": (0.4, 0.7, 0.15),
        "high": (0.7, 1.0, 0.20)
    }

    # Retry schedules (in hours)
    payment_retry_schedule = [1, 6, 24]

    # Guest communication
    message_frequency_cap = 3  # Max messages per day
    vip_auto_upgrade = True

    # Housekeeping
    rush_clean_window = 30  # minutes for rush cleans
    inspection_rate = 0.20  # 20% random inspection

# Load configuration
config = SystemConfig.from_env()
policy = PolicyConfig()

# Sample property configurations
PROPERTIES = {
    "prop_001": PropertyConfig(
        property_id="prop_001",
        name="Arlington Suites",
        rooms=120,
        location="Arlington, VA"
    ),
    "prop_002": PropertyConfig(
        property_id="prop_002",
        name="Tysons Corner Inn",
        rooms=85,
        location="Tysons, VA"
    )
}