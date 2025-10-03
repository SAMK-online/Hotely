"""
PMS Integration Tools
=====================
Tools for interacting with Property Management System.
"""

from typing import Dict, List, Optional, Any
from datetime import date, datetime
import logging
try:
    from hotelpilot.models.data_models import (
        Reservation, ReservationStatus, Room, RoomStatus,
        Guest, AuditLog, Event
    )
except ImportError:
    # Use relative imports if package not installed
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from models.data_models import (
        Reservation, ReservationStatus, Room, RoomStatus,
        Guest, AuditLog, Event
    )

logger = logging.getLogger(__name__)

# PMS Tools (These would connect to actual PMS in production)

def get_room_availability(
    check_in: str,
    check_out: str,
    room_type: Optional[str] = None,
    property_id: str = "prop_001"
) -> Dict[str, Any]:
    """
    Check room availability for given dates.

    Args:
        check_in: Check-in date (YYYY-MM-DD)
        check_out: Check-out date (YYYY-MM-DD)
        room_type: Optional specific room type
        property_id: Property identifier

    Returns:
        Dictionary with available rooms and rates
    """
    logger.info(f"Checking availability from {check_in} to {check_out}")

    # Simulated availability check
    available_rooms = [
        {"room_type": "standard", "count": 5, "rate": 129.00},
        {"room_type": "deluxe", "count": 2, "rate": 189.00},
        {"room_type": "suite", "count": 1, "rate": 299.00}
    ]

    if room_type:
        available_rooms = [r for r in available_rooms if r["room_type"] == room_type]

    return {
        "status": "success",
        "check_in": check_in,
        "check_out": check_out,
        "available": len(available_rooms) > 0,
        "rooms": available_rooms,
        "property_id": property_id
    }

def create_reservation(
    guest_name: str,
    guest_email: str,
    guest_phone: str,
    check_in: str,
    check_out: str,
    room_type: str,
    rate: float,
    adults: int = 1,
    children: int = 0,
    special_requests: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a new reservation in PMS.

    Args:
        guest_name: Guest full name
        guest_email: Guest email
        guest_phone: Guest phone
        check_in: Check-in date
        check_out: Check-out date
        room_type: Room type
        rate: Daily rate
        adults: Number of adults
        children: Number of children
        special_requests: Special requests

    Returns:
        Reservation confirmation details
    """
    try:
        # Parse guest name
        name_parts = guest_name.split(" ", 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ""

        # Calculate total
        check_in_date = datetime.strptime(check_in, "%Y-%m-%d").date()
        check_out_date = datetime.strptime(check_out, "%Y-%m-%d").date()
        nights = (check_out_date - check_in_date).days
        total_amount = rate * nights

        # Create reservation (simulated)
        reservation = Reservation(
            guest_id=f"g_{guest_email[:8]}",
            check_in=check_in_date,
            check_out=check_out_date,
            room_type=room_type,
            rate=rate,
            adults=adults,
            children=children,
            special_requests=special_requests,
            total_amount=total_amount,
            balance_due=total_amount,
            status=ReservationStatus.CONFIRMED
        )

        logger.info(f"Created reservation {reservation.reservation_id}")

        return {
            "status": "success",
            "reservation_id": reservation.reservation_id,
            "confirmation_number": reservation.reservation_id.upper(),
            "guest_name": guest_name,
            "check_in": check_in,
            "check_out": check_out,
            "room_type": room_type,
            "total_amount": total_amount,
            "nights": nights,
            "message": f"Reservation confirmed for {nights} nights"
        }

    except Exception as e:
        logger.error(f"Failed to create reservation: {e}")
        return {
            "status": "error",
            "error": str(e),
            "message": "Failed to create reservation"
        }

def modify_reservation(
    reservation_id: str,
    modifications: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Modify existing reservation.

    Args:
        reservation_id: Reservation ID
        modifications: Dictionary of fields to modify

    Returns:
        Modification result
    """
    logger.info(f"Modifying reservation {reservation_id}: {modifications}")

    # Simulated modification
    allowed_fields = ["check_in", "check_out", "room_type", "special_requests", "eta"]

    applied = {}
    for field, value in modifications.items():
        if field in allowed_fields:
            applied[field] = value

    return {
        "status": "success",
        "reservation_id": reservation_id,
        "modifications_applied": applied,
        "message": f"Reservation {reservation_id} updated successfully"
    }

def cancel_reservation(
    reservation_id: str,
    reason: Optional[str] = None
) -> Dict[str, Any]:
    """
    Cancel a reservation.

    Args:
        reservation_id: Reservation ID
        reason: Cancellation reason

    Returns:
        Cancellation confirmation
    """
    logger.info(f"Cancelling reservation {reservation_id}")

    return {
        "status": "success",
        "reservation_id": reservation_id,
        "cancelled_at": datetime.now().isoformat(),
        "reason": reason or "Guest requested cancellation",
        "refund_amount": 0.0,  # Would calculate based on policy
        "message": f"Reservation {reservation_id} cancelled"
    }

def get_room_status(room_id: str) -> Dict[str, Any]:
    """
    Get current room status.

    Args:
        room_id: Room identifier

    Returns:
        Room status information
    """
    # Simulated room status
    return {
        "status": "success",
        "room_id": room_id,
        "room_number": f"R{room_id[-3:]}",
        "room_status": "available",
        "cleanliness": "clean",
        "occupied": False,
        "last_cleaned": datetime.now().isoformat(),
        "maintenance_required": False
    }

def update_room_status(
    room_id: str,
    status: str,
    notes: Optional[str] = None
) -> Dict[str, Any]:
    """
    Update room status in PMS.

    Args:
        room_id: Room identifier
        status: New status
        notes: Optional notes

    Returns:
        Update confirmation
    """
    logger.info(f"Updating room {room_id} status to {status}")

    valid_statuses = ["available", "occupied", "dirty", "cleaning", "maintenance", "out_of_order"]

    if status not in valid_statuses:
        return {
            "status": "error",
            "error": f"Invalid status. Must be one of: {valid_statuses}"
        }

    return {
        "status": "success",
        "room_id": room_id,
        "new_status": status,
        "updated_at": datetime.now().isoformat(),
        "notes": notes,
        "message": f"Room {room_id} status updated to {status}"
    }

def attach_note_to_reservation(
    reservation_id: str,
    note: str,
    author: str = "system"
) -> Dict[str, Any]:
    """
    Attach a note to reservation.

    Args:
        reservation_id: Reservation ID
        note: Note content
        author: Note author

    Returns:
        Confirmation
    """
    logger.info(f"Adding note to reservation {reservation_id}")

    return {
        "status": "success",
        "reservation_id": reservation_id,
        "note_id": f"note_{datetime.now().timestamp()}",
        "note": note,
        "author": author,
        "created_at": datetime.now().isoformat(),
        "message": "Note added successfully"
    }

def get_arrivals_departures(
    date: str,
    property_id: str = "prop_001"
) -> Dict[str, Any]:
    """
    Get arrivals and departures for a specific date.

    Args:
        date: Date (YYYY-MM-DD)
        property_id: Property identifier

    Returns:
        Lists of arrivals and departures
    """
    # Simulated data
    arrivals = [
        {
            "reservation_id": "res_001",
            "guest_name": "John Smith",
            "room_type": "deluxe",
            "eta": "14:00",
            "vip": False
        },
        {
            "reservation_id": "res_002",
            "guest_name": "Sarah Johnson",
            "room_type": "suite",
            "eta": "16:00",
            "vip": True
        }
    ]

    departures = [
        {
            "reservation_id": "res_003",
            "guest_name": "Mike Wilson",
            "room_number": "201",
            "checkout_time": "11:00"
        }
    ]

    stayovers = [
        {
            "reservation_id": "res_004",
            "guest_name": "Emily Brown",
            "room_number": "305",
            "nights_remaining": 2
        }
    ]

    return {
        "status": "success",
        "date": date,
        "property_id": property_id,
        "arrivals": arrivals,
        "arrival_count": len(arrivals),
        "departures": departures,
        "departure_count": len(departures),
        "stayovers": stayovers,
        "stayover_count": len(stayovers),
        "total_occupied": len(stayovers)
    }

def set_rate_plan(
    room_type: str,
    date: str,
    rate: float,
    restrictions: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Update rate plan in PMS.

    Args:
        room_type: Room type
        date: Date for rate
        rate: New rate
        restrictions: Optional restrictions (min_stay, closed_to_arrival, etc.)

    Returns:
        Update confirmation
    """
    logger.info(f"Setting rate for {room_type} on {date}: ${rate}")

    return {
        "status": "success",
        "room_type": room_type,
        "date": date,
        "previous_rate": 129.00,  # Would fetch actual
        "new_rate": rate,
        "percent_change": ((rate - 129.00) / 129.00) * 100,
        "restrictions": restrictions or {},
        "updated_at": datetime.now().isoformat(),
        "message": f"Rate updated for {room_type} on {date}"
    }