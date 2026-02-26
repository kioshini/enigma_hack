"""
ML Service Mock.

Simulates an ML model that analyzes email text and returns
complexity, sentiment, confidence, and a suggested response.

This module is designed to be replaced with a real LLM integration later.
"""

import random
import hashlib
from app.schemas import MLAnalysisResponse

# Keywords that signal negative sentiment
NEGATIVE_KEYWORDS = [
    "angry", "furious", "terrible", "worst", "hate", "disgusting",
    "unacceptable", "fraud", "scam", "lawsuit", "lawyer", "refund",
    "complaint", "disappointed", "horrible", "awful", "broken",
    "не работает", "ужасно", "верните деньги", "жалоба", "обман",
    "разочарован", "отвратительно", "кошмар", "безобразие",
]

# Keywords that signal high complexity
COMPLEX_KEYWORDS = [
    "integration", "api", "multiple", "enterprise", "migration",
    "compliance", "security", "breach", "urgent", "critical",
    "escalate", "manager", "legal", "contract", "sla",
    "интеграция", "миграция", "безопасность", "критично", "срочно",
    "руководство", "договор", "юридический",
]

# Positive keywords
POSITIVE_KEYWORDS = [
    "thank", "thanks", "great", "excellent", "awesome", "love",
    "amazing", "wonderful", "helpful", "good", "best",
    "спасибо", "отлично", "замечательно", "прекрасно", "хорошо",
]

RESPONSE_TEMPLATES = {
    ("low", "positive"): "Thank you for your kind feedback! We're glad we could help. Is there anything else we can assist you with?",
    ("low", "neutral"): "Thank you for reaching out. We've reviewed your request and here's what we suggest: please check our FAQ section for quick answers, or reply to this email for further assistance.",
    ("low", "negative"): "We're sorry to hear about your experience. We take your feedback seriously and would like to resolve this issue. A support agent will follow up within 24 hours.",
    ("high", "positive"): "Thank you for your detailed message. Due to the complexity of your request, we've assigned a specialist to review it. You'll receive a response within 48 hours.",
    ("high", "neutral"): "We've received your request which requires additional review from our technical team. A specialist will be assigned to your case shortly.",
    ("high", "negative"): "We sincerely apologize for the inconvenience. Your case has been escalated to our senior support team for immediate attention. Expect a response within 12 hours.",
}


def _deterministic_random(text: str, seed_suffix: str = "") -> float:
    """Generate a deterministic 'random' float based on text hash."""
    h = hashlib.md5((text + seed_suffix).encode()).hexdigest()
    return int(h[:8], 16) / 0xFFFFFFFF


def analyze_email(text: str) -> MLAnalysisResponse:
    """
    Mock ML analysis of email text.

    In production, this would call an LLM API (OpenAI, Claude, etc.)
    or a custom trained model.
    """
    text_lower = text.lower()

    # Determine sentiment
    neg_score = sum(1 for kw in NEGATIVE_KEYWORDS if kw in text_lower)
    pos_score = sum(1 for kw in POSITIVE_KEYWORDS if kw in text_lower)

    if neg_score > pos_score:
        sentiment = "negative"
    elif pos_score > neg_score:
        sentiment = "positive"
    else:
        sentiment = "neutral"

    # Determine complexity
    complex_score = sum(1 for kw in COMPLEX_KEYWORDS if kw in text_lower)
    word_count = len(text.split())

    if complex_score >= 2 or word_count > 200:
        complexity = "high"
    elif complex_score == 1 or word_count > 100:
        # Use deterministic randomness for borderline cases
        if _deterministic_random(text, "complexity") > 0.5:
            complexity = "high"
        else:
            complexity = "low"
    else:
        complexity = "low"

    # Confidence based on clarity of signals
    base_confidence = 0.7
    signal_strength = abs(neg_score - pos_score) + complex_score
    confidence = min(0.99, base_confidence + signal_strength * 0.05)
    # Add slight deterministic variation
    confidence += (_deterministic_random(text, "confidence") - 0.5) * 0.1
    confidence = round(max(0.5, min(0.99, confidence)), 2)

    # Get suggested response
    suggested_response = RESPONSE_TEMPLATES.get(
        (complexity, sentiment),
        "Thank you for contacting us. Your request is being reviewed."
    )

    return MLAnalysisResponse(
        complexity=complexity,
        sentiment=sentiment,
        confidence=confidence,
        suggested_response=suggested_response,
    )
