"""Test fixtures and configurations."""

import pytest
from unittest.mock import Mock, patch
from todoist_api_python.api import TodoistAPI


@pytest.fixture
def mock_todoist_api():
    """Mock TodoistAPI with common test data."""
    api = Mock(spec=TodoistAPI)
    
    # Sample projects
    api.get_projects.return_value = [
        {"id": "proj_1", "name": "Work", "color": "blue"},
        {"id": "proj_2", "name": "Personal", "color": "green"}
    ]
    
    # Sample tasks
    api.get_tasks.return_value = [
        {"id": "task_1", "content": "Review code", "project_id": "proj_1"},
        {"id": "task_2", "content": "Buy groceries", "project_id": "proj_2"}
    ]
    
    api.get_project.return_value = {"id": "proj_1", "name": "Work", "color": "blue"}
    api.get_task.return_value = {"id": "task_1", "content": "Review code", "project_id": "proj_1"}
    
    return api


@pytest.fixture
def todoist_api_patch():
    """Patch TodoistAPI constructor for testing."""
    with patch('todoist_api_python.api.TodoistAPI') as mock_class:
        yield mock_class
