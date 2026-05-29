# Hub Rental System

Hub Rental System is an internal hardware management platform that allows employees to browse and rent physical equipment, while providing administrators with tools to track inventory and user accounts. It also includes an AI layer provided as a standalone MCP server for auditing inventory.

## System Architecture

The project consists of three main components:
1. **Frontend**: A Vue 3 Single Page Application (SPA) using Vite. It communicates with the backend via REST APIs.
2. **Backend**: A FastAPI application powered by Python 3.13, using SQLAlchemy to interface with an SQLite database (`hub.db`). It enforces all business logic, handles JWT-based authentication, and manages data seeding.
3. **MCP Server**: A standalone Model Context Protocol server that directly interfaces with the database in read-only mode to provide inventory audits and insights for AI clients (e.g., Claude Desktop).

## Development

- **Backend**: Python (FastAPI, SQLAlchemy, Pytest). Managed via `uv`.
- **Frontend**: JavaScript (Vue 3, Vite, Pinia, Axios). Managed via `npm`.
- **MCP Server**: Python (mcp SDK). Managed via `uv`.

Please see the individual READMEs in each folder (`frontend/`, `backend/`, `mcp_server/`) for setup and development instructions.

## VPS Deployment (Docker Demo)

This project is prepared to be easily deployed to a VPS as a demonstration using Docker Compose. The configuration builds both the backend and frontend, linking them together and exposing the frontend on port 80.

### Prerequisites
- Docker and Docker Compose installed on your VPS.

### Deployment Steps

1. Clone the repository onto your VPS:
   ```bash
   git clone <repository_url> hub-rental
   cd hub-rental
   ```

2. Start the services using Docker Compose:
   ```bash
   docker-compose up -d --build
   ```

3. Access the application:
   - The frontend will be available at `http://<your-vps-ip>`
   - The backend API will be available at `http://<your-vps-ip>:8000/api/v1`

### Data Persistence
The `hub.db` SQLite database is persisted within the `./data` directory mapped to `/app/data` inside the backend container.