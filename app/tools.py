from .models import Tool, ToolParameter


async def get_weather(location: str, unit: str = "celsius") -> dict:
    """
    Get the current weather for a specified location.

    Args:
        location: The city name or location to get weather for
        unit: Temperature unit - 'celsius' or 'fahrenheit' (default: celsius)

    Returns:
        A dictionary with weather information including temperature, conditions, and humidity
    """
    # Simulated weather data for demonstration purposes
    weather_conditions = ["sunny", "partly cloudy", "cloudy", "rainy", "stormy"]

    # Simulated temperature based on location hash
    base_temp = hash(location) % 30 + 5

    if unit.lower() == "fahrenheit":
        temp = base_temp * 9 / 5 + 32
        unit_label = "°F"
    else:
        temp = base_temp
        unit_label = "°C"

    condition = weather_conditions[hash(location) % len(weather_conditions)]
    humidity = (hash(location) % 40) + 40  # 40-80% range

    return {
        "location": location,
        "temperature": round(temp, 1),
        "unit": unit_label,
        "condition": condition,
        "humidity": humidity,
        "wind_speed": (hash(location) % 20) + 5,
        "wind_unit": "km/h"
    }


# Tool Schema for get_weather - describes the tool for MCP discovery
get_weather_tool_schema = Tool(
    name="get_weather",
    description="Get the current weather for a specified location including temperature, conditions, and humidity",
    input_schema={
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "The city name or location to get weather for"
            },
            "unit": {
                "type": "string",
                "description": "Temperature unit - 'celsius' or 'fahrenheit'",
                "enum": ["celsius", "fahrenheit"],
                "default": "celsius"
            }
        },
        "required": ["location"]
    }
)