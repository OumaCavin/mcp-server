"""
MCP Server - Model Context Protocol Server for Tool Discovery and Execution

This module implements the main FastAPI application that handles MCP protocol requests.
It provides endpoints for tool discovery and tool execution following the JSON-RPC 2.0 specification.

Author: OumaCavin
"""

from fastapi import FastAPI, HTTPException
from app.models import ModelContextRequest, ModelContextResponse
from app.tools import get_weather_tool_schema, get_weather


# =============================================================================
# FastAPI Application Instance
# =============================================================================

# Create the FastAPI app instance with metadata for documentation
# The title, description, and version appear in the auto-generated API docs
app = FastAPI(
    title="MCP Server",
    description="Model Context Protocol Server for tool discovery and execution",
    version="1.0.0"
)


# =============================================================================
# Tool Registry
# =============================================================================

# The tool_registry is a dictionary that stores all available tools.
# Each tool is registered with:
#   - 'schema': The Tool model containing metadata (name, description, input schema)
#   - 'function': The actual async function to execute when the tool is called
#
# To add a new tool:
#   1. Create the tool function in app/tools.py
#   2. Define the tool schema (input_schema) in app/tools.py
#   3. Register the tool here by adding it to this dictionary

tool_registry = {
    get_weather_tool_schema.name: {
        "schema": get_weather_tool_schema,
        "function": get_weather
    }
}


# =============================================================================
# API Endpoints
# =============================================================================

@app.get("/")
async def root():
    """
    Root endpoint returning server information.

    This endpoint provides basic information about the MCP server
    including its name, version, and purpose.

    Returns:
        dict: Server metadata including name, version, and description
    """
    return {
        "name": "MCP Server",
        "version": "1.0.0",
        "description": "Model Context Protocol Server for tool discovery and execution"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring.

    This endpoint is used by load balancers and monitoring systems
    to verify that the server is running and responsive.

    Returns:
        dict: Health status indicator
    """
    return {"status": "healthy"}


# =============================================================================
# MCP Protocol Handler
# =============================================================================

@app.post("/mcp", response_model=ModelContextResponse)
async def handle_mcp_request(request: ModelContextRequest) -> ModelContextResponse:
    """
    Main MCP endpoint for tool discovery and execution.

    This endpoint handles all MCP protocol operations including:
    - 'discover': Returns a list of all available tools with their schemas
    - 'execute': Executes a specified tool with given arguments

    The request and response follow the JSON-RPC 2.0 specification.

    Args:
        request: The MCP request containing method and parameters

    Returns:
        ModelContextResponse: The response containing tool list or execution result

    Raises:
        HTTPException: 400 for invalid requests or unknown methods
        HTTPException: 404 if the requested tool does not exist
    """
    # Extract the request ID for response correlation
    # The ID allows the client to match responses with their requests
    response_id = request.id

    try:
        # =====================================================================
        # Handle 'discover' Method
        # =====================================================================
        # The discover method returns a list of all tools registered in the
        # tool_registry along with their metadata (name, description, schema)

        if request.method == "discover":
            # Build the tool list by extracting metadata from each registered tool
            tools = [
                {
                    "name": tool_data["schema"].name,
                    "description": tool_data["schema"].description,
                    "input_schema": tool_data["schema"].input_schema
                }
                for tool_data in tool_registry.values()
            ]

            # Return the tool list in a JSON-RPC 2.0 compliant response
            return ModelContextResponse(
                id=response_id,
                result={"tools": tools}
            )

        # =====================================================================
        # Handle 'execute' Method
        # =====================================================================
        # The execute method runs a specific tool with provided arguments

        elif request.method == "execute":
            # Validate that required parameters are present
            if not request.params or "tool_name" not in request.params:
                raise HTTPException(
                    status_code=400,
                    detail="Missing 'tool_name' in parameters"
                )

            # Extract the tool name and arguments from the request
            tool_name = request.params["tool_name"]
            tool_args = request.params.get("arguments", {})

            # Check if the requested tool exists in our registry
            if tool_name not in tool_registry:
                raise HTTPException(
                    status_code=404,
                    detail=f"Tool '{tool_name}' not found. Use 'discover' to see available tools."
                )

            # Retrieve the tool function from the registry
            tool_func = tool_registry[tool_name]["function"]

            # Execute the tool function with the provided arguments
            # Using **tool_args to unpack the arguments dictionary as keyword arguments
            result = await tool_func(**tool_args)

            # Return the execution result in a JSON-RPC 2.0 compliant response
            return ModelContextResponse(
                id=response_id,
                result={"output": result}
            )

        # =====================================================================
        # Handle Unknown Methods
        # =====================================================================
        # If the method is neither 'discover' nor 'execute', return an error

        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown method '{request.method}'. Use 'discover' or 'execute'."
            )

    # Re-raise HTTP exceptions (they contain important status codes)
    except HTTPException:
        raise

    # Catch all other exceptions and return them as JSON-RPC errors
    # This prevents the server from crashing and provides useful error info
    except Exception as e:
        return ModelContextResponse(
            id=response_id,
            error={
                "code": -32603,  # JSON-RPC internal error code
                "message": f"Internal error: {str(e)}"
            }
        )


# =============================================================================
# Application Entry Point
# =============================================================================

# This allows running the server directly with: python app/main.py
# For development, prefer: uvicorn app.main:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)