"""
Hotely Data Models
==================
Core data models for the hotel operations system.
"""

from dataclasses import dataclass, field
from datetime import datetime, date, time
from typing import Dict, List, Optional, Any
from enum import Enum
import uuid

# Enums
class ReservationStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CHECKED_IN = "checked_in"
    CHECKED_OUT = "checked_out"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"

class RoomStatus(Enum):
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    DIRTY = "dirty"
    CLEANING = "cleaning"
    INSPECTING = "inspecting"
    OUT_OF_ORDER = "out_of_order"
    MAINTENANCE = "maintenance"

class PaymentStatus(Enum):
    PENDING = "pending"
    AUTHORIZED = "authorized"
    CAPTURED = "captured"
    FAILED = "failed"
    REFUNDED = "refunded"
    PARTIAL = "partial"

class TaskStatus(Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class MessageChannel(Enum):
    EMAIL = "email"
    SMS = "sms"
    WHATSAPP = "whatsapp"
    VOICE = "voice"

class TaskPriority(Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4
    VIP = 5

# Data Models
@dataclass
class Guest:
    """Guest information"""
    guest_id: str = field(default_factory=lambda: f"g_{uuid.uuid4().hex[:8]}")
    first_name: str = ""
    last_name: str = ""
    email: Optional[str] = None
    phone: Optional[str] = None
    language: str = "en"
    preferences: Dict[str, Any] = field(default_factory=dict)
    vip: bool = False
    loyalty_number: Optional[str] = None
    consent: Dict[str, bool] = field(default_factory=lambda: {
        "marketing": False,
        "sms": False,
        "voice_recording": False
    })
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

@dataclass
class Room:
    """Room information"""
    room_id: str
    room_number: str
    room_type: str  # e.g., "standard", "deluxe", "suite"
    floor: int
    status: RoomStatus = RoomStatus.AVAILABLE
    features: List[str] = field(default_factory=list)  # ["ocean_view", "balcony"]
    max_occupancy: int = 2
    base_rate: float = 0.0
    out_of_order_reason: Optional[str] = None
    last_cleaned: Optional[datetime] = None
    assigned_to: Optional[str] = None  # Staff ID

@dataclass
class Reservation:
    """Reservation details"""
    reservation_id: str = field(default_factory=lambda: f"res_{uuid.uuid4().hex[:8]}")
    guest_id: str = ""
    room_id: Optional[str] = None
    check_in: date = field(default_factory=date.today)
    check_out: date = field(default_factory=date.today)
    status: ReservationStatus = ReservationStatus.PENDING
    room_type: str = "standard"
    rate: float = 0.0
    channel: str = "direct"  # "direct", "ota", "phone", "walk-in"
    adults: int = 1
    children: int = 0
    special_requests: Optional[str] = None
    eta: Optional[time] = None
    deposit_amount: float = 0.0
    deposit_status: PaymentStatus = PaymentStatus.PENDING
    total_amount: float = 0.0
    balance_due: float = 0.0
    notes: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

@dataclass
class HousekeepingTask:
    """Housekeeping task"""
    task_id: str = field(default_factory=lambda: f"hk_{uuid.uuid4().hex[:8]}")
    room_id: str = ""
    reservation_id: Optional[str] = None
    task_type: str = "clean"  # "clean", "inspect", "deep_clean", "turndown"
    priority: TaskPriority = TaskPriority.NORMAL
    assigned_to: Optional[str] = None
    due_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: TaskStatus = TaskStatus.PENDING
    notes: Optional[str] = None
    inspection_required: bool = False
    inspection_passed: Optional[bool] = None

@dataclass
class Payment:
    """Payment record"""
    payment_id: str = field(default_factory=lambda: f"pay_{uuid.uuid4().hex[:8]}")
    reservation_id: str = ""
    guest_id: str = ""
    amount: float = 0.0
    currency: str = "USD"
    method: str = "card"  # "card", "cash", "check", "wire"
    status: PaymentStatus = PaymentStatus.PENDING
    transaction_id: Optional[str] = None
    last_four: Optional[str] = None
    failure_code: Optional[str] = None
    failure_message: Optional[str] = None
    retry_count: int = 0
    last_attempt: Optional[datetime] = None
    next_retry: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class Message:
    """Guest communication message"""
    message_id: str = field(default_factory=lambda: f"msg_{uuid.uuid4().hex[:8]}")
    guest_id: Optional[str] = None
    reservation_id: Optional[str] = None
    channel: MessageChannel = MessageChannel.EMAIL
    direction: str = "outbound"  # "inbound", "outbound"
    subject: Optional[str] = None
    content: str = ""
    intent: Optional[str] = None  # Detected intent for inbound
    sentiment: Optional[float] = None  # -1.0 to 1.0
    delivered: bool = False
    read: bool = False
    response_to: Optional[str] = None  # Parent message ID
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class RateProposal:
    """Dynamic rate proposal"""
    proposal_id: str = field(default_factory=lambda: f"rate_{uuid.uuid4().hex[:8]}")
    date: date = field(default_factory=date.today)
    room_type: str = "standard"
    current_rate: float = 0.0
    proposed_rate: float = 0.0
    percent_change: float = 0.0
    reason: str = ""
    confidence: float = 0.0
    demand_index: float = 0.0
    applied: bool = False
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    rollback_key: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class FlightSignal:
    """Flight demand signal"""
    signal_id: str = field(default_factory=lambda: f"sig_{uuid.uuid4().hex[:8]}")
    date: date = field(default_factory=date.today)
    airport: str = ""
    arrival_band: str = ""  # "morning", "midday", "evening", "late"
    seat_capacity: int = 0
    baseline_capacity: int = 0
    capacity_delta: float = 0.0
    fare_pressure: Optional[float] = None
    confidence: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class AuditLog:
    """Audit trail entry"""
    audit_id: str = field(default_factory=lambda: f"audit_{uuid.uuid4().hex[:8]}")
    actor: str = ""  # Agent or user ID
    object_type: str = ""
    object_id: str = ""
    action: str = ""
    previous_value: Optional[Dict[str, Any]] = None
    new_value: Optional[Dict[str, Any]] = None
    reason: Optional[str] = None
    policy_id: Optional[str] = None
    rollback_key: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class Event:
    """System event"""
    event_id: str = field(default_factory=lambda: f"evt_{uuid.uuid4().hex[:8]}")
    event_type: str = ""  # e.g., "reservation.created", "payment.failed"
    payload: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class AgentContext:
    """Context passed between agents"""
    session_id: str = field(default_factory=lambda: f"sess_{uuid.uuid4().hex[:8]}")
    property_id: str = ""
    user: Optional[str] = None
    guest: Optional[Guest] = None
    reservation: Optional[Reservation] = None
    state: Dict[str, Any] = field(default_factory=dict)
    events: List[Event] = field(default_factory=list)
    audit_trail: List[AuditLog] = field(default_factory=list)