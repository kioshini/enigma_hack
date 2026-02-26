"""
Read-only Email API routes.

NO create/update/delete endpoints exposed.
All data comes exclusively from the email ingestion pipeline.
"""

import csv
import io
from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.database import get_db
from app.models import Email
from app.schemas import EmailOut, EmailListResponse, StatsResponse

router = APIRouter(prefix="/api/v1/emails", tags=["emails"])

VALID_STATUSES = {"NEW", "PROCESSED", "NEEDS_OPERATOR", "ESCALATED", "CLOSED"}


@router.get("", response_model=EmailListResponse)
def list_emails(
    status: Optional[str] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search in sender/subject"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """List emails with optional filtering. Read-only."""
    query = db.query(Email)

    if status and status.upper() in VALID_STATUSES:
        query = query.filter(Email.status == status.upper())

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Email.sender.ilike(search_pattern)) |
            (Email.subject.ilike(search_pattern))
        )

    total = query.count()
    emails = query.order_by(desc(Email.created_at)).offset(offset).limit(limit).all()

    return EmailListResponse(
        emails=[EmailOut.model_validate(e) for e in emails],
        total=total,
    )


@router.get("/stats", response_model=StatsResponse)
def get_stats(db: Session = Depends(get_db)):
    """Get email statistics by status."""
    total = db.query(func.count(Email.id)).scalar() or 0

    counts = {}
    for s in VALID_STATUSES:
        counts[s.lower()] = (
            db.query(func.count(Email.id))
            .filter(Email.status == s)
            .scalar() or 0
        )

    return StatsResponse(
        total=total,
        new=counts.get("new", 0),
        processed=counts.get("processed", 0),
        needs_operator=counts.get("needs_operator", 0),
        escalated=counts.get("escalated", 0),
        closed=counts.get("closed", 0),
    )


@router.get("/{email_id}", response_model=EmailOut)
def get_email(email_id: str, db: Session = Depends(get_db)):
    """Get a single email by ID. Read-only."""
    email_record = db.query(Email).filter(Email.id == email_id).first()
    if not email_record:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Email not found")
    return EmailOut.model_validate(email_record)


@router.get("/export/csv")
def export_csv(
    status: Optional[str] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search filter"),
    db: Session = Depends(get_db),
):
    """Export filtered emails as CSV."""
    query = db.query(Email)

    if status and status.upper() in VALID_STATUSES:
        query = query.filter(Email.status == status.upper())

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Email.sender.ilike(search_pattern)) |
            (Email.subject.ilike(search_pattern))
        )

    emails = query.order_by(desc(Email.created_at)).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "ID", "Sender", "Subject", "Status", "Complexity",
        "Sentiment", "Confidence", "AI Response", "Created At"
    ])

    for e in emails:
        writer.writerow([
            str(e.id), e.sender, e.subject, e.status,
            e.complexity or "", e.sentiment or "",
            e.confidence or "", e.ai_response or "",
            e.created_at.isoformat() if e.created_at else "",
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=emails_export.csv"},
    )
