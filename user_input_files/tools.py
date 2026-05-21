from .models import Tool, ToolParameter

# Task 4.1 - Create the get_weather tool function
# 2. Define a function named get_weather that accepts one argument: location (a string)
def get_weather(location: str) -> str:
    # 3. Return a string indicating the weather using the exact lab example format
    return f"The weather in {location} is sunny."


# Task 4.2 - Define the Tool Schema for get_weather
# 1. Create an instance of the Tool model assigned to GET_WEATHER_TOOL
GET_WEATHER_TOOL = Tool(
    name='get_weather',  # 2. Set the name to 'get_weather'
    description='Gets the current weather for a specified location.',  # 3. Set the description
    parameters=[  # 4. Set the parameters to a list containing one ToolParameter instance
        ToolParameter(
            name='location',
            type='string',
            description='The city and state, e.g., San Francisco, CA',
            required=True
        )
    ]
)
