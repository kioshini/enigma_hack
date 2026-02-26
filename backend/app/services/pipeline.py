"""
Pipeline service.

Orchestrates the flow: Email → ML analysis → Status assignment → DB update.
Business logic for status determination lives here, NOT in ML service.
"""

import logging
from sqlalchemy.orm import Session
from app.models import Email
from app.services.ml_service import analyze_email

logger = logging.getLogger(__name__)


def determine_status(complexity: str, sentiment: str) -> str:
    """
    Business logic for status determination.

    Rules:
      - sentiment == 'negative' → ESCALATED (highest priority)
      - complexity == 'high' → NEEDS_OPERATOR
      - complexity == 'low' → PROCESSED
    """
    if sentiment == "negative":
        return "ESCALATED"
    if complexity == "high":
        return "NEEDS_OPERATOR"
    return "PROCESSED"


def process_email(db: Session, email: Email) -> Email:
    """
    Run full processing pipeline on a single email.

    1. Send email body to ML service (mock)
    2. Apply business logic to determine status
    3. Update email record in database
    """
    try:
        text = f"Subject: {email.subject or ''}\n\n{email.body or ''}"
        analysis = analyze_email(text)

        status = determine_status(analysis.complexity, analysis.sentiment)

        email.complexity = analysis.complexity
        email.sentiment = analysis.sentiment
        email.confidence = analysis.confidence
        email.ai_response = analysis.suggested_response
        email.status = status

        db.commit()
        db.refresh(email)

        logger.info(
            f"Email {email.id} processed: status={status}, "
            f"complexity={analysis.complexity}, sentiment={analysis.sentiment}, "
            f"confidence={analysis.confidence}"
        )

    except Exception as e:
        logger.error(f"Failed to process email {email.id}: {e}")
        db.rollback()
        raise

    return email
