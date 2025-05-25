"""Tests for Todoist API v1 client."""

import pytest
from unittest.mock import Mock, patch
import httpx
from todoist_mcp.api_v1 import TodoistV1Client


@pytest.fixture
def api_client(mock_httpx_client):
    """Create API client with mocked httpx."""
    return TodoistV1Client("test_token")


@pytest.fixture
def mock_httpx_client():
    """Mock httpx.Client for testing."""
    with patch("todoist_mcp.api_v1.httpx.Client") as mock_class:
        mock_instance = Mock()
        mock_class.return_value = mock_instance
        yield mock_instance


class TestTodoistV1Client:
    def test_init(self, api_client):
        """Test client initialization."""
        assert api_client.token == "test_token"
        assert api_client.headers["Authorization"] == "Bearer test_token"
        assert api_client.headers["Content-Type"] == "application/json"
    
    def test_get_projects_with_limit(self, api_client, mock_httpx_client):
        """Test get_projects with limit parameter."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [{"id": "123", "name": "Test Project"}],
            "next_cursor": "abc123"
        }
        mock_response.raise_for_status = Mock()
        mock_response.status_code = 200
        mock_response.content = b'{"results": [{"id": "123", "name": "Test Project"}], "next_cursor": "abc123"}'
        
        mock_instance = mock_httpx_client
        mock_instance.request.return_value = mock_response
        
        result = api_client.get_projects(limit=1)
        
        mock_instance.request.assert_called_once_with(
            "GET",
            "https://api.todoist.com/api/v1/projects",
            json=None,
            params={"limit": 1}
        )
        assert result["results"][0]["name"] == "Test Project"
        assert result["next_cursor"] == "abc123"
    
    def test_get_projects_with_cursor(self, api_client, mock_httpx_client):
        """Test get_projects with cursor for pagination."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [{"id": "456", "name": "Next Project"}],
            "next_cursor": None
        }
        mock_response.raise_for_status = Mock()
        mock_response.status_code = 200
        mock_response.content = b'{"results": [{"id": "456", "name": "Next Project"}], "next_cursor": null}'
        
        mock_instance = mock_httpx_client
        mock_instance.request.return_value = mock_response
        
        result = api_client.get_projects(limit=1, cursor="abc123")
        
        mock_instance.request.assert_called_once_with(
            "GET",
            "https://api.todoist.com/api/v1/projects",
            json=None,
            params={"limit": 1, "cursor": "abc123"}
        )
        assert result["next_cursor"] is None
    
    def test_get_project(self, api_client, mock_httpx_client):
        """Test get_project by ID."""
        mock_response = Mock()
        mock_response.json.return_value = {"id": "123", "name": "Test Project"}
        mock_response.raise_for_status = Mock()
        mock_response.status_code = 200
        mock_response.content = b'{"id": "123", "name": "Test Project"}'
        
        mock_instance = mock_httpx_client
        mock_instance.request.return_value = mock_response
        
        result = api_client.get_project("123")
        
        mock_instance.request.assert_called_once_with(
            "GET",
            "https://api.todoist.com/api/v1/projects/123",
            json=None,
            params=None
        )
        assert result["id"] == "123"
    
    def test_add_project(self, api_client, mock_httpx_client):
        """Test add_project."""
        mock_response = Mock()
        mock_response.json.return_value = {"id": "789", "name": "New Project"}
        mock_response.raise_for_status = Mock()
        mock_response.status_code = 200
        mock_response.content = b'{"id": "789", "name": "New Project"}'
        
        mock_instance = mock_httpx_client
        mock_instance.request.return_value = mock_response
        
        result = api_client.add_project("New Project", color="red")
        
        mock_instance.request.assert_called_once_with(
            "POST",
            "https://api.todoist.com/api/v1/projects",
            json={"name": "New Project", "color": "red"},
            params=None
        )
        assert result["name"] == "New Project"
    
    def test_get_tasks_with_filters(self, api_client, mock_httpx_client):
        """Test get_tasks with various filters."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [{"id": "task1", "content": "Test Task"}],
            "next_cursor": "task_cursor"
        }
        mock_response.raise_for_status = Mock()
        mock_response.status_code = 200
        mock_response.content = b'{"results": [{"id": "task1", "content": "Test Task"}], "next_cursor": "task_cursor"}'
        
        mock_instance = mock_httpx_client
        mock_instance.request.return_value = mock_response
        
        result = api_client.get_tasks(
            project_id="123",
            limit=10,
            section_id="456",
            parent_id="789"
        )
        
        expected_params = {
            "limit": 10,
            "project_id": "123",
            "section_id": "456",
            "parent_id": "789"
        }
        
        mock_instance.request.assert_called_once_with(
            "GET",
            "https://api.todoist.com/api/v1/tasks",
            json=None,
            params=expected_params
        )
        assert result["results"][0]["content"] == "Test Task"
    
    def test_add_task(self, api_client, mock_httpx_client):
        """Test add_task with various parameters."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "task123",
            "content": "New Task",
            "project_id": "proj123"
        }
        mock_response.raise_for_status = Mock()
        mock_response.status_code = 200
        mock_response.content = b'{"id": "task123", "content": "New Task", "project_id": "proj123"}'
        
        mock_instance = mock_httpx_client
        mock_instance.request.return_value = mock_response
        
        result = api_client.add_task(
            "New Task",
            project_id="proj123",
            priority=4,
            due_string="tomorrow"
        )
        
        expected_json = {
            "content": "New Task",
            "project_id": "proj123",
            "priority": 4,
            "due_string": "tomorrow"
        }
        
        mock_instance.request.assert_called_once_with(
            "POST",
            "https://api.todoist.com/api/v1/tasks",
            json=expected_json,
            params=None
        )
        assert result["content"] == "New Task"
    
    def test_error_handling(self, api_client, mock_httpx_client):
        """Test error handling for failed requests."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "404 Not Found",
            request=Mock(),
            response=Mock(status_code=404)
        )
        mock_response.status_code = 404
        mock_response.content = b''
        
        mock_instance = mock_httpx_client
        mock_instance.request.return_value = mock_response
        
        with pytest.raises(httpx.HTTPStatusError):
            api_client.get_project("nonexistent")
