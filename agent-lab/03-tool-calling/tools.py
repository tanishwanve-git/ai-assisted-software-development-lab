import datetime
import os
import random
import subprocess
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


def read_file(filepath: str) -> str:
    """Read and return the contents of a file."""
    filepath = filepath.strip()
    if not os.path.exists(filepath):
        return f"Error: File '{filepath}' does not exist."
    if os.path.isdir(filepath):
        return f"Error: '{filepath}' is a directory, not a file."
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        return f"📄 Contents of {filepath}:\n{content}"
    except PermissionError:
        return f"Error: Permission denied to read '{filepath}'."
    except UnicodeDecodeError:
        return f"Error: '{filepath}' is not a valid text file."
    except OSError as e:
        return f"Error reading '{filepath}': {e}"


def write_file(filepath: str, content: str) -> str:
    """Write content to a file, creating it if it doesn't exist."""
    filepath = filepath.strip()
    try:
        # Create parent directories if they don't exist
        parent = os.path.dirname(filepath)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return f"✏️ Successfully wrote {len(content)} characters to {filepath}"
    except PermissionError:
        return f"Error: Permission denied to write to '{filepath}'."
    except OSError as e:
        return f"Error writing to '{filepath}': {e}"


def run_bash(command: str) -> str:
    """Run a bash command using subprocess.run and return the output."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
        )
        output = ""
        if result.stdout:
            output += f"stdout:\n{result.stdout}"
        if result.stderr:
            output += f"stderr:\n{result.stderr}"
        if not output:
            output = "(no output)"
        return f"🖥️ Exit code: {result.returncode}\n{output}"
    except subprocess.TimeoutExpired:
        return "Error: Command timed out after 30 seconds."
    except OSError as e:
        return f"Error running command: {e}"


# 2. Tool dispatch registry mapping function names to callable Python functions
AVAILABLE_TOOLS = {
    "get_current_time": get_current_time,
    "get_current_weather": get_current_weather,
    "roll_dice": roll_dice,
    "get_time_in": get_time_in,
    "delete_file": delete_file,
    "read_file": read_file,
    "write_file": write_file,
    "run_bash": run_bash,
}

# Tools that require user confirmation before execution
DANGEROUS_TOOLS = {"delete_file", "write_file", "run_bash"}

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
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read and return the contents of a file at the given filepath.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "The absolute or relative path to the file to read",
                    }
                },
                "required": ["filepath"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write content to a file, creating it if it doesn't exist. This is a destructive operation that overwrites existing content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "The absolute or relative path to the file to write",
                    },
                    "content": {
                        "type": "string",
                        "description": "The text content to write to the file",
                    }
                },
                "required": ["filepath", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_bash",
            "description": "Run a bash shell command and return the output. Has a 30-second timeout. This is a potentially dangerous operation.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The bash command to execute (e.g. 'ls -la', 'cat file.txt', 'echo hello')",
                    }
                },
                "required": ["command"],
            },
        },
    },
]
