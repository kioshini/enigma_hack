import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class Email(Base):
    __tablename__ = "emails"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sender = Column(String(500), nullable=False)
    subject = Column(String(1000), nullable=True, default="")
    body = Column(Text, nullable=True, default="")
    status = Column(String(50), nullable=False, default="NEW")
    complexity = Column(String(50), nullable=True)
    sentiment = Column(String(50), nullable=True)
    ai_response = Column(Text, nullable=True)
    confidence = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    message_id = Column(String(500), nullable=True, unique=True)
