"""
Payment Integration Tools
=========================
Tools for handling payments, billing, and revenue recovery.
"""

from typing import Dict, Optional, Any
from datetime import datetime, timedelta
import logging
import secrets
from hotelpilot.models.data_models import Payment, PaymentStatus

logger = logging.getLogger(__name__)

def create_payment_link(
    amount: float,
    reservation_id: str,
    guest_email: str,
    description: Optional[str] = None,
    expires_in_hours: int = 48
) -> Dict[str, Any]:
    """
    Create a secure payment link for guest.

    Args:
        amount: Payment amount
        reservation_id: Associated reservation
        guest_email: Guest email for notification
        description: Payment description
        expires_in_hours: Link expiration time

    Returns:
        Payment link details
    """
    logger.info(f"Creating payment link for ${amount} - reservation {reservation_id}")

    # Generate secure payment link (simulated)
    link_id = f"pl_{secrets.token_urlsafe(8)}"
    link_url = f"https://pay.hotelpilot.com/{link_id}"
    expires_at = datetime.now() + timedelta(hours=expires_in_hours)

    return {
        "status": "success",
        "link_id": link_id,
        "url": link_url,
        "amount": amount,
        "currency": "USD",
        "reservation_id": reservation_id,
        "description": description or f"Payment for reservation {reservation_id}",
        "expires_at": expires_at.isoformat(),
        "sent_to": guest_email,
        "message": f"Payment link created and sent to {guest_email}"
    }

def process_payment(
    amount: float,
    payment_method: str,
    reservation_id: str,
    guest_id: str,
    capture: bool = True
) -> Dict[str, Any]:
    """
    Process a payment transaction.

    Args:
        amount: Payment amount
        payment_method: Payment method ID or token
        reservation_id: Associated reservation
        guest_id: Guest identifier
        capture: Whether to capture immediately

    Returns:
        Transaction result
    """
    logger.info(f"Processing payment of ${amount} for reservation {reservation_id}")

    # Simulated payment processing
    success_rate = 0.85  # 85% success rate for simulation
    import random

    if random.random() < success_rate:
        transaction_id = f"txn_{secrets.token_hex(8)}"
        status = PaymentStatus.CAPTURED if capture else PaymentStatus.AUTHORIZED

        return {
            "status": "success",
            "transaction_id": transaction_id,
            "amount": amount,
            "currency": "USD",
            "payment_status": status.value,
            "reservation_id": reservation_id,
            "last_four": "4242",
            "brand": "Visa",
            "captured": capture,
            "created_at": datetime.now().isoformat(),
            "message": f"Payment {'captured' if capture else 'authorized'} successfully"
        }
    else:
        # Payment failed
        failure_codes = ["insufficient_funds", "card_declined", "expired_card", "incorrect_cvc"]
        failure_code = random.choice(failure_codes)

        return {
            "status": "error",
            "error_code": failure_code,
            "error_message": get_failure_message(failure_code),
            "amount": amount,
            "reservation_id": reservation_id,
            "retry_eligible": failure_code != "expired_card",
            "message": "Payment failed"
        }

def capture_authorization(
    authorization_id: str,
    amount: Optional[float] = None
) -> Dict[str, Any]:
    """
    Capture a previously authorized payment.

    Args:
        authorization_id: Authorization transaction ID
        amount: Optional partial capture amount

    Returns:
        Capture result
    """
    logger.info(f"Capturing authorization {authorization_id}")

    return {
        "status": "success",
        "authorization_id": authorization_id,
        "capture_id": f"cap_{secrets.token_hex(8)}",
        "amount": amount or 150.00,  # Would fetch from authorization
        "captured_at": datetime.now().isoformat(),
        "message": "Authorization captured successfully"
    }

def refund_payment(
    transaction_id: str,
    amount: Optional[float] = None,
    reason: Optional[str] = None
) -> Dict[str, Any]:
    """
    Refund a payment transaction.

    Args:
        transaction_id: Original transaction ID
        amount: Optional partial refund amount
        reason: Refund reason

    Returns:
        Refund result
    """
    logger.info(f"Processing refund for transaction {transaction_id}")

    refund_id = f"ref_{secrets.token_hex(8)}"

    return {
        "status": "success",
        "refund_id": refund_id,
        "transaction_id": transaction_id,
        "amount": amount or 150.00,  # Would fetch from transaction
        "reason": reason or "Guest requested refund",
        "processed_at": datetime.now().isoformat(),
        "message": "Refund processed successfully"
    }

def check_payment_status(payment_id: str) -> Dict[str, Any]:
    """
    Check status of a payment or payment link.

    Args:
        payment_id: Payment or link ID

    Returns:
        Payment status information
    """
    # Simulated status check
    return {
        "status": "success",
        "payment_id": payment_id,
        "payment_status": "captured",
        "amount": 150.00,
        "currency": "USD",
        "last_updated": datetime.now().isoformat(),
        "attempts": 1,
        "last_four": "4242"
    }

def retry_failed_payment(
    payment_id: str,
    new_method: Optional[str] = None
) -> Dict[str, Any]:
    """
    Retry a failed payment with smart scheduling.

    Args:
        payment_id: Failed payment ID
        new_method: Optional new payment method

    Returns:
        Retry result
    """
    logger.info(f"Retrying payment {payment_id}")

    # Smart retry logic based on failure code
    # In production, this would check the failure code and apply appropriate retry strategy

    return process_payment(
        amount=150.00,  # Would fetch from original
        payment_method=new_method or "pm_original",
        reservation_id="res_123",
        guest_id="g_456",
        capture=True
    )

def generate_3ds_challenge(
    payment_method: str,
    amount: float
) -> Dict[str, Any]:
    """
    Generate 3D Secure challenge for payment.

    Args:
        payment_method: Payment method
        amount: Transaction amount

    Returns:
        3DS challenge details
    """
    challenge_id = f"3ds_{secrets.token_hex(8)}"
    challenge_url = f"https://secure.hotelpilot.com/3ds/{challenge_id}"

    return {
        "status": "requires_action",
        "action": "3ds_challenge",
        "challenge_id": challenge_id,
        "challenge_url": challenge_url,
        "amount": amount,
        "expires_in": 600,  # 10 minutes
        "message": "3D Secure verification required"
    }

def get_payment_recovery_candidates(
    days_back: int = 7,
    min_amount: float = 50.0
) -> Dict[str, Any]:
    """
    Get list of failed payments eligible for recovery.

    Args:
        days_back: How many days to look back
        min_amount: Minimum amount threshold

    Returns:
        List of recovery candidates
    """
    # Simulated data
    candidates = [
        {
            "payment_id": "pay_001",
            "reservation_id": "res_001",
            "guest_email": "john@example.com",
            "amount": 189.00,
            "failed_at": (datetime.now() - timedelta(days=1)).isoformat(),
            "failure_code": "insufficient_funds",
            "retry_count": 1
        },
        {
            "payment_id": "pay_002",
            "reservation_id": "res_002",
            "guest_email": "sarah@example.com",
            "amount": 299.00,
            "failed_at": (datetime.now() - timedelta(days=2)).isoformat(),
            "failure_code": "card_declined",
            "retry_count": 0
        }
    ]

    total_recoverable = sum(c["amount"] for c in candidates)

    return {
        "status": "success",
        "candidates": candidates,
        "total_candidates": len(candidates),
        "total_recoverable": total_recoverable,
        "recovery_rate_estimate": 0.65,  # 65% historical recovery rate
        "message": f"Found {len(candidates)} payments eligible for recovery"
    }

def get_failure_message(code: str) -> str:
    """Get human-readable failure message."""
    messages = {
        "insufficient_funds": "Insufficient funds in account",
        "card_declined": "Card was declined by issuer",
        "expired_card": "Card has expired",
        "incorrect_cvc": "Security code is incorrect",
        "processing_error": "Error processing payment"
    }
    return messages.get(code, "Payment could not be processed")