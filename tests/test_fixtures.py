"""Test example showing mock usage patterns."""

import pytest
from unittest.mock import Mock, patch
from tests.conftest import mock_todoist_api


def test_mock_usage_example(mock_todoist_api):
    """Example of using mocked TodoistAPI."""
    # Mock returns predefined data
    projects = mock_todoist_api.get_projects()
    assert len(projects) == 2
    assert projects[0]["name"] == "Work"
    
    # Mock method calls can be verified
    mock_todoist_api.add_task.assert_not_called()
    
    # Configure specific return values
    mock_todoist_api.add_task.return_value = {"id": "new_task", "content": "Test task"}
    result = mock_todoist_api.add_task("Test task")
    assert result["id"] == "new_task"


@patch('todoist_api_python.api.TodoistAPI')
def test_patch_usage_example(mock_class):
    """Example of patching TodoistAPI constructor."""
    # Mock instance returned by constructor
    mock_instance = Mock()
    mock_class.return_value = mock_instance
    
    # Configure mock behavior
    mock_instance.get_projects.return_value = [{"id": "test", "name": "Test"}]
    
    # Use in actual code
    from todoist_api_python.api import TodoistAPI
    api = TodoistAPI("fake_token")
    projects = api.get_projects()
    
    assert projects[0]["name"] == "Test"
    mock_class.assert_called_once_with("fake_token")
