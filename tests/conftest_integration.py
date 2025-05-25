"""Shared fixtures for integration tests with proper cleanup."""

import pytest
import os
from dotenv import load_dotenv
from todoist_mcp.server import TodoistMCPServer
import datetime

# Load environment variables
load_dotenv()


@pytest.fixture
def server():
    """Create server instance with real API token."""
    token = os.getenv("TODOIST_API_TOKEN")
    if not token:
        raise ValueError("TODOIST_API_TOKEN not found in environment")
    return TodoistMCPServer(token=token)


@pytest.fixture
def test_project_manager(server):
    """Manager for test projects with automatic cleanup."""
    created_projects = []
    
    def create_project(name_suffix=""):
        """Create a test project and track it for cleanup."""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        name = f"TEST_INTEGRATION_{timestamp}_{name_suffix}"
        project = server.api.add_project(name=name, color="red")
        created_projects.append(project["id"])
        return project
    
    yield create_project
    
    # Cleanup all created projects
    for project_id in created_projects:
        try:
            server.api.delete_project(project_id)
        except Exception as e:
            print(f"Failed to delete project {project_id}: {e}")


@pytest.fixture
def cleanup_test_projects(server):
    """Clean up any leftover test projects from previous runs."""
    # Get all projects
    all_projects = server.api.get_projects()
    
    # Find and delete test projects
    for project in all_projects.get("results", []):
        if project["name"].startswith("TEST_INTEGRATION_") or project["name"].startswith("Test Move - ") or project["name"].startswith("Test Project - "):
            try:
                server.api.delete_project(project["id"])
                print(f"Cleaned up old test project: {project['name']}")
            except Exception as e:
                print(f"Failed to clean up {project['name']}: {e}")
