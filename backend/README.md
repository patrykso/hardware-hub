# Hub Rental — Backend

FastAPI REST API for the hardware rental system.

## Setup

```bash
cd backend
cp .env.example .env   # optional; defaults work for local dev
uv sync
```

## Run

```bash
uv run uvicorn app.main:app --reload
```

Health check: `GET http://127.0.0.1:8000/health`
