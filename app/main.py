from fastapi import FastAPI, HTTPException
from app.models import ModelContextRequest, ModelContextResponse
from app.tools import get_weather_tool_schema, get_weather


# Create the FastAPI app instance
app = FastAPI(
    title="MCP Server",
    description="Model Context Protocol Server for tool discovery and execution",
    version="1.0.0"
)

# Create the tool_registry dictionary
tool_registry = {
    get_weather_tool_schema.name: {
        "schema": get_weather_tool_schema,
        "function": get_weather
    }
}


@app.get("/")
async def root():
    """Root endpoint returning server information."""
    return {
        "name": "MCP Server",
        "version": "1.0.0",
        "description": "Model Context Protocol Server for tool discovery and execution"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/mcp", response_model=ModelContextResponse)
async def handle_mcp_request(request: ModelContextRequest) -> ModelContextResponse:
    """
    Main MCP endpoint for tool discovery and execution.

    Supports two methods:
    - 'discover': Returns list of available tools
    - 'execute': Executes a specific tool by name
    """
    response_id = request.id

    try:
        # Discovery handler - return list of available tools
        if request.method == "discover":
            tools = [
                {
                    "name": tool_data["schema"].name,
                    "description": tool_data["schema"].description,
                    "input_schema": tool_data["schema"].input_schema
                }
                for tool_data in tool_registry.values()
            ]
            return ModelContextResponse(
                id=response_id,
                result={"tools": tools}
            )

        # Execution handler - execute a specific tool
        elif request.method == "execute":
            if not request.params or "tool_name" not in request.params:
                raise HTTPException(
                    status_code=400,
                    detail="Missing 'tool_name' in parameters"
                )

            tool_name = request.params["tool_name"]
            tool_args = request.params.get("arguments", {})

            # Check if tool exists in registry
            if tool_name not in tool_registry:
                raise HTTPException(
                    status_code=404,
                    detail=f"Tool '{tool_name}' not found. Use 'discover' to see available tools."
                )

            # Execute the tool function
            tool_func = tool_registry[tool_name]["function"]
            result = await tool_func(**tool_args)

            return ModelContextResponse(
                id=response_id,
                result={"output": result}
            )

        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown method '{request.method}'. Use 'discover' or 'execute'."
            )

    except HTTPException:
        raise
    except Exception as e:
        return ModelContextResponse(
            id=response_id,
            error={
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)