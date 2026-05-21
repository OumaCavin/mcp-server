# Task 2.1 - Import FastAPI
# Make sure HTTPException is imported alongside FastAPI
from fastapi import FastAPI, HTTPException

# Task 3.2 - Import request and response models from app.models
from app.models import ModelContextRequest, ModelContextResponse

# Task 4.3 - Import the tool schema from app.tools
from app.tools import GET_WEATHER_TOOL

# Task 5.1 - Import the tool function from app.tools
from app.tools import get_weather

# Task 2.1 - Create the FastAPI app instance
app = FastAPI(title="MCP Server Lab")

# Task 5.1 - Create the tool_registry dictionary
tool_registry = {
    'get_weather': get_weather
}

# Task 2.2 - Create the /mcp POST endpoint
@app.post("/mcp", response_model=ModelContextResponse)
async def handle_mcp_request(request: ModelContextRequest):
    
    # --- Task 4.3: Discovery Handler ---
    if request.verb == 'discovery':
        return ModelContextResponse(
            tools=[GET_WEATHER_TOOL]
        )

    # --- Task 5.2 & 6.1: Execution Handler with Error Handling ---
    elif request.verb == 'execute':
        # 2. Wrap your tool execution logic in a try...except block
        try:
            # 3. In the try block, attempt to look up the tool in the tool_registry
            selected_function = tool_registry[request.tool_name]
            
            # Call the tool and store the output
            tool_output = selected_function(**request.arguments)
            
            return ModelContextResponse(
                result=tool_output
            )
            
        # 4. In the except section, catch a KeyError (tool not found)
        except KeyError:
            # Raise an HTTPException from FastAPI with a status_code of 404 and a detail message
            raise HTTPException(status_code=404, detail="Tool not found")
