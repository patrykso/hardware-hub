# Hardware Hub - Backend

This is the FastAPI backend for the Hardware Hub equipment management system.

## Features
- REST API for equipment and rental management.
- JWT-based authentication.
- SQLite database via SQLAlchemy.
- Configurable environments for dev/prod.

## Development Setup

```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload --port 8000
```

## Running Tests

Tests are executed with pytest:
```bash
uv run pytest
```

## Environment Variables

The backend accepts the following environment variables (defined in `app/core/config.py`):
- `ENV`: Environment mode (defaults to `prod`). When set to `dev`, dev credentials and secrets are used if not provided.
- `SECRET_KEY`: Used to sign JWTs (Required in `prod`).
- `DB_PATH`: Path to the SQLite database (defaults to `hub.db`).
- `ADMIN_USERNAME`: Initial admin username (Required in `prod`).
- `ADMIN_PASSWORD`: Initial admin password (Required in `prod`).
- `CORS_ORIGINS`: Comma-separated list of allowed CORS origins.
