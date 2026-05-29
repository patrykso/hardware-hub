# Hardware Hub - MCP Server

This is the standalone MCP (Model Context Protocol) server for the Hardware Hub. It provides AI clients like Claude Desktop with read-only access to the database to perform inventory analysis and provide audits.

## Setup

```bash
cd mcp_server
uv sync
```

## Running the Server

Make sure to set the `DB_PATH` in `.env` to point to the backend's `hub.db`.

```bash
uv run python server.py
```

## Claude Desktop Configuration

Add the following to your `claude_desktop_config.json`:

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
