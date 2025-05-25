"""Clean up test projects from Todoist."""

import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from todoist_mcp.server import TodoistMCPServer

load_dotenv()

def cleanup_test_projects():
    """Remove all test projects."""
    server = TodoistMCPServer()
    
    print("Fetching all projects...")
    all_projects = server.api.get_projects()
    
    test_prefixes = [
        "TEST_INTEGRATION_",
        "Test Move - ",
        "Test Project - ",
        "Test - "
    ]
    
    deleted_count = 0
    
    for project in all_projects.get("results", []):
        if any(project["name"].startswith(prefix) for prefix in test_prefixes):
            try:
                print(f"Deleting: {project['name']} {project["id"]}")
                server.api.delete_project(project["id"])
                deleted_count += 1
            except Exception as e:
                print(f"Failed to delete {project['name']}: {e}")
    
    print(f"\nCleanup complete. Deleted {deleted_count} test projects.")

if __name__ == "__main__":
    cleanup_test_projects()
