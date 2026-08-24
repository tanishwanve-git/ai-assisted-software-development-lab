import datetime
import os
import random
import urllib.parse
import urllib.request
import zoneinfo


# 1. Tool implementations
def get_current_time(city: str) -> str:
    """Get current date and time for a given city using Python stdlib."""
    normalized = city.strip().replace(" ", "_").lower()
    tz_name = next(
        (tz for tz in zoneinfo.available_timezones() if normalized in tz.lower()),
        "UTC",
    )
    now = datetime.datetime.now(zoneinfo.ZoneInfo(tz_name))
    return now.strftime(f"%Y-%m-%d %H:%M:%S ({tz_name})")


def get_current_weather(city: str) -> str:
    """Get current weather conditions for a city using wttr.in."""
    encoded_city = urllib.parse.quote(city.strip())
    url = f"https://wttr.in/{encoded_city}?format=%l:+%C+%t,+humidity+%h"
    req = urllib.request.Request(url, headers={"User-Agent": "curl/7.68.0"})
    with urllib.request.urlopen(req, timeout=5) as response:
        return response.read().decode("utf-8").strip()


def roll_dice(sides: int) -> str:
    """Roll a die with the given number of sides and return the result."""
    sides = int(sides)
    if sides < 2:
        return "Error: A die must have at least 2 sides."
    result = random.randint(1, sides)
    return f"🎲 Rolled a d{sides}: {result}"


def get_time_in(city: str) -> str:
    """Get the current date and time for a given city."""
    normalized = city.strip().replace(" ", "_").lower()
    tz_name = next(
        (tz for tz in zoneinfo.available_timezones() if normalized in tz.lower()),
        "UTC",
    )
    now = datetime.datetime.now(zoneinfo.ZoneInfo(tz_name))
    return now.strftime(f"%Y-%m-%d %H:%M:%S ({tz_name})")


def delete_file(filepath: str) -> str:
    """Delete a file at the given filepath using os.remove."""
    filepath = filepath.strip()
    if not os.path.exists(filepath):
        return f"Error: File '{filepath}' does not exist."
    if os.path.isdir(filepath):
        return f"Error: '{filepath}' is a directory, not a file."
    try:
        os.remove(filepath)
        return f"🗑️ Successfully deleted: {filepath}"
    except PermissionError:
        return f"Error: Permission denied to delete '{filepath}'."
    except OSError as e:
        return f"Error deleting '{filepath}': {e}"


# 2. Tool dispatch registry mapping function names to callable Python functions
AVAILABLE_TOOLS = {
    "get_current_time": get_current_time,
    "get_current_weather": get_current_weather,
    "roll_dice": roll_dice,
    "get_time_in": get_time_in,
    "delete_file": delete_file,
}

# Tools that require user confirmation before execution
DANGEROUS_TOOLS = {"delete_file"}

# 3. OpenAI-compatible tool definitions schema exposed to the model
TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Get the current date and time for a given city or timezone.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "City name (e.g. Tokyo, London, New York, Kolkata)",
                    }
                },
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get current weather conditions for a given city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "City name (e.g. Paris, Tokyo, Gandhinagar)",
                    }
                },
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "roll_dice",
            "description": "Roll a die with a given number of sides and return the result.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sides": {
                        "type": "integer",
                        "description": "Number of sides on the die (e.g. 6 for a standard die, 20 for a d20)",
                    }
                },
                "required": ["sides"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_time_in",
            "description": "Get the current date and time for a given city or timezone.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "City name (e.g. Tokyo, London, New York, Kolkata)",
                    }
                },
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "delete_file",
            "description": "Delete a file at the given filepath. This is a destructive operation.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "The absolute or relative path to the file to delete",
                    }
                },
                "required": ["filepath"],
            },
        },
    },
]
