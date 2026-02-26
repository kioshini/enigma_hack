"""
Email ingestion service.

Polls an IMAP mailbox at a configurable interval,
downloads new emails, stores them in the database,
and triggers the ML processing pipeline.
"""

import logging
import email as email_lib
from email.header import decode_header
from email.utils import parseaddr
from typing import Optional

from imapclient import IMAPClient
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import SessionLocal
from app.models import Email
from app.services.pipeline import process_email

logger = logging.getLogger(__name__)
settings = get_settings()


def decode_mime_header(header_value: str) -> str:
    """Decode a MIME-encoded email header."""
    if not header_value:
        return ""
    decoded_parts = decode_header(header_value)
    result = []
    for part, charset in decoded_parts:
        if isinstance(part, bytes):
            result.append(part.decode(charset or "utf-8", errors="replace"))
        else:
            result.append(part)
    return " ".join(result)


def extract_body(msg: email_lib.message.Message) -> str:
    """Extract plain text body from an email message."""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition", ""))
            if content_type == "text/plain" and "attachment" not in content_disposition:
                payload = part.get_payload(decode=True)
                if payload:
                    charset = part.get_content_charset() or "utf-8"
                    return payload.decode(charset, errors="replace")
        # Fallback: try to get HTML
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/html":
                payload = part.get_payload(decode=True)
                if payload:
                    charset = part.get_content_charset() or "utf-8"
                    return payload.decode(charset, errors="replace")
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            charset = msg.get_content_charset() or "utf-8"
            return payload.decode(charset, errors="replace")
    return ""


def poll_mailbox():
    """
    Connect to IMAP server, fetch unseen emails, store and process them.
    """
    if not settings.IMAP_EMAIL or not settings.IMAP_PASSWORD:
        logger.warning("IMAP credentials not configured. Skipping email poll.")
        return

    logger.info(f"Polling mailbox: {settings.IMAP_EMAIL} on {settings.IMAP_SERVER}")

    try:
        with IMAPClient(settings.IMAP_SERVER, port=settings.IMAP_PORT, ssl=True) as client:
            client.login(settings.IMAP_EMAIL, settings.IMAP_PASSWORD)
            client.select_folder(settings.IMAP_FOLDER)

            # Search for unseen messages
            messages = client.search(["UNSEEN"])
            logger.info(f"Found {len(messages)} unseen messages")

            if not messages:
                return

            # Fetch messages
            fetched = client.fetch(messages, ["RFC822", "ENVELOPE"])

            db: Session = SessionLocal()
            try:
                for uid, data in fetched.items():
                    try:
                        raw_email = data[b"RFC822"]
                        msg = email_lib.message_from_bytes(raw_email)

                        # Extract message ID for deduplication
                        message_id = msg.get("Message-ID", "")

                        # Check if already exists
                        existing = db.query(Email).filter(
                            Email.message_id == message_id
                        ).first()
                        if existing:
                            logger.debug(f"Skipping duplicate: {message_id}")
                            continue

                        # Parse fields
                        sender_name, sender_addr = parseaddr(msg.get("From", ""))
                        sender = sender_addr or decode_mime_header(msg.get("From", "unknown"))
                        subject = decode_mime_header(msg.get("Subject", "(no subject)"))
                        body = extract_body(msg)

                        # Store in database with status NEW
                        email_record = Email(
                            sender=sender,
                            subject=subject,
                            body=body[:10000],  # Limit body size
                            status="NEW",
                            message_id=message_id,
                        )
                        db.add(email_record)
                        db.commit()
                        db.refresh(email_record)

                        logger.info(f"Stored email {email_record.id} from {sender}: {subject}")

                        # Trigger ML pipeline
                        process_email(db, email_record)

                        # Mark as seen on server
                        client.add_flags([uid], [b"\\Seen"])

                    except Exception as e:
                        logger.error(f"Error processing message UID {uid}: {e}")
                        db.rollback()
                        continue

            finally:
                db.close()

    except Exception as e:
        logger.error(f"IMAP connection failed: {e}")
