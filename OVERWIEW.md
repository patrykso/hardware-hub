<!-- This file contains project overview -->

# Hub Rental System — Project Overview

An internal tool for managing and renting physical hardware (phones, laptops, etc.) within a company. Employees browse available gear and check it out. Admins manage inventory, user accounts, and can run an AI-powered audit of the equipment state.

Estimated build time: ~6 hours with AI assistance.

---

## Tech Stack

| Layer      | Technology                                      |
|------------|-------------------------------------------------|
| Backend    | Python, FastAPI                                 |
| Frontend   | Vue 3, Vite (Single Page App)                   |
| Database   | SQLite (single `.db` file), SQLAlchemy ORM      |
| Auth       | JWT (Bearer tokens), passlib + python-jose      |
| AI         | LiteLLM (Ollama locally, cloud LLM in production) |
| Testing    | pytest                                          |
| Packages   | uv                                              |

**Why these choices:**

- **FastAPI over Django:** The frontend is a Vue SPA that talks to a pure JSON API. Django's built-in features (templating, admin panel) don't help here. FastAPI is async-native, which matters for LLM calls that can take seconds. It also auto-generates OpenAPI docs.
- **SQLite over a document store:** The data is relational (rentals link users to equipment). SQLite is a real database in a single file — it supports transactions, foreign keys, and querying. If the system outgrows it, switching to PostgreSQL via SQLAlchemy is a config change.
- **LiteLLM:** Provides a unified interface for talking to Ollama (local), Claude, GPT-4o, or Gemini. Swapping providers is a one-line env var change.
- **No Alembic (for now):** The schema is stable. SQLAlchemy's `create_all()` creates tables on startup. If the schema needs to change in a way that affects existing data, add Alembic at that point.

---

## How the App Works

### Roles

There are two roles: **Admin** and **User**.

- Users cannot create their own accounts. Only an Admin can create accounts.
- A default Admin account is seeded on first startup.

### Equipment Status

Every piece of hardware is always in one of three states:

```
Available → (user rents) → InUse → (user returns) → Available
Available / InUse → (admin sets) → Repair → (admin sets) → Available
```

The system enforces that these transitions are the only valid ones.

### Rental Flow

1. User logs in.
2. Browses the dashboard — sees all equipment with name, brand, purchase date, and status. Can sort and filter.
3. Clicks "Rent" on an Available item → status becomes InUse.
4. When done, returns it → status becomes Available again.

Guards prevent impossible actions: renting something that's broken, returning someone else's gear, etc.

### Admin Panel

- Add / remove equipment items
- Toggle any item's Repair status
- Create new user accounts
- Run the AI Inventory Audit

### AI Inventory Audit

Admin-only feature. Clicking "Run Audit" sends the full inventory snapshot and rental history to an LLM. The LLM returns a plain-language report flagging potential issues, for example:

- Items that have been stuck in Repair for an unusually long time
- Items that have never been rented (potentially redundant)
- Items rented very frequently (may be showing wear)

This runs on-demand and takes a few seconds. The result is displayed in the admin panel but not saved to the database.

---

## Project Structure (high level)

```
hub-rental/
├── backend/          # FastAPI app
│   ├── app/
│   │   ├── models/   # SQLAlchemy DB models
│   │   ├── schemas/  # Pydantic request/response shapes
│   │   ├── routers/  # HTTP route definitions (thin layer)
│   │   ├── services/ # Business logic (rental guards, AI audit)
│   │   └── core/     # Config, JWT/auth utilities
│   ├── tests/
│   └── seed.py       # Loads initial 11 equipment records from JSON
├── frontend/         # Vue 3 SPA
│   └── src/
│       ├── views/    # LoginView, DashboardView, AdminView
│       ├── stores/   # Pinia (auth, equipment state)
│       └── api/      # Axios instance + per-resource API calls
└── data/
    └── initial_data.json   # Source data (11 equipment records)
```

---

## Running Locally

### Backend

```bash
cd backend
uv sync
cp .env.example .env      # fill in SECRET_KEY, Ollama model, etc.
uv run uvicorn app.main:app --reload
```

On startup: tables are created, seed data is loaded (idempotent), default admin account is created if absent.

API docs available at: `http://localhost:8000/docs`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Runs on `http://localhost:5173`. Talks to the backend at `localhost:8000`.

### Environment Variables (backend `.env`)

```
SECRET_KEY=your-secret-key-here
DB_PATH=hub.db
LLM_PROVIDER=ollama
LLM_MODEL=llama3
CORS_ORIGINS=http://localhost:5173
```

For production, change `LLM_PROVIDER` and `LLM_MODEL` to your cloud provider.

---

## Testing

```bash
cd backend
uv run pytest
```

Tests use an isolated in-memory SQLite database — they never touch `hub.db`.

The three critical tests that must always pass:

| Test | What it checks |
|------|---------------|
| `test_cannot_rent_equipment_in_repair` | Renting a broken item is rejected |
| `test_cannot_rent_equipment_already_in_use` | Renting an already-rented item is rejected |
| `test_cannot_return_other_users_rental` | Returning someone else's rental is rejected |

---

## Deployment

Two independent units to deploy:

- **Backend:** Any host that supports a persistent filesystem and a long-running Python process. Good options: VPS (Hetzner, DigitalOcean), Fly.io, Railway, Render. Vercel is not suitable (serverless functions can't persist a SQLite file).
- **Frontend:** Build with `npm run build`, serve the `dist/` folder from the same VPS (via nginx) or a static host like Vercel.

CORS: the backend must have the frontend's production URL in `CORS_ORIGINS`.

---

## What's Not in Scope (v1)

- Email notifications
- Rental history visible to regular users (only admins see full history in v1)
- Reservation / booking ahead of time
- Equipment categories or tags
- Semantic search (potential v2 AI feature)
- Chat assistant (potential v2 AI feature)
