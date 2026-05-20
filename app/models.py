from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict


class ToolParameter(BaseModel):
    """Model representing a tool parameter specification."""
    name: str = Field(..., description="The name of the parameter")
    type: str = Field(..., description="The data type of the parameter (e.g., string, integer)")
    description: str = Field(..., description="Human-readable description of the parameter")
    required: bool = Field(default=False, description="Whether this parameter is required")
    default: Optional[Any] = Field(default=None, description="Default value if not required")


class Tool(BaseModel):
    """Model representing a tool available in the MCP server."""
    name: str = Field(..., description="Unique identifier for the tool")
    description: str = Field(..., description="Human-readable description of what the tool does")
    input_schema: Dict[str, Any] = Field(..., description="JSON Schema for tool input parameters")


class ModelContextRequest(BaseModel):
    """Request model for MCP protocol operations."""
    jsonrpc: str = Field(default="2.0", description="JSON-RPC version")
    id: Optional[int] = Field(default=None, description="Request identifier")
    method: str = Field(..., description="The method to invoke (discover, execute)")
    params: Optional[Dict[str, Any]] = Field(default=None, description="Method parameters")


class ModelContextResponse(BaseModel):
    """Response model for MCP protocol operations."""
    jsonrpc: str = Field(default="2.0", description="JSON-RPC version")
    id: Optional[int] = Field(default=None, description="Response identifier")
    result: Optional[Any] = Field(default=None, description="Result data")
    error: Optional[Dict[str, Any]] = Field(default=None, description="Error information")