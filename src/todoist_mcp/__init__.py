"""Todoist MCP Server package."""
from todoist_mcp.server import TodoistMCPServer
import argparse
import os

__version__ = "0.1.0"

def main():
    """
    Run the Sceptre MCP server with command-line arguments.
    """
    parser = argparse.ArgumentParser(description="Sceptre MCP Server")
    parser.add_argument(
        "--project-path", 
        help="Path to the Sceptre project (defaults to current directory)"
    )
    parser.add_argument(
        "--host", 
        default="localhost",
        help="Host to bind the server to (if using HTTP transport)"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=8000,
        help="Port to bind the server to (if using HTTP transport)"
    )
    parser.add_argument(
        "--transport", 
        choices=["stdio", "sse", "streamable-http"],
        default="stdio",
        help="Transport protocol to use"
    )
    
    args = parser.parse_args()
    
    # Create and run the server
    server = TodoistMCPServer()
    
    if args.transport in ["sse", "streamable-http"]:
        server.run(transport=args.transport, host=args.host, port=args.port)
    else:
        server.run(transport="stdio")

__all__ = ["main"]

if __name__ == "__main__":
    main()
# Optionally expose other important items at package level

