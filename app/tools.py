"""
MCP Server - Tool Definitions and Implementations

This module contains the implementations and schemas for all available tools
in the MCP server. Each tool consists of:
1. An async function that performs the actual operation
2. A Tool schema that describes the tool for discovery purposes

To add a new tool:
1. Implement the async function that performs the tool's operation
2. Create a Tool schema with name, description, and input_schema
3. Register the tool in app/main.py's tool_registry dictionary

Author: OumaCavin
"""

from .models import Tool, ToolParameter


# =============================================================================
# Weather Tool
# =============================================================================

async def get_weather(location: str, unit: str = "celsius") -> dict:
    """
    Get the current weather for a specified location.

    This function simulates weather data retrieval. In a production environment,
    this would call an external weather API (e.g., OpenWeatherMap, WeatherAPI).

    Args:
        location: The city name or location to get weather for.
                  Examples: "San Francisco", "London", "Tokyo"
        unit: Temperature unit - either 'celsius' or 'fahrenheit'.
              Defaults to 'celsius' if not specified.

    Returns:
        A dictionary containing weather information:
        - location: The requested location name
        - temperature: The current temperature (rounded to 1 decimal place)
        - unit: The temperature unit label (°C or °F)
        - condition: Weather condition (sunny, partly cloudy, cloudy, rainy, stormy)
        - humidity: Humidity percentage (40-80%)
        - wind_speed: Wind speed in km/h (5-25)
        - wind_unit: Unit label for wind speed ("km/h")

    Example:
        >>> weather = await get_weather("Paris", "celsius")
        >>> print(weather)
        {
            'location': 'Paris',
            'temperature': 15.2,
            'unit': '°C',
            'condition': 'partly cloudy',
            'humidity': 62,
            'wind_speed': 14,
            'wind_unit': 'km/h'
        }
    """
    # Define available weather conditions for simulation
    # In production, these would come from a real weather API
    weather_conditions = ["sunny", "partly cloudy", "cloudy", "rainy", "stormy"]

    # Calculate base temperature using location hash
    # This ensures consistent temperatures for the same location
    # Range: 5-35 (hash returns values that can be negative, so we offset)
    base_temp = hash(location) % 30 + 5

    # Convert temperature to requested unit
    if unit.lower() == "fahrenheit":
        # Convert Celsius to Fahrenheit: F = C * 9/5 + 32
        temp = base_temp * 9 / 5 + 32
        unit_label = "°F"
    else:
        # Default to Celsius
        temp = base_temp
        unit_label = "°C"

    # Determine weather condition based on location hash
    # Using modulo ensures we stay within array bounds
    condition = weather_conditions[hash(location) % len(weather_conditions)]

    # Calculate humidity percentage (40-80% range)
    # hash(location) % 40 gives 0-39, then add 40 for 40-79
    humidity = (hash(location) % 40) + 40

    # Calculate wind speed (5-25 km/h range)
    # hash(location) % 20 gives 0-19, then add 5 for 5-24
    wind_speed = (hash(location) % 20) + 5

    # Return structured weather data
    return {
        "location": location,
        "temperature": round(temp, 1),
        "unit": unit_label,
        "condition": condition,
        "humidity": humidity,
        "wind_speed": wind_speed,
        "wind_unit": "km/h"
    }


# =============================================================================
# Tool Schema Registration
# =============================================================================

# The tool schema is the metadata that AI models use to understand
# what the tool does and what parameters it accepts. This schema is
# returned during the 'discover' operation so that AI clients can
# present appropriate options to users and validate inputs.

# Tool Schema for get_weather - describes the tool for MCP discovery
# This schema follows the JSON Schema format used by the MCP protocol
get_weather_tool_schema = Tool(
    name="get_weather",
    description="Get the current weather for a specified location including temperature, conditions, and humidity",
    input_schema={
        # JSON Schema type for the input (must be "object" for tool parameters)
        "type": "object",
        # Define the properties (parameters) this tool accepts
        "properties": {
            # The 'location' parameter - required
            "location": {
                "type": "string",
                "description": "The city name or location to get weather for"
            },
            # The 'unit' parameter - optional with default value
            "unit": {
                "type": "string",
                "description": "Temperature unit - 'celsius' or 'fahrenheit'",
                # Restrict to specific allowed values
                "enum": ["celsius", "fahrenheit"],
                # Default value if not provided by the caller
                "default": "celsius"
            }
        },
        # List of required parameters (minimum: location is required)
        "required": ["location"]
    }
)