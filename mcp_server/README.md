# Hub Rental MCP Server

A standalone Model Context Protocol (MCP) server that provides read-only tool access to the hardware hub rental database.

## Features

Provides four tools:
- `get_inventory()`: Retrieve all hardware equipment details.
- `get_active_rentals()`: Retrieve all currently active rentals.
- `get_rental_history(equipment_id)`: Retrieve full rental history for an equipment item.
- `audit_inventory()`: Apply deterministic logic to audit inventory state and identify issues.
