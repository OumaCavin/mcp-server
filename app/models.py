"""
MCP Server - Data Models

This module defines Pydantic models for the MCP protocol's request and response payloads.
These models ensure type safety and provide automatic validation for incoming requests
and outgoing responses following the JSON-RPC 2.0 specification.

Author: OumaCavin
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict


# =============================================================================
# Tool Definition Models
# =============================================================================

# These models define the structure of tools that can be discovered and executed
# through the MCP protocol. They describe the tool's metadata and input parameters.


class ToolParameter(BaseModel):
    """
    Model representing a single parameter for a tool.

    This model describes a parameter that a tool accepts, including its name,
    data type, description, and whether it is required.

    Attributes:
        name: The parameter's identifier name (used when passing arguments)
        type: The data type (e.g., "string", "integer", "boolean")
        description: Human-readable explanation of what the parameter does
        required: Whether this parameter must be provided (default: False)
        default: Default value if the parameter is not required and not provided
    """

    name: str = Field(
        ...,
        description="The name of the parameter"
    )
    type: str = Field(
        ...,
        description="The data type of the parameter (e.g., string, integer)"
    )
    description: str = Field(
        ...,
        description="Human-readable description of the parameter"
    )
    required: bool = Field(
        default=False,
        description="Whether this parameter is required"
    )
    default: Optional[Any] = Field(
        default=None,
        description="Default value if not required"
    )


class Tool(BaseModel):
    """
    Model representing a tool available in the MCP server.

    This model contains all the metadata needed for an AI to:
    - Identify the tool by its unique name
    - Understand what the tool does
    - Know what input parameters to provide

    Attributes:
        name: Unique identifier for the tool (used in execute requests)
        description: Human-readable explanation of the tool's functionality
        input_schema: JSON Schema defining the expected input parameters
    """

    name: str = Field(
        ...,
        description="Unique identifier for the tool"
    )
    description: str = Field(
        ...,
        description="Human-readable description of what the tool does"
    )
    input_schema: Dict[str, Any] = Field(
        ...,
        description="JSON Schema for tool input parameters"
    )


# =============================================================================
# Protocol Message Models
# =============================================================================

# These models implement the JSON-RPC 2.0 specification for request/response
# messaging. JSON-RPC is a stateless, lightweight remote procedure call protocol.


class ModelContextRequest(BaseModel):
    """
    Request model for MCP protocol operations.

    This model represents an incoming MCP request following JSON-RPC 2.0 format.
    It includes the version identifier, request ID for correlation, the method
    name, and any parameters needed for the operation.

    Attributes:
        jsonrpc: Must be "2.0" to comply with JSON-RPC 2.0 specification
        id: Optional request identifier for matching responses to requests
        method: The operation to perform ("discover" or "execute")
        params: Optional dictionary of method-specific parameters

    Example:
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "execute",
            "params": {
                "tool_name": "get_weather",
                "arguments": {"location": "London"}
            }
        }
    """

    jsonrpc: str = Field(
        default="2.0",
        description="JSON-RPC version"
    )
    id: Optional[int] = Field(
        default=None,
        description="Request identifier for correlating responses"
    )
    method: str = Field(
        ...,
        description="The method to invoke (discover or execute)"
    )
    params: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Method-specific parameters"
    )


class ModelContextResponse(BaseModel):
    """
    Response model for MCP protocol operations.

    This model represents an MCP response following JSON-RPC 2.0 format.
    It includes the version identifier, the response ID (matching the request),
    and either a result or an error.

    Attributes:
        jsonrpc: Must be "2.0" to comply with JSON-RPC 2.0 specification
        id: Response identifier matching the request ID
        result: The successful result data (None if error occurred)
        error: Error information if the request failed (None if successful)

    Note:
        A response must contain either 'result' OR 'error', never both.
        This is a JSON-RPC 2.0 specification requirement.
    """

    jsonrpc: str = Field(
        default="2.0",
        description="JSON-RPC version"
    )
    id: Optional[int] = Field(
        default=None,
        description="Response identifier matching the request ID"
    )
    result: Optional[Any] = Field(
        default=None,
        description="Result data on success"
    )
    error: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Error information on failure"
    )