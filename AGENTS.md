<!-- This file contains architectural and business context of the project. -->

# Hub Rental System — Agent Specification

> This document is the authoritative reference for any LLM agent working on this codebase.
> Read it fully before writing or modifying any code. All decisions here were made deliberately.

---

## What This Project Is

An internal hardware rental management system. Employees can browse and rent physical equipment (phones, laptops, etc.). Admins manage inventory and user accounts. An AI layer is provided as a standalone MCP server that connects directly to the database — it is not part of the web application. The web system is a REST API (FastAPI) consumed by a Vue 3 SPA.

---

## Hard Constraints

- Backend: Python, FastAPI
- Frontend: Vue 3 + Vite (SPA, no SSR)
- Database: SQLite, accessed via SQLAlchemy ORM. One `.db` file on disk.
- No Alembic (schema is stable; use `create_all()` on startup)
- MCP server: separate Python package in `mcp_server/`, uses the `mcp` Python SDK, reads `hub.db` directly (read-only)
- No LiteLLM, no LLM calls anywhere in the FastAPI backend
- Package manager: `uv`
- Tests: `pytest`, minimum 3 critical rental-logic tests
- No self-registration. Admin creates all user accounts.
- Auth: JWT (Bearer token). Roles: `admin`, `user`.

---

## Repository Structure

```
hub-rental/
├── backend/
│   ├── app/
│   │   ├── main.py            # App entrypoint, startup, CORS, router registration
│   │   ├── database.py        # SQLAlchemy engine, SessionLocal, Base
│   │   ├── models/
│   │   │   ├── equipment.py
│   │   │   ├── user.py
│   │   │   └── rental.py
│   │   ├── schemas/           # Pydantic request/response models
│   │   │   ├── equipment.py
│   │   │   ├── user.py
│   │   │   └── rental.py
│   │   ├── routers/
│   │   │   ├── auth.py
│   │   │   ├── equipment.py
│   │   │   ├── rentals.py
│   │   │   └── users.py
│   │   ├── services/
│   │   │   └── rental_service.py   # All rental business logic and guards
│   │   └── core/
│   │       ├── config.py      # Settings via pydantic-settings / env vars
│   │       └── security.py    # JWT creation, verification, password hashing
│   ├── seed.py                # Loads initial_data.json into DB (idempotent)
│   ├── tests/
│   │   ├── conftest.py        # Test DB setup, fixtures, test client
│   │   └── test_rental_engine.py
│   └── pyproject.toml
├── mcp_server/
│   ├── server.py              # MCP server entrypoint, tool definitions
│   ├── database.py            # Read-only SQLAlchemy session pointing at hub.db
│   ├── pyproject.toml
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── views/
│   │   │   ├── LoginView.vue
│   │   │   ├── DashboardView.vue
│   │   │   └── AdminView.vue
│   │   ├── components/
│   │   ├── stores/            # Pinia stores (auth, equipment)
│   │   └── api/               # Axios instance + per-resource API modules
│   ├── package.json
│   └── vite.config.js
├── data/
│   └── initial_data.json      # Source of truth for seed data
└── README.md
```

---

## Data Models

### Equipment (SQLAlchemy model: `app/models/equipment.py`)

| Field          | Type        | Notes                                      |
|----------------|-------------|---------------------------------------------|
| `id`           | Integer, PK | Auto-increment                              |
| `name`         | String      | e.g. "Apple iPhone 13 Pro Max"              |
| `brand`        | String      | e.g. "Apple"                                |
| `purchase_date`| Date        | ISO 8601 string in seed JSON                |
| `status`       | Enum        | `Available` \| `InUse` \| `Repair`          |

Status is stored as a Python `Enum` (`EquipmentStatus`). Never store as raw string.

### User (SQLAlchemy model: `app/models/user.py`)

| Field           | Type        | Notes                        |
|-----------------|-------------|------------------------------|
| `id`            | Integer, PK |                              |
| `username`      | String      | Unique                       |
| `password_hash` | String      | bcrypt via passlib           |
| `is_admin`      | Boolean     | Default: False               |
| `created_at`    | DateTime    | UTC                          |

### Rental (SQLAlchemy model: `app/models/rental.py`)

| Field          | Type        | Notes                                |
|----------------|-------------|--------------------------------------|
| `id`           | Integer, PK |                                      |
| `equipment_id` | FK          | → Equipment.id                       |
| `user_id`      | FK          | → User.id                            |
| `rented_at`    | DateTime    | UTC, set on creation                 |
| `returned_at`  | DateTime    | Nullable. Set on return.             |

An open rental (not yet returned) is identified by `returned_at IS NULL`.

---

## Status State Machine

```
Available ──── rent ────► InUse ──── return ────► Available
Available ──── (admin) ──► Repair
InUse ─────── (must return first, then admin) ──► Repair
Repair ─────── (admin) ──► Available
```

Only admins can toggle `Repair`. Users can only trigger `rent` and `return`.

---

## Business Logic Rules (enforce in `rental_service.py`)

All rules raise `HTTPException` with an appropriate 4xx code and a descriptive `detail` string.

1. **Cannot rent if status is not `Available`** → 409
2. **Cannot rent if the equipment already has an open rental** → 409 (defensive, should not occur if rule 1 is enforced, but check anyway)
3. **Cannot return equipment that has no open rental** → 409
4. **Cannot return equipment rented by a different user** (unless admin) → 403
5. **Cannot delete equipment that is currently `InUse`** → 409
6. **Setting status to `Repair` on equipment that is `InUse` is not allowed** — the item must be returned first → 409

These rules are the core of the system. They must be tested.

---

## API Endpoints

All endpoints under `/api/v1/`. Auth via `Authorization: Bearer <token>` header.

### Auth

| Method | Path             | Auth     | Description                          |
|--------|------------------|----------|--------------------------------------|
| POST   | `/auth/login`    | None     | Returns JWT access token             |

Request body: `{ "username": str, "password": str }`
Response: `{ "access_token": str, "token_type": "bearer" }`

### Equipment

| Method | Path                   | Auth       | Description                                        |
|--------|------------------------|------------|----------------------------------------------------|
| GET    | `/equipment`           | Any user   | List all. Query params: `status`, `brand`, `sort_by`, `order` |
| POST   | `/equipment`           | Admin only | Create new equipment item                          |
| PATCH  | `/equipment/{id}`      | Admin only | Update fields (name, brand, purchase_date, status) |
| DELETE | `/equipment/{id}`      | Admin only | Delete item (guard: not InUse)                     |

### Rentals

| Method | Path                      | Auth       | Description                                   |
|--------|---------------------------|------------|-----------------------------------------------|
| POST   | `/rentals`                | Any user   | Rent an item. Body: `{ "equipment_id": int }` |
| POST   | `/rentals/{id}/return`    | Any user   | Return an item (guards apply)                 |
| GET    | `/rentals`                | Any user   | Own rentals. Admin sees all.                  |

### Users (Admin only)

| Method | Path           | Auth       | Description            |
|--------|----------------|------------|------------------------|
| POST   | `/users`       | Admin only | Create a user account  |
| GET    | `/users`       | Admin only | List all users         |

There is no `/audit` endpoint. Audit functionality is exclusively in the MCP server.

---

## Auth Implementation (`app/core/security.py`)

- Password hashing: `passlib` with bcrypt scheme
- JWT: `python-jose` with HS256 algorithm
- Token payload: `{ "sub": username, "is_admin": bool, "exp": timestamp }`
- Token expiry: configurable via env, default 8 hours
- Dependency: FastAPI `Depends(get_current_user)` injects the current user into routes
- Admin guard: separate dependency `Depends(get_current_admin_user)` — raises 403 if not admin

---

## MCP Server (`mcp_server/`)

The MCP server is a **separate Python package** with its own `pyproject.toml`. It is not imported by the FastAPI backend and has no HTTP interface. It is consumed by an MCP-compatible client such as Claude Desktop.

### Purpose

Provides an AI client (Claude Desktop or equivalent) with structured read-only access to the rental system's database. The LLM reasons over the data and generates inventory insights. No LLM calls happen inside the MCP server itself — it only returns data.

### Database Access

- Opens `hub.db` directly via SQLAlchemy in **read-only mode**
- DB path configured via `DB_PATH` environment variable in `mcp_server/.env`
- Uses the same model definitions as the backend (import from a shared location or duplicate minimally — see note below)
- Never writes to the database

> **Note on shared models:** The MCP server and backend share the same `hub.db` schema. To avoid duplication, the MCP server may define its own lightweight SQLAlchemy models mirroring the backend's, rather than importing from the backend package. This keeps the two packages independent.

### Tools

The MCP server exposes four tools:

**`get_inventory()`**
- Returns all equipment rows: id, name, brand, purchase_date, status
- No parameters
- Used by the LLM to get a full picture of current inventory state

**`get_active_rentals()`**
- Returns all rentals where `returned_at IS NULL`
- Each row includes: rental id, equipment name, username of renter, rented_at timestamp
- Used to see what is currently checked out and by whom

**`get_rental_history(equipment_id: int)`**
- Returns all rental records (including returned) for a specific equipment item
- Each row includes: username, rented_at, returned_at (null if still active)
- Used to analyse usage patterns for a specific item

**`audit_inventory()`**
- Applies deterministic business logic to the full inventory and rental history
- No parameters
- Returns a structured list of findings. Each finding contains:
  - `equipment_id`: int
  - `name`: str
  - `issue_type`: one of `long_in_repair` | `never_rented` | `high_rental_frequency` | `long_active_rental`
  - `detail`: human-readable description with concrete data (e.g. "In Repair for 47 days")
  - `severity`: `info` | `warning` | `critical`

Flagging rules (all thresholds are hardcoded constants in `server.py`, easy to adjust):

| issue_type              | Condition                                                      | Severity   |
|-------------------------|----------------------------------------------------------------|------------|
| `long_in_repair`        | Status is `Repair` and no rental activity for > 30 days       | `warning`  |
| `never_rented`          | No rental record exists for this item at all                   | `info`     |
| `high_rental_frequency` | Total completed rentals > 10                                   | `info`     |
| `long_active_rental`    | Open rental (returned_at IS NULL) has been open for > 14 days | `warning`  |

If no issues are found, returns an empty list — not an error.

The LLM receives these pre-computed findings and narrates them to the admin. It does not need to discover issues itself; its role is to summarise, contextualise, and answer follow-up questions.

### Running the MCP Server

```bash
cd mcp_server
uv sync
cp .env.example .env   # set DB_PATH to absolute path of hub.db
uv run python server.py
```

### Claude Desktop Configuration

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "hub-rental": {
      "command": "uv",
      "args": ["--directory", "/absolute/path/to/hub-rental/mcp_server", "run", "python", "server.py"]
    }
  }
}
```

### Environment Variables (`mcp_server/.env`)

```
DB_PATH=/absolute/path/to/hub-rental/backend/hub.db
```

---

## Environment Variables (`backend/app/core/config.py`)

Use `pydantic-settings` to load from `.env`:

```
SECRET_KEY=           # JWT signing key (required)
DB_PATH=hub.db        # Path to SQLite file
CORS_ORIGINS=http://localhost:5173   # comma-separated
```

There are no LLM-related environment variables in the backend.

---

## Seed Script (`backend/seed.py`)

- Reads `data/initial_data.json`
- Inserts records into `equipment` table only if the table is empty (idempotent)
- JSON field `purchaseDate` maps to DB column `purchase_date`
- Called once on startup via FastAPI `lifespan` event (after `create_all()`)
- Also creates a default admin user if no admin exists (credentials from env or hardcoded default for dev)

Initial JSON record shape:
```json
{ "id": 1, "name": "Apple iPhone 13 Pro Max", "brand": "Apple", "purchaseDate": "2021-11-23", "status": "Available" }
```

---

## Testing (`backend/tests/`)

Framework: `pytest`. Use FastAPI's `TestClient` with an in-memory SQLite DB (separate from production DB).

`conftest.py` must:
- Create a fresh in-memory SQLite DB per test session
- Provide a seeded admin user and a seeded regular user
- Provide a seeded equipment item in each relevant status
- Provide authenticated test client fixtures for both roles

### Required Critical Tests (minimum)

File: `tests/test_rental_engine.py`

1. **`test_cannot_rent_equipment_in_repair`** — attempt to rent an item with status `Repair`, expect 409
2. **`test_cannot_rent_equipment_already_in_use`** — attempt to rent an item with status `InUse`, expect 409
3. **`test_cannot_return_other_users_rental`** — user B attempts to return an item rented by user A, expect 403

Additional tests encouraged:
- `test_successful_rent_changes_status_to_in_use`
- `test_successful_return_changes_status_to_available`
- `test_admin_can_toggle_repair_status`
- `test_non_admin_cannot_create_user`

The MCP server tools are pure database reads and can be tested by calling the tool functions directly with a test in-memory DB — no MCP protocol required.

---

## Conventions

- All datetime values stored and returned in UTC ISO 8601
- Use Pydantic schemas for all request validation and response serialization — never return SQLAlchemy model objects directly
- Router files contain only routing logic. Business logic lives in `services/`
- `HTTPException` is raised in service layer, not in routers
- Frontend API calls go through a centralized Axios instance in `src/api/` that attaches the JWT header automatically
- Vue state management: Pinia (auth store holds token and user info; equipment store holds inventory)

---

## What This Project Is NOT

- Not a public-facing application. No SEO, no SSR.
- Not a multi-tenant system.
- Not a full accounting/asset management system. No depreciation, cost tracking, or procurement workflow.
- Not a real-time system. No WebSockets.
- The MCP server is not a web service. It has no HTTP endpoints and is not deployed to a server.