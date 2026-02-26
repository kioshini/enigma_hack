# Email AI Support System

AI-powered email support processing pipeline.

```
Email → Backend (IMAP polling) → ML Service (mock) → PostgreSQL → Frontend (read-only)
```

## Architecture

| Service    | Tech                  | Port  | Role                              |
|------------|-----------------------|-------|-----------------------------------|
| backend    | FastAPI (Python 3.11) | 8000  | IMAP ingestion, ML mock, REST API |
| postgres   | PostgreSQL 16         | 5432  | Data storage                      |
| frontend   | React + Vite + TS     | 3000  | Read-only dashboard               |

## Quick Start

### 1. Clone & configure

```bash
cp .env.example .env
```

Edit `.env` and set your IMAP credentials:

```env
IMAP_SERVER=imap.gmail.com
IMAP_PORT=993
IMAP_EMAIL=your-email@gmail.com
IMAP_PASSWORD=your-app-password
IMAP_FOLDER=INBOX
```

> **Gmail**: use [App Passwords](https://support.google.com/accounts/answer/185833) (enable 2FA first).

### 2. Run

```bash
docker-compose up --build
```

### 3. Access

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## How It Works

1. **Email Ingestion** — Backend polls IMAP mailbox every 30 seconds
2. **Storage** — New emails are saved to PostgreSQL with status `NEW`
3. **ML Analysis** — Each email is sent to the ML mock service for classification
4. **Status Assignment** (business logic):
   - `sentiment = negative` → **ESCALATED**
   - `complexity = high` → **NEEDS_OPERATOR**
   - `complexity = low` → **PROCESSED**
5. **Frontend** — Read-only dashboard auto-refreshes every 5 seconds

## API Endpoints

| Method | Endpoint                  | Description              |
|--------|---------------------------|--------------------------|
| GET    | `/api/v1/emails`          | List emails (filterable) |
| GET    | `/api/v1/emails/stats`    | Status statistics        |
| GET    | `/api/v1/emails/{id}`     | Single email detail      |
| GET    | `/api/v1/emails/export/csv` | CSV export (filtered)  |
| POST   | `/api/v1/ml/analyze`      | ML analysis endpoint     |
| GET    | `/health`                 | Health check             |

> **No POST/PUT/DELETE for emails** — data comes only from IMAP pipeline.

## Frontend Features

- Color-coded rows by status (green/yellow/red/grey)
- Status filter buttons with counters
- Search by sender/subject
- CSV export (respects active filters)
- Auto-refresh every 5 seconds
- **No create/edit/delete buttons** — read-only by design

## Project Structure

```
hackaton/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app + scheduler
│   │   ├── config.py            # Settings from ENV
│   │   ├── database.py          # SQLAlchemy engine
│   │   ├── models.py            # Email ORM model
│   │   ├── schemas.py           # Pydantic schemas
│   │   ├── routes/
│   │   │   ├── emails.py        # Read-only email API
│   │   │   └── ml.py            # ML analysis endpoint
│   │   └── services/
│   │       ├── email_ingestion.py  # IMAP polling
│   │       ├── ml_service.py       # ML mock (replaceable)
│   │       └── pipeline.py         # Processing pipeline
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── api.ts
│   │   ├── types.ts
│   │   ├── index.css
│   │   └── components/
│   │       ├── EmailTable.tsx
│   │       ├── StatusFilter.tsx
│   │       └── ExportButton.tsx
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
├── .env
└── README.md
```

## Replacing ML Mock with Real LLM

The ML mock is isolated in `backend/app/services/ml_service.py`. To integrate a real model:

1. Replace `analyze_email()` function in `ml_service.py`
2. Or extract as a separate container and update `ML_SERVICE_URL` in `.env`
3. The `POST /api/v1/ml/analyze` interface stays the same

Expected response format:
```json
{
  "complexity": "low | high",
  "sentiment": "positive | neutral | negative",
  "confidence": 0.85,
  "suggested_response": "..."
}
```
