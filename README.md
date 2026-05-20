# MCP Server

![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-E92063?style=for-the-badge&logo=pydantic&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

A Model Context Protocol (MCP) server implementation for tool discovery and execution. This server enables AI models to discover available tools and execute them through a standardized JSON-RPC interface.

## Overview

MCP is a standardized specification that allows AI models and agents to interact with external tools and services in a secure and predictable way. This server implements the discovery and execution patterns that enable AI chatbots to use external tools without embedding tool-specific logic in the AI model itself.

## Features

- **Tool Discovery**: AI can query available tools via the `discover` method
- **Tool Execution**: AI can execute tools via the `execute` method with custom arguments
- **JSON-RPC Protocol**: Standardized request/response format for tool operations
- **Extensible Architecture**: Easy to add new tools to the registry

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Running the Server

```bash
cd app
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Or directly:

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Server information |
| `/health` | GET | Health check endpoint |
| `/mcp` | POST | MCP protocol endpoint |

### MCP Protocol

#### Discovery Request

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "discover",
  "params": {}
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "tools": [
      {
        "name": "get_weather",
        "description": "Get the current weather for a specified location...",
        "input_schema": {...}
      }
    ]
  }
}
```

#### Execution Request

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "execute",
  "params": {
    "tool_name": "get_weather",
    "arguments": {
      "location": "San Francisco",
      "unit": "celsius"
    }
  }
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "output": {
      "location": "San Francisco",
      "temperature": 18.5,
      "unit": "°C",
      "condition": "partly cloudy",
      "humidity": 65,
      "wind_speed": 12,
      "wind_unit": "km/h"
    }
  }
}
```

## Available Tools

### get_weather

Get the current weather for a specified location including temperature, conditions, and humidity.

**Parameters:**
- `location` (string, required): The city name or location to get weather for
- `unit` (string, optional): Temperature unit - 'celsius' or 'fahrenheit' (default: celsius)

## Project Structure

```
mcp-server/
├── .gitignore
├── requirements.txt
├── README.md
└── app/
    ├── __init__.py
    ├── main.py      # FastAPI app with MCP endpoints
    ├── models.py    # Pydantic models for MCP protocol
    └── tools.py     # Tool implementations and schemas
```

## Technology Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **Uvicorn**: Lightning-fast ASGI server
- **Pydantic**: Data validation using Python type annotations
- **Python**: Programming language

## License

MIT License - see LICENSE file for details

## Author

**OumaCavin** - cavin.otieno012@gmail.com

GitHub: [OumaCavin](https://github.com/OumaCavin)