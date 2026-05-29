<!-- This file contains project overview -->

# Hub Rental System — Project Overview

An internal tool for managing and renting physical hardware (phones, laptops, etc.) within a company. Employees browse available gear and check it out. Admins manage inventory and user accounts. An AI layer is provided as a standalone MCP server that gives Claude Desktop (or any MCP-compatible client) structured read-only access to the database for inventory analysis.

Estimated build time: ~6 hours with AI assistance.

---

## Tech Stack

| Layer        | Technology                                      |
|--------------|-------------------------------------------------|
| Backend      | Python, FastAPI                                 |
| Frontend     | Vue 3, Vite (Single Page App)                   |
| Database     | SQLite (single `.db` file), SQLAlchemy ORM      |
| Auth         | JWT (Bearer tokens), passlib + python-jose      |
| AI           | MCP server (Python `mcp` SDK), Claude Desktop   |
| Testing      | pytest                                          |
| Packages     | uv                                              |

**Why these choices:**

- **FastAPI over Django:** The frontend is a Vue SPA that talks to a pure JSON API. FastAPI is async-native and auto-generates OpenAPI docs, which is useful when working with AI agents on the codebase.
- **SQLite over a document store:** The data is relational (rentals link users to equipment). SQLite is a real database in a single file — transactions, foreign keys, querying. If the system outgrows it, switching to PostgreSQL via SQLAlchemy is a config change.
- **MCP server over in-app LLM calls:** Rather than embedding LLM calls inside the web app, the AI layer is a separate MCP server. An admin connects to it via Claude Desktop and queries the inventory through natural language. The LLM reasoning happens in the client — the MCP server only returns structured data. This means no LLM dependencies in the web app at all.
- **No Alembic (for now):** The schema is stable. SQLAlchemy's `create_all()` creates tables on startup. Add Alembic if the schema needs to change in a way that affects existing data.

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

Guards prevent impossible actions: renting something in Repair, returning someone else's gear, etc.

### Admin Panel

- Add / remove equipment items
- Toggle any item's Repair status
- Create new user accounts

### AI Inventory Audit (via MCP)

This does not live in the web app. An admin opens **Claude Desktop** with the MCP server configured and interacts with the inventory through natural language.

The MCP server exposes an `audit_inventory()` tool that applies deterministic logic to the current data and returns a structured list of flagged issues — items stuck in Repair too long, items never rented, items with unusually long active rentals, and high-frequency items that may be showing wear. Claude receives these pre-computed findings and presents them as a report. The admin can then ask follow-up questions, and Claude can call the other tools (`get_inventory`, `get_active_rentals`, `get_rental_history`) to dig deeper.

Example session:

> "Run an audit" → Claude calls `audit_inventory()`, reports 3 findings
> "Which one has been in Repair longest?" → Claude calls `get_rental_history(id)` to check
> "Are there any items that have never been used at all?" → Claude already has this from the audit findings

---

## Project Structure

```
hub-rental/
├── backend/                  # FastAPI app
│   ├── app/
│   │   ├── models/           # SQLAlchemy DB models
│   │   ├── schemas/          # Pydantic request/response shapes
│   │   ├── routers/          # HTTP route definitions (thin layer)
│   │   ├── services/         # Business logic (rental guards)
│   │   └── core/             # Config, JWT/auth utilities
│   ├── seed.py               # Loads initial 11 equipment records from JSON
│   └── tests/
├── mcp_server/               # Standalone MCP server (separate package)
│   ├── server.py             # Tool definitions, MCP entrypoint
│   └── database.py           # Read-only SQLAlchemy access to hub.db
├── frontend/                 # Vue 3 SPA
│   └── src/
│       ├── views/            # LoginView, DashboardView, AdminView
│       ├── stores/           # Pinia (auth, equipment state)
│       └── api/              # Axios instance + per-resource API calls
└── data/
    └── initial_data.json     # Source data (11 equipment records)
```

---

## Running Locally

### Backend

```bash
cd backend
uv sync
cp .env.example .env      # fill in SECRET_KEY
uv run uvicorn app.main:app --reload
```

On startup: tables are created, seed data is loaded (idempotent), default admin account is created if absent.

API docs: `http://localhost:8000/docs`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Runs on `http://localhost:5173`. Talks to the backend at `localhost:8000`.

### MCP Server

```bash
cd mcp_server
uv sync
cp .env.example .env      # set DB_PATH to absolute path of hub.db
uv run python server.py
```

Then add to your `claude_desktop_config.json`:

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

### Backend Environment Variables (`.env`)

```
SECRET_KEY=your-secret-key-here
DB_PATH=hub.db
CORS_ORIGINS=http://localhost:5173
```

### MCP Server Environment Variables (`mcp_server/.env`)

```
DB_PATH=/absolute/path/to/hub-rental/backend/hub.db
```

---

## Testing

```bash
cd backend
uv run pytest
```

Tests use an isolated in-memory SQLite database — they never touch `hub.db`.

The three critical tests that must always pass:

| Test | What it checks |
|------|----------------|
| `test_cannot_rent_equipment_in_repair` | Renting a broken item is rejected |
| `test_cannot_rent_equipment_already_in_use` | Renting an already-rented item is rejected |
| `test_cannot_return_other_users_rental` | Returning someone else's rental is rejected |

---

## Deployment

Three independent units:

- **Backend:** Any host with a persistent filesystem and a long-running Python process. VPS (Hetzner, DigitalOcean), Fly.io, Railway, or Render. Vercel is not suitable (serverless functions cannot persist a SQLite file to disk).
- **Frontend:** Build with `npm run build`, serve the `dist/` folder from the same VPS via nginx, or from a static host like Vercel.
- **MCP server:** Runs locally on the admin's machine. It is not a web service and is not deployed to a server. It reads `hub.db` directly, so it needs network or local access to wherever the database file lives.

CORS: the backend must have the frontend's production URL in `CORS_ORIGINS`.

---

## What's Not in Scope (v1)

- Email notifications
- Rental history visible to regular users (admins see full history via MCP)
- Reservation / booking ahead of time
- Equipment categories or tags
- Semantic search in the web UI (potential v2 feature)
- Chat interface in the web UI (the MCP server covers this use case outside the app)