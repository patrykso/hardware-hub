# Hardware Hub

Hub Rental System is an internal hardware management platform that allows employees to browse and rent physical equipment, while providing administrators with tools to track inventory and user accounts. It also includes an AI layer provided as a standalone MCP server for auditing inventory.

**Live demo available [here](http://srv41.mikr.us:40155) (doesn't include MCP server).**

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

Project is also prepared to run inside Docker containers. Please take a look at the `docker-compose.yml` file if that is interesting to you.

## AI Development

### Tools 
The tools used to develop this project include:
- Claude,
- Gemini,
- GitHub Copilot,
- Google Antigravity,
- Amazon Kiro,
- Google Stitch,

In early pull requests there are GitHub Copilots reviews visible. The phases developed with Antigravity have `Walkthroughs` attached to the pull requests.

## Features

- admin command center with options to create/remove users, manage hardware equipment, reset database, track rentals, 
- dashboard displaying list of hardware with filtering and sorting support,
- rent/return flow for users,
- super simple mcp server to provide audit features,
- this is not a proper JWT workflow (xss),

## Additional information

Please note that in the root directory that are two files created mainly for LLMs - `OVERVIEW.md` and `AGENTS.md`.

`OVERVIEW.md` was a file created with idea to have a short description of the project in case structured intro was needed for LLM-based chat conversations, but after all wasn't really used. There might be some incosistencies between this file and final project.

`AGENTS.md` are the instructions for AI implementation agents and the foundations of this project. However, some minor inconsistencies might still appear, e. g. at `API Sections` it states that `GET /rentals` returs own rentals, but `Admin sees all` - this is not true and has been overrided during development.