# Hardware Hub

Hub Rental System is an internal hardware management platform that allows employees to browse and rent physical equipment, while providing administrators with tools to track inventory and user accounts. It also includes an AI layer provided as a standalone MCP server for auditing inventory.

Live demo available [here](http://srv41.mikr.us:40155) (doesn't include MCP server).

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
- Claude chat - for architectural design and consultations,
- Gemini chat - for consultations,
- GitHub Copilot - for early PR reviews (but then I ran out of weekly limit..) and agentic AI development mainly both of backend and frontend at beginning of the project.
- Google Antigravity - as main implementation agent,
- Amazon Kiro - mainly for frontend tweaks and polishing,
- Google Stitch - to develop frontend layout drafts.

### Prompt trail

Chat with Claude about architecture [here](https://claude.ai/share/fb9056d3-0336-4acd-9dc7-ab5ca13dedf3)

Google Stitch project [here](https://stitch.withgoogle.com/projects/4808263333780882634)

In early pull requests there are GitHub Copilots reviews visible. The phases developed with Antigravity have `Walkthroughs` attached to the pull requests.

### Correction of AI

There were `some` cases in which AI provided suboptimal, buggy or insecure solutions. There is a `slight` chance that I haven't notice all of them. In general I've had a plan to make use of Github Copilot pull request reviews, but that quickly stopped working as I ran out of my weekly limits.

I remind myself two main situations in which I've though to myself "OK, this might be a problem":
- unclean seed - I haven't notice this at first and only realized during development - I was rather suprised that Claude didn't mention it during architecture talk. I've guided the AI on how to deal with these cases, mainly by introducing `ERROR` status,
- I've decided to implement AI equipment auditing tool, but at first I wanted it to be integrated within the project - just during development it came to me that simple MCP server might be a better idea for now. LLMs never mentioned nor suggest this, so I've had to modify already existing project specification at rather late stage.

## Data strategy

The initial dataset is included in `data/initial_data.json`.
To be fair - at first I didn't notice the issues with seed (e. g. duplicated ID, wrong date format) - I guess I just wasn't expecting it - lesson learnt. I think one of the AI reviews noticed data format issue and then I decided to double check the data, finding more inconsistencies. In general, the `bad` records are marked with `ERROR` status and are to be resolved by admin. In a current state, additional information like "notes" or "history" are stored in a database, but not used. This is something to think about in future development - as of right now there are lot of empty data in these columns (relational database) which might become a problem. One idea might be to utilize a NoSQL database, but that comes with different issues as well. The project doesn't utilize migrations which is something that obviously should be introduced at one point.

## Implementation status & Trade-offs

● Inventory Auditor: An AI-driven check that flags potential issues in the current
inventory based on all available information -->

### ✅ Fully Implemented

- admin Command Center, but currently, the admin can only see HIS/HERS rentals in `Rentals` view - there should probably be a different dedicated view for all the rentals,
- smart dashboard displaying list of hardware with filtering and sorting support. 
- rent/return flow.

### ⚡ Shortcuts & Hacks

All of stated below are mainly not fixed because of the time limit. Can't guarentee there are not more issues I haven't picked up during the development of this project as I slightly.. underestimated the needed time effort.

- core logic is ok, but not perfect - e. g. there is a possibility for state mismatch in database - user can rent a hardware that is later manually set to `Available` by admin,
- inventory auditor -  mcp server to provide audit features works, but needs more polishing - eg. there is only `get_rental_history` that takes single id as parameter,
- database handling should be better - e. g. introduce migrations and fix the a `lot of empty space` issue,
- this is not a proper JWT workflow,
- better handling of error state - for now it just signals there's an issue with the record,
- finding seed path is forgiving as quick-fix to docker related issues,
- introduce better initial credentials handling, currently the separation between for dev and prod deployments is bad.

### ⚠ Partial / Missing

- ai assistant inside the web-app (Audit view),
- better filtering,
- maybe make the frontend look more concise and adjust the color pallette,
- better documentation inside codebase and make sure the current `.md` documents are up-to-date.

### 🔮 Next Steps

As there is still a lot of things to polish, resolving some of the shortcuts and known issues should be top priority, so the project could be use in real environment:

- improve the rental core logic to cover issue with admin manually changing in-use state,
- create the proper JWT flow so that the project can be safely deployed,
- introduce better database handling, migrations and resolve the issue with empty columns,

another thing I would consider important business requirement that wasn't stated in original requirements explicitly:
- create a view for admin to see and manage rentals (hardware to user) as I consider this important business requirement that wasn't really stated in original requirements.

In general this project isn't as polish as I originally planned and is currently in a state of MVP, but as I said before - I've underestimated the time limits.

## Additional information

Please note that in the root directory that are two files created mainly for LLMs - `OVERVIEW.md` and `AGENTS.md`.

`OVERVIEW.md` was a file created with idea to have a short description of the project in case structured intro was needed for LLM-based chat conversations, but after all wasn't really used. There might be some incosistencies between this file and final project.

`AGENTS.md` are the instructions for AI implementation agents and the foundations of this project. However, some minor inconsistencies might still appear, e. g. at `API Sections` it states that `GET /rentals` returs own rentals, but `Admin sees all` - this is not true and has been overrided during development.