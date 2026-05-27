<!-- This file contains architectural and business context of the project. -->

# Hub Rental System — Agent Specification

> This document is the authoritative reference for any LLM agent working on this codebase.
> Read it fully before writing or modifying any code. All decisions here were made deliberately.

---

## What This Project Is

An internal hardware rental management system. Employees can browse and rent physical equipment (phones, laptops, etc.). Admins manage inventory and user accounts. An AI layer provides an on-demand inventory audit. The system is a REST API (FastAPI) consumed by a Vue 3 SPA.

---

## Hard Constraints

- Backend: Python, FastAPI
- Frontend: Vue 3 + Vite (SPA, no SSR)
- Database: SQLite, accessed via SQLAlchemy ORM. One `.db` file on disk.
- No Alembic (schema is stable; use `create_all()` on startup)
- LLM abstraction: LiteLLM (supports Ollama locally, cloud providers in production)
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
│   │   │   ├── users.py
│   │   │   └── audit.py
│   │   ├── services/
│   │   │   ├── rental_service.py   # All rental business logic and guards
│   │   │   └── audit_service.py    # LLM audit logic
│   │   ├── core/
│   │   │   ├── config.py      # Settings via pydantic-settings / env vars
│   │   │   └── security.py    # JWT creation, verification, password hashing
│   │   └── seed.py            # Loads initial_data.json into DB (idempotent)
│   ├── tests/
│   │   ├── conftest.py        # Test DB setup, fixtures, test client
│   │   └── test_rental_engine.py
│   ├── pyproject.toml
│   └── hub.db                 # gitignored
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
|----------------|-------------|--------------------------------------------|
| `id`           | Integer, PK | Auto-increment                             |
| `name`         | String      | e.g. "Apple iPhone 13 Pro Max"             |
| `brand`        | String      | e.g. "Apple"                               |
| `purchase_date`| Date        | ISO 8601 string in seed JSON               |
| `status`       | Enum        | `Available` \| `InUse` \| `Repair`         |

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

| Method | Path                   | Auth       | Description                                       |
|--------|------------------------|------------|---------------------------------------------------|
| GET    | `/equipment`           | Any user   | List all equipment. Supports query params: `status`, `brand`, `sort_by`, `order` |
| POST   | `/equipment`           | Admin only | Create new equipment item                         |
| PATCH  | `/equipment/{id}`      | Admin only | Update fields (name, brand, purchase_date, status)|
| DELETE | `/equipment/{id}`      | Admin only | Delete item (guard: not InUse)                    |

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

### Audit (Admin only)

| Method | Path            | Auth       | Description                              |
|--------|-----------------|------------|------------------------------------------|
| POST   | `/audit/run`    | Admin only | Triggers LLM inventory audit, returns report |

---

## Auth Implementation (`app/core/security.py`)

- Password hashing: `passlib` with bcrypt scheme
- JWT: `python-jose` with HS256 algorithm
- Token payload: `{ "sub": username, "is_admin": bool, "exp": timestamp }`
- Token expiry: configurable via env, default 8 hours
- Dependency: FastAPI `Depends(get_current_user)` injects the current user into routes
- Admin guard: separate dependency `Depends(get_current_admin_user)` — raises 403 if not admin

---

## AI Audit (`app/services/audit_service.py`)

- Triggered by admin via `POST /audit/run`
- Fetches all equipment rows + all rental rows from DB
- Constructs a structured prompt including full inventory snapshot and rental history summary
- Sends to LLM via LiteLLM
- LLM provider and model selected via environment variables (`LLM_PROVIDER`, `LLM_MODEL`)
- Local dev: Ollama (e.g. `ollama/llama3`)
- Production: any LiteLLM-supported provider (e.g. `anthropic/claude-sonnet-4-20250514`)
- Expected LLM output: structured report with flagged issues (items long in Repair, items never rented, items with high rental frequency suggesting wear)
- Response is returned directly to the admin as a text/JSON report — not persisted

---

## Environment Variables (`app/core/config.py`)

Use `pydantic-settings` to load from `.env`:

```
SECRET_KEY=           # JWT signing key (required)
DB_PATH=hub.db        # Path to SQLite file
LLM_PROVIDER=ollama   # or anthropic, openai, etc.
LLM_MODEL=llama3      # model name for LiteLLM
CORS_ORIGINS=http://localhost:5173   # comma-separated
```

---

## Seed Script (`app/seed.py`)

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

## Testing (`tests/`)

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
