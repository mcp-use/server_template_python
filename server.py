#!/usr/bin/env python3
"""
A simple MCP (Model Context Protocol) server example.
This server provides basic tools and resources for demonstration.
"""

from fastmcp import FastMCP
import datetime
import json
import argparse

# Initialize FastMCP server with a name
mcp = FastMCP("simple_server")

# Sample data for demonstration
SAMPLE_DATA = {
    "users": [
        {"id": 1, "name": "Alice", "email": "alice@example.com"},
        {"id": 2, "name": "Bob", "email": "bob@example.com"},
        {"id": 3, "name": "Charlie", "email": "charlie@example.com"}
    ],
    "tasks": [
        {"id": 1, "title": "Complete project", "status": "in_progress", "user_id": 1},
        {"id": 2, "title": "Review code", "status": "pending", "user_id": 2},
        {"id": 3, "title": "Write documentation", "status": "completed", "user_id": 1}
    ]
}


# Tool 1: Get current time
@mcp.tool()
async def get_current_time(timezone: str = "UTC") -> str:
    """
    Get the current date and time.
    
    Args:
        timezone: Timezone name (e.g., "UTC", "EST", "PST"). Currently only supports UTC.
    
    Returns:
        Current date and time as a formatted string.
    """
    current_time = datetime.datetime.now(datetime.timezone.utc)
    return f"Current time ({timezone}): {current_time.strftime('%Y-%m-%d %H:%M:%S %Z')}"


# Tool 2: Calculate
@mcp.tool()
async def calculate(expression: str) -> str:
    """
    Perform a simple mathematical calculation.
    
    Args:
        expression: Mathematical expression to evaluate (e.g., "2 + 2", "10 * 5")
    
    Returns:
        Result of the calculation as a string.
    """
    try:
        # Use eval with restricted namespace for safety
        # In production, use a proper math parser
        allowed_names = {
            "__builtins__": {},
            "abs": abs,
            "round": round,
            "min": min,
            "max": max,
        }
        result = eval(expression, allowed_names)
        return f"Result: {result}"
    except Exception as e:
        return f"Error evaluating expression: {str(e)}"


# Tool 3: Get users
@mcp.tool()
async def get_users() -> str:
    """
    Retrieve the list of all users from the sample database.
    
    Returns:
        JSON-formatted string containing user information.
    """
    return json.dumps(SAMPLE_DATA["users"], indent=2)


# Tool 4: Get tasks
@mcp.tool()
async def get_tasks(status: str = None, user_id: int = None) -> str:
    """
    Retrieve tasks from the sample database with optional filtering.
    
    Args:
        status: Filter by task status (pending, in_progress, completed)
        user_id: Filter by user ID
    
    Returns:
        JSON-formatted string containing task information.
    """
    tasks = SAMPLE_DATA["tasks"]
    
    # Apply filters if provided
    if status:
        tasks = [t for t in tasks if t["status"] == status]
    if user_id:
        tasks = [t for t in tasks if t["user_id"] == user_id]
    
    return json.dumps(tasks, indent=2)


# Tool 5: Echo message
@mcp.tool()
async def echo_message(message: str, uppercase: bool = False) -> str:
    """
    Echo back a message, optionally in uppercase.
    
    Args:
        message: The message to echo back
        uppercase: Whether to convert the message to uppercase
    
    Returns:
        The echoed message.
    """
    if uppercase:
        return message.upper()
    return message


# Tool 6: Count words
@mcp.tool()
async def count_words(text: str) -> str:
    """
    Count the number of words in a given text.
    
    Args:
        text: The text to analyze
    
    Returns:
        Word count statistics.
    """
    words = text.split()
    word_count = len(words)
    char_count = len(text)
    char_count_no_spaces = len(text.replace(" ", ""))
    
    return f"""Text Statistics:
- Word count: {word_count}
- Character count (with spaces): {char_count}
- Character count (without spaces): {char_count_no_spaces}
- Average word length: {char_count_no_spaces / word_count if word_count > 0 else 0:.2f} characters"""


# Main entry point
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simple MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse", "streamable-http"],
        default="streamable-http",
        help="Transport type to use (default: stdio)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=3000,
        help="Port to run the server on (only used with sse transport, default: 8000)"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host to use"
    )
    
    args = parser.parse_args()
    
    # Run the server with the specified transport
    if args.transport == "stdio":
        mcp.run(transport='stdio')
    elif args.transport == "sse":
        mcp.run(transport='sse', port=args.port, host=args.host)
    elif args.transport == "streamable-http":
        mcp.run(transport='streamable-http', port=args.port, host=args.host)
