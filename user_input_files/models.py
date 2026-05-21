from pydantic import BaseModel
from typing import Optional, List, Any, Dict

# ToolParameter and Tool models (from Task 3.1)
class ToolParameter(BaseModel):
    name: str
    type: str
    description: str
    required: bool = True

class Tool(BaseModel):
    name: str
    description: str
    parameters: List[ToolParameter]


# --- Task 3.2 Requirements ---

# 2. Create a model ModelContextRequest
class ModelContextRequest(BaseModel):
    verb: str  # 'discovery' or 'execute'
    tool_name: Optional[str] = None
    arguments: Optional[Dict[str, Any]] = None


# 3. Create a model ModelContextResponse
class ModelContextResponse(BaseModel):
    tools: Optional[List[Tool]] = None
    result: Optional[Any] = None
