"""
Email AI Support System — Backend Entry Point.

Pipeline: Email → Backend (IMAP polling) → ML Service (mock) → DB → Frontend (read-only)
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler

from app.config import get_settings
from app.database import engine, Base
from app.routes.emails import router as emails_router
from app.routes.ml import router as ml_router
from app.services.email_ingestion import poll_mailbox

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)
settings = get_settings()

scheduler = BackgroundScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created.")

    # Start IMAP polling scheduler
    scheduler.add_job(
        poll_mailbox,
        "interval",
        seconds=settings.IMAP_POLL_INTERVAL,
        id="email_poll",
        replace_existing=True,
        max_instances=1,
    )
    scheduler.start()
    logger.info(f"Email polling started (every {settings.IMAP_POLL_INTERVAL}s)")

    yield

    # Shutdown
    scheduler.shutdown(wait=False)
    logger.info("Scheduler stopped.")


app = FastAPI(
    title="Email AI Support System",
    description="AI-powered email support processing pipeline",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Routes
app.include_router(emails_router)
app.include_router(ml_router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "email-ai-backend"}
