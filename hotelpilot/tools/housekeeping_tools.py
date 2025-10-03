"""
Housekeeping and Maintenance Tools
===================================
Tools for managing housekeeping tasks and maintenance tickets.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
from hotelpilot.models.data_models import (
    HousekeepingTask, TaskStatus, TaskPriority,
    Room, RoomStatus
)

logger = logging.getLogger(__name__)

def create_housekeeping_task(
    room_id: str,
    task_type: str,
    priority: str = "normal",
    due_at: Optional[str] = None,
    notes: Optional[str] = None,
    reservation_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a housekeeping task.

    Args:
        room_id: Room identifier
        task_type: Type of task (clean, inspect, deep_clean, turndown)
        priority: Task priority
        due_at: When task is due (ISO format)
        notes: Additional notes
        reservation_id: Associated reservation

    Returns:
        Created task details
    """
    logger.info(f"Creating {task_type} task for room {room_id}")

    priority_map = {
        "low": TaskPriority.LOW,
        "normal": TaskPriority.NORMAL,
        "high": TaskPriority.HIGH,
        "urgent": TaskPriority.URGENT,
        "vip": TaskPriority.VIP
    }

    task = HousekeepingTask(
        room_id=room_id,
        task_type=task_type,
        priority=priority_map.get(priority, TaskPriority.NORMAL),
        due_at=datetime.fromisoformat(due_at) if due_at else datetime.now() + timedelta(hours=2),
        notes=notes,
        reservation_id=reservation_id,
        inspection_required=task_type == "deep_clean" or priority == "vip"
    )

    return {
        "status": "success",
        "task_id": task.task_id,
        "room_id": room_id,
        "task_type": task_type,
        "priority": priority,
        "due_at": task.due_at.isoformat(),
        "inspection_required": task.inspection_required,
        "message": f"Housekeeping task created for room {room_id}"
    }

def assign_housekeeping_task(
    task_id: str,
    staff_id: str
) -> Dict[str, Any]:
    """
    Assign task to staff member.

    Args:
        task_id: Task identifier
        staff_id: Staff member ID

    Returns:
        Assignment confirmation
    """
    logger.info(f"Assigning task {task_id} to {staff_id}")

    return {
        "status": "success",
        "task_id": task_id,
        "assigned_to": staff_id,
        "assigned_at": datetime.now().isoformat(),
        "message": f"Task {task_id} assigned to {staff_id}"
    }

def complete_housekeeping_task(
    task_id: str,
    staff_id: str,
    inspection_passed: Optional[bool] = None,
    notes: Optional[str] = None
) -> Dict[str, Any]:
    """
    Mark task as completed.

    Args:
        task_id: Task identifier
        staff_id: Staff member completing task
        inspection_passed: If inspection was required
        notes: Completion notes

    Returns:
        Completion confirmation
    """
    logger.info(f"Completing task {task_id}")

    completion_time = datetime.now()
    duration_minutes = 25  # Simulated task duration

    return {
        "status": "success",
        "task_id": task_id,
        "completed_by": staff_id,
        "completed_at": completion_time.isoformat(),
        "duration_minutes": duration_minutes,
        "inspection_passed": inspection_passed,
        "notes": notes,
        "message": f"Task {task_id} completed"
    }

def get_daily_housekeeping_plan(
    date: str,
    property_id: str = "prop_001"
) -> Dict[str, Any]:
    """
    Generate daily housekeeping plan.

    Args:
        date: Plan date (YYYY-MM-DD)
        property_id: Property identifier

    Returns:
        Daily housekeeping plan
    """
    logger.info(f"Generating housekeeping plan for {date}")

    # Simulated plan generation
    # In production, would analyze arrivals, departures, stayovers

    tasks = [
        {
            "task_id": "hk_001",
            "room": "201",
            "type": "checkout_clean",
            "priority": "high",
            "due_time": "14:00",
            "assigned_to": "staff_01",
            "guest_arrival": "15:00"
        },
        {
            "task_id": "hk_002",
            "room": "305",
            "type": "stayover_clean",
            "priority": "normal",
            "due_time": "16:00",
            "assigned_to": "staff_02",
            "guest_preference": "afternoon"
        },
        {
            "task_id": "hk_003",
            "room": "412",
            "type": "checkout_clean",
            "priority": "vip",
            "due_time": "13:00",
            "assigned_to": "staff_03",
            "inspection_required": True
        }
    ]

    staff_assignments = {
        "staff_01": {"name": "Maria", "room_count": 12, "tasks": ["hk_001"]},
        "staff_02": {"name": "John", "room_count": 11, "tasks": ["hk_002"]},
        "staff_03": {"name": "Sarah", "room_count": 10, "tasks": ["hk_003"]}
    }

    return {
        "status": "success",
        "date": date,
        "property_id": property_id,
        "tasks": tasks,
        "total_tasks": len(tasks),
        "checkout_cleans": 2,
        "stayover_cleans": 1,
        "deep_cleans": 0,
        "staff_assignments": staff_assignments,
        "total_staff": len(staff_assignments),
        "estimated_completion": "16:30",
        "vip_rooms": 1
    }

def rebalance_assignments(
    trigger: str,
    affected_room: Optional[str] = None
) -> Dict[str, Any]:
    """
    Rebalance staff assignments due to changes.

    Args:
        trigger: Reason for rebalance (early_checkin, late_checkout, etc.)
        affected_room: Room affected by change

    Returns:
        Rebalanced assignments
    """
    logger.info(f"Rebalancing assignments due to {trigger}")

    changes = []

    if trigger == "early_checkin" and affected_room:
        changes.append({
            "room": affected_room,
            "previous_time": "14:00",
            "new_time": "12:00",
            "reassigned_to": "staff_03",
            "reason": "Rush clean for early check-in"
        })
    elif trigger == "late_checkout" and affected_room:
        changes.append({
            "room": affected_room,
            "previous_time": "11:00",
            "new_time": "14:00",
            "reassigned_to": "staff_02",
            "reason": "Late checkout approved"
        })

    return {
        "status": "success",
        "trigger": trigger,
        "affected_room": affected_room,
        "changes": changes,
        "change_count": len(changes),
        "rebalanced_at": datetime.now().isoformat(),
        "message": f"Assignments rebalanced due to {trigger}"
    }

def get_room_cleaning_status(room_id: str) -> Dict[str, Any]:
    """
    Get current cleaning status of a room.

    Args:
        room_id: Room identifier

    Returns:
        Room cleaning status
    """
    # Simulated status
    import random
    statuses = ["clean", "dirty", "cleaning", "inspecting"]
    status = random.choice(statuses)

    result = {
        "status": "success",
        "room_id": room_id,
        "room_number": f"R{room_id[-3:]}",
        "cleaning_status": status,
        "last_cleaned": (datetime.now() - timedelta(hours=2)).isoformat(),
        "assigned_to": "staff_01" if status == "cleaning" else None
    }

    if status == "cleaning":
        result["estimated_completion"] = (datetime.now() + timedelta(minutes=15)).isoformat()

    return result

def schedule_inspection(
    room_id: str,
    inspection_type: str = "routine",
    inspector_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Schedule room inspection.

    Args:
        room_id: Room to inspect
        inspection_type: Type of inspection
        inspector_id: Optional specific inspector

    Returns:
        Inspection schedule confirmation
    """
    logger.info(f"Scheduling {inspection_type} inspection for room {room_id}")

    inspection_id = f"insp_{datetime.now().timestamp()}"

    return {
        "status": "success",
        "inspection_id": inspection_id,
        "room_id": room_id,
        "inspection_type": inspection_type,
        "scheduled_for": (datetime.now() + timedelta(minutes=30)).isoformat(),
        "inspector_id": inspector_id or "supervisor_01",
        "message": f"Inspection scheduled for room {room_id}"
    }

def create_maintenance_ticket(
    room_id: str,
    issue: str,
    severity: str = "low",
    details: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create maintenance ticket.

    Args:
        room_id: Affected room
        issue: Issue description
        severity: Issue severity (low, medium, high, urgent)
        details: Additional details

    Returns:
        Ticket creation confirmation
    """
    logger.info(f"Creating maintenance ticket for room {room_id}: {issue}")

    ticket_id = f"mnt_{datetime.now().timestamp()}"

    # Determine SLA based on severity
    sla_hours = {
        "urgent": 2,
        "high": 8,
        "medium": 24,
        "low": 48
    }

    sla_target = datetime.now() + timedelta(hours=sla_hours.get(severity, 24))

    # Determine if room should be blocked
    block_room = severity in ["urgent", "high"]

    return {
        "status": "success",
        "ticket_id": ticket_id,
        "room_id": room_id,
        "issue": issue,
        "severity": severity,
        "details": details,
        "sla_target": sla_target.isoformat(),
        "room_blocked": block_room,
        "created_at": datetime.now().isoformat(),
        "message": f"Maintenance ticket {ticket_id} created"
    }

def get_housekeeping_metrics(
    date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get housekeeping performance metrics.

    Args:
        date: Optional specific date

    Returns:
        Housekeeping metrics
    """
    target_date = date or datetime.now().date().isoformat()

    return {
        "status": "success",
        "date": target_date,
        "metrics": {
            "total_rooms_cleaned": 45,
            "average_clean_time": 24.5,  # minutes
            "rush_cleans": 3,
            "inspections_passed": 8,
            "inspections_failed": 1,
            "staff_efficiency": 0.92,  # 92%
            "guest_satisfaction": 4.6  # out of 5
        },
        "staff_performance": [
            {"staff_id": "staff_01", "rooms_cleaned": 16, "avg_time": 23.2},
            {"staff_id": "staff_02", "rooms_cleaned": 15, "avg_time": 25.1},
            {"staff_id": "staff_03", "rooms_cleaned": 14, "avg_time": 24.8}
        ],
        "issues": [
            {"room": "305", "issue": "Extra cleaning required", "time_impact": 10}
        ]
    }