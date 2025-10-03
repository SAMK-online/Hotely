"""
Messaging and Communication Tools
==================================
Tools for guest communication via SMS, WhatsApp, email, and voice.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
from hotelpilot.models.data_models import MessageChannel

logger = logging.getLogger(__name__)

def send_sms(
    to_number: str,
    message: str,
    reservation_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Send SMS message to guest.

    Args:
        to_number: Recipient phone number
        message: Message content
        reservation_id: Associated reservation

    Returns:
        Send confirmation
    """
    logger.info(f"Sending SMS to {to_number}")

    # Check quiet hours (9 PM - 8 AM)
    current_hour = datetime.now().hour
    if 21 <= current_hour or current_hour < 8:
        return {
            "status": "blocked",
            "reason": "quiet_hours",
            "message": "Message blocked due to quiet hours (9 PM - 8 AM)"
        }

    # Simulated SMS send
    message_id = f"sms_{datetime.now().timestamp()}"

    return {
        "status": "success",
        "message_id": message_id,
        "to": to_number,
        "channel": "sms",
        "delivered": True,
        "reservation_id": reservation_id,
        "sent_at": datetime.now().isoformat(),
        "message": "SMS sent successfully"
    }

def send_whatsapp(
    to_number: str,
    message: str,
    template: Optional[str] = None,
    media_url: Optional[str] = None,
    reservation_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Send WhatsApp message to guest.

    Args:
        to_number: Recipient WhatsApp number
        message: Message content
        template: Optional template name
        media_url: Optional media attachment
        reservation_id: Associated reservation

    Returns:
        Send confirmation
    """
    logger.info(f"Sending WhatsApp to {to_number}")

    # Check quiet hours
    current_hour = datetime.now().hour
    if 21 <= current_hour or current_hour < 8:
        return {
            "status": "blocked",
            "reason": "quiet_hours",
            "message": "Message blocked due to quiet hours"
        }

    message_id = f"wa_{datetime.now().timestamp()}"

    return {
        "status": "success",
        "message_id": message_id,
        "to": to_number,
        "channel": "whatsapp",
        "template": template,
        "has_media": media_url is not None,
        "delivered": True,
        "read": False,
        "reservation_id": reservation_id,
        "sent_at": datetime.now().isoformat(),
        "message": "WhatsApp message sent successfully"
    }

def send_email(
    to_email: str,
    subject: str,
    body: str,
    html_body: Optional[str] = None,
    attachments: Optional[List[str]] = None,
    reservation_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Send email to guest.

    Args:
        to_email: Recipient email
        subject: Email subject
        body: Plain text body
        html_body: Optional HTML body
        attachments: Optional attachment URLs
        reservation_id: Associated reservation

    Returns:
        Send confirmation
    """
    logger.info(f"Sending email to {to_email}: {subject}")

    message_id = f"email_{datetime.now().timestamp()}"

    return {
        "status": "success",
        "message_id": message_id,
        "to": to_email,
        "channel": "email",
        "subject": subject,
        "has_html": html_body is not None,
        "attachment_count": len(attachments) if attachments else 0,
        "delivered": True,
        "opened": False,
        "reservation_id": reservation_id,
        "sent_at": datetime.now().isoformat(),
        "message": "Email sent successfully"
    }

def start_voice_call(
    to_number: str,
    script: str,
    intents: List[str],
    language: str = "en",
    reservation_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Initiate outbound voice call.

    Args:
        to_number: Recipient phone number
        script: Call script/flow
        intents: Supported intents for the call
        language: Call language
        reservation_id: Associated reservation

    Returns:
        Call initiation result
    """
    logger.info(f"Initiating voice call to {to_number}")

    # Check quiet hours
    current_hour = datetime.now().hour
    if 21 <= current_hour or current_hour < 8:
        return {
            "status": "blocked",
            "reason": "quiet_hours",
            "message": "Call blocked due to quiet hours"
        }

    call_id = f"call_{datetime.now().timestamp()}"

    return {
        "status": "success",
        "call_id": call_id,
        "to": to_number,
        "channel": "voice",
        "language": language,
        "supported_intents": intents,
        "reservation_id": reservation_id,
        "initiated_at": datetime.now().isoformat(),
        "message": "Call initiated successfully"
    }

def detect_language(text: str) -> Dict[str, Any]:
    """
    Detect language of incoming message.

    Args:
        text: Message text

    Returns:
        Detected language
    """
    # Simplified language detection
    # In production, would use proper NLP service

    if any(word in text.lower() for word in ["hola", "gracias", "por favor"]):
        language = "es"
    elif any(word in text.lower() for word in ["bonjour", "merci", "s'il vous"]):
        language = "fr"
    else:
        language = "en"

    return {
        "status": "success",
        "detected_language": language,
        "confidence": 0.85,
        "text_sample": text[:100]
    }

def analyze_sentiment(text: str) -> Dict[str, Any]:
    """
    Analyze sentiment of guest message.

    Args:
        text: Message text

    Returns:
        Sentiment analysis results
    """
    # Simplified sentiment analysis
    # In production, would use proper NLP service

    negative_words = ["terrible", "awful", "bad", "horrible", "worst", "disappointed"]
    positive_words = ["excellent", "great", "wonderful", "amazing", "best", "fantastic"]

    text_lower = text.lower()
    negative_count = sum(1 for word in negative_words if word in text_lower)
    positive_count = sum(1 for word in positive_words if word in text_lower)

    if negative_count > positive_count:
        sentiment = "negative"
        score = -0.7
    elif positive_count > negative_count:
        sentiment = "positive"
        score = 0.8
    else:
        sentiment = "neutral"
        score = 0.0

    return {
        "status": "success",
        "sentiment": sentiment,
        "score": score,  # -1.0 to 1.0
        "confidence": 0.75,
        "requires_attention": sentiment == "negative"
    }

def classify_intent(text: str) -> Dict[str, Any]:
    """
    Classify intent of incoming message.

    Args:
        text: Message text

    Returns:
        Intent classification
    """
    # Simplified intent classification
    # In production, would use proper NLP service

    text_lower = text.lower()

    intents = {
        "booking": ["book", "reservation", "availability", "reserve"],
        "modify": ["change", "modify", "update", "reschedule"],
        "cancel": ["cancel", "cancellation", "refund"],
        "check_in": ["check in", "checkin", "arrival", "early check"],
        "check_out": ["check out", "checkout", "late checkout", "departure"],
        "payment": ["pay", "payment", "bill", "charge", "invoice"],
        "amenity": ["wifi", "breakfast", "gym", "pool", "parking"],
        "complaint": ["complaint", "problem", "issue", "broken", "not working"],
        "info": ["what time", "where", "how", "when", "directions"]
    }

    detected_intent = "general"
    max_confidence = 0.3

    for intent, keywords in intents.items():
        matches = sum(1 for keyword in keywords if keyword in text_lower)
        confidence = matches / len(keywords)

        if confidence > max_confidence:
            detected_intent = intent
            max_confidence = confidence

    return {
        "status": "success",
        "intent": detected_intent,
        "confidence": min(max_confidence * 2, 1.0),  # Scale up confidence
        "requires_human": max_confidence < 0.4,
        "text_sample": text[:100]
    }

def generate_response(
    intent: str,
    context: Dict[str, Any],
    language: str = "en"
) -> Dict[str, Any]:
    """
    Generate appropriate response based on intent.

    Args:
        intent: Detected intent
        context: Conversation context
        language: Response language

    Returns:
        Generated response
    """
    # Response templates by intent
    templates = {
        "booking": "I'd be happy to help you with a reservation. May I have your check-in and check-out dates?",
        "modify": "I can help you modify your reservation. Please provide your confirmation number.",
        "cancel": "I understand you'd like to cancel. Please provide your confirmation number to proceed.",
        "check_in": "Welcome! Our standard check-in time is 3 PM. Would you like to request early check-in?",
        "check_out": "Check-out time is 11 AM. Would you like to request late check-out for an additional fee?",
        "payment": "I can help with payment. Would you like me to send you a secure payment link?",
        "amenity": "I'd be happy to help with amenity information. What would you like to know about?",
        "complaint": "I apologize for the inconvenience. Let me connect you with our team to resolve this immediately.",
        "info": "I'd be happy to provide that information. What specifically would you like to know?",
        "general": "Thank you for contacting us. How may I assist you today?"
    }

    response = templates.get(intent, templates["general"])

    # Translate if needed (simplified)
    if language == "es":
        response = "¡Hola! ¿En qué puedo ayudarle hoy?"
    elif language == "fr":
        response = "Bonjour! Comment puis-je vous aider aujourd'hui?"

    return {
        "status": "success",
        "response": response,
        "intent": intent,
        "language": language,
        "requires_followup": intent in ["booking", "modify", "cancel", "complaint"]
    }

def check_message_frequency(
    guest_id: str,
    channel: str,
    window_hours: int = 24
) -> Dict[str, Any]:
    """
    Check if guest has reached message frequency cap.

    Args:
        guest_id: Guest identifier
        channel: Message channel
        window_hours: Time window to check

    Returns:
        Frequency check result
    """
    # Simulated frequency check
    # In production, would check actual message history

    message_count = 2  # Simulated count
    frequency_cap = 3

    return {
        "status": "success",
        "guest_id": guest_id,
        "channel": channel,
        "message_count": message_count,
        "frequency_cap": frequency_cap,
        "can_send": message_count < frequency_cap,
        "window_hours": window_hours,
        "next_available": (datetime.now() + timedelta(hours=4)).isoformat() if message_count >= frequency_cap else None
    }