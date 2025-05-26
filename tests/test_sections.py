"""Test suite for sections management functionality."""

import pytest
from unittest.mock import Mock, patch
import httpx
from todoist_mcp.api_v1 import TodoistV1Client


@pytest.fixture
def api_client():
    """Create API client with mocked httpx."""
    with patch("todoist_mcp.api_v1.httpx.Client") as mock_class:
        mock_instance = Mock()
        mock_class.return_value = mock_instance
        client = TodoistV1Client("test_token")
        yield client, mock_instance


class TestSections:
    """Test sections CRUD operations."""
    
    def test_get_sections(self, api_client):
        """Test getting all sections for a project."""
        client, mock_http = api_client
        
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "id": "7025",
                "project_id": "2203306141",
                "order": 1,
                "name": "Groceries"
            },
            {
                "id": "7026",
                "project_id": "2203306141",
                "order": 2,
                "name": "Household"
            }
        ]
        mock_response.content = b'[{"id": "7025", "project_id": "2203306141", "order": 1, "name": "Groceries"}]'
        mock_http.request.return_value = mock_response
        
        sections = client.get_sections("2203306141")
        
        assert len(sections) == 2
        assert sections[0]["name"] == "Groceries"
        assert sections[1]["name"] == "Household"
        mock_http.request.assert_called_once_with(
            "GET",
            "https://api.todoist.com/api/v1/sections",
            params={"project_id": "2203306141", "limit": 100}
        )
    
    def test_get_sections_with_pagination(self, api_client):
        """Test getting sections with cursor-based pagination."""
        client, mock_http = api_client
        
        # First page
        mock_response1 = Mock()
        mock_response1.status_code = 200
        mock_response1.json.return_value = [{"id": f"700{i}", "name": f"Section {i}"} for i in range(100)]
        mock_response1.headers = {"X-Pagination-Next-Cursor": "next_cursor_123"}
        
        # Second page
        mock_response2 = Mock()
        mock_response2.status_code = 200
        mock_response2.json.return_value = [{"id": f"71{i:02d}", "name": f"Section {i+100}"} for i in range(20)]
        mock_response2.headers = {}
        
        mock_http.request.side_effect = [mock_response1, mock_response2]
        
        sections = client.get_sections("2203306141")
        
        assert len(sections) == 120
        assert sections[0]["name"] == "Section 0"
        assert sections[119]["name"] == "Section 119"
        assert mock_http.request.call_count == 2
    
    def test_get_sections_with_cursor_and_limit(self, api_client):
        """Test getting sections with custom cursor and limit."""
        client, mock_http = api_client
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"id": "7025", "name": "Test Section"}]
        mock_response.headers = {}  # No cursor to avoid recursion in test
        mock_http.request.return_value = mock_response
        
        sections = client.get_sections("2203306141", cursor="start_cursor", limit=50)
        
        assert len(sections) == 1
        mock_http.request.assert_called_once_with(
            "GET",
            "https://api.todoist.com/api/v1/sections",
            params={
                "project_id": "2203306141",
                "cursor": "start_cursor",
                "limit": 50
            }
        )
    
    def test_get_section(self, api_client):
        """Test getting a single section by ID."""
        client, mock_http = api_client
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "7025",
            "project_id": "2203306141",
            "order": 1,
            "name": "Groceries"
        }
        mock_http.request.return_value = mock_response
        
        section = client.get_section("7025")
        
        assert section["id"] == "7025"
        assert section["name"] == "Groceries"
        mock_http.request.assert_called_once_with(
            "GET",
            "https://api.todoist.com/api/v1/sections/7025",
            json=None,
            params=None
        )
    
    def test_add_section(self, api_client):
        """Test creating a new section."""
        client, mock_http = api_client
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "7027",
            "project_id": "2203306141",
            "order": 3,
            "name": "Electronics"
        }
        mock_http.request.return_value = mock_response
        
        section = client.add_section("2203306141", "Electronics", order=3)
        
        assert section["id"] == "7027"
        assert section["name"] == "Electronics"
        assert section["order"] == 3
        mock_http.request.assert_called_once_with(
            "POST",
            "https://api.todoist.com/api/v1/sections",
            json={
                "project_id": "2203306141",
                "name": "Electronics",
                "order": 3
            },
            params=None
        )
    
    def test_add_section_without_order(self, api_client):
        """Test creating a section without specifying order."""
        client, mock_http = api_client
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "7028",
            "project_id": "2203306141",
            "order": 4,
            "name": "Books"
        }
        mock_http.request.return_value = mock_response
        
        section = client.add_section("2203306141", "Books")
        
        assert section["name"] == "Books"
        mock_http.request.assert_called_once_with(
            "POST",
            "https://api.todoist.com/api/v1/sections",
            json={
                "project_id": "2203306141",
                "name": "Books"
            },
            params=None
        )
    
    def test_update_section(self, api_client):
        """Test updating a section's name."""
        client, mock_http = api_client
        
        mock_response = Mock()
        mock_response.status_code = 204
        mock_response.content = b''
        mock_http.request.return_value = mock_response
        
        result = client.update_section("7025", name="Fresh Produce")
        
        assert result is None  # 204 returns None
        mock_http.request.assert_called_once_with(
            "POST",
            "https://api.todoist.com/api/v1/sections/7025",
            json={"name": "Fresh Produce"},
            params=None
        )
    
    def test_delete_section(self, api_client):
        """Test deleting a section."""
        client, mock_http = api_client
        
        mock_response = Mock()
        mock_response.status_code = 204
        mock_response.content = b''
        mock_http.request.return_value = mock_response
        
        result = client.delete_section("7025")
        
        assert result is None  # 204 returns None
        mock_http.request.assert_called_once_with(
            "DELETE",
            "https://api.todoist.com/api/v1/sections/7025",
            json=None,
            params=None
        )
    
    def test_move_section(self, api_client):
        """Test reordering a section within a project."""
        client, mock_http = api_client
        
        mock_response = Mock()
        mock_response.status_code = 204
        mock_response.content = b''
        mock_http.request.return_value = mock_response
        
        result = client.move_section("7025", order=5)
        
        assert result is None  # 204 returns None
        mock_http.request.assert_called_once_with(
            "POST",
            "https://api.todoist.com/api/v1/sections/7025/move",
            json={"order": 5},
            params=None
        )
    
    def test_get_sections_error_handling(self, api_client):
        """Test error handling for get sections."""
        client, mock_http = api_client
        
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "404 Not Found",
            request=Mock(),
            response=Mock(status_code=404)
        )
        mock_http.request.return_value = mock_response
        
        with pytest.raises(httpx.HTTPStatusError):
            client.get_sections("invalid_project")
    
    def test_add_section_rate_limit(self, api_client):
        """Test rate limit handling for add section."""
        client, mock_http = api_client
        
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "429 Too Many Requests",
            request=Mock(),
            response=Mock(status_code=429, headers={"Retry-After": "60"})
        )
        mock_http.request.return_value = mock_response
        
        with pytest.raises(httpx.HTTPStatusError) as excinfo:
            client.add_section("2203306141", "New Section")
        
        assert excinfo.value.response.status_code == 429
    
    def test_update_section_empty_name(self, api_client):
        """Test updating section with empty name should fail."""
        client, mock_http = api_client
        
        # The validation should happen in the client
        with pytest.raises(ValueError) as excinfo:
            client.update_section("7025", name="")
        
        assert "Section name cannot be empty" in str(excinfo.value)
    
    def test_move_section_invalid_order(self, api_client):
        """Test moving section with invalid order."""
        client, mock_http = api_client
        
        # The validation should happen in the client
        with pytest.raises(ValueError) as excinfo:
            client.move_section("7025", order=-1)
        
        assert "Order must be a positive integer" in str(excinfo.value)


class TestSectionsIntegration:
    """Integration tests for sections with tasks."""
    
    def test_move_task_to_section(self, api_client):
        """Test moving a task to a different section."""
        client, mock_http = api_client
        
        # This test verifies that the existing move_task method supports section_id
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "task123", "section_id": "7025"}
        mock_http.request.return_value = mock_response
        
        result = client.move_task("task123", section_id="7025")
        
        assert result["section_id"] == "7025"
        mock_http.request.assert_called_once_with(
            "POST",
            "https://api.todoist.com/api/v1/tasks/task123/move",
            json={"section_id": "7025"},
            params=None
        )
    
    def test_get_tasks_filtered_by_section(self, api_client):
        """Test getting tasks filtered by section_id."""
        client, mock_http = api_client
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [
                {
                    "id": "task1",
                    "content": "Buy milk",
                    "section_id": "7025"
                },
                {
                    "id": "task2", 
                    "content": "Buy bread",
                    "section_id": "7025"
                }
            ],
            "next_cursor": None
        }
        mock_http.request.return_value = mock_response
        
        tasks = client.get_tasks(section_id="7025")
        
        assert len(tasks["results"]) == 2
        assert all(task["section_id"] == "7025" for task in tasks["results"])
        mock_http.request.assert_called_once_with(
            "GET",
            "https://api.todoist.com/api/v1/tasks",
            json=None,
            params={"section_id": "7025"}
        )
    
    def test_task_includes_section_id(self, api_client):
        """Test that task responses include section_id field."""
        client, mock_http = api_client
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "task123",
            "content": "Test task",
            "project_id": "2203306141",
            "section_id": "7025"
        }
        mock_http.request.return_value = mock_response
        
        task = client.get_task("task123")
        
        assert "section_id" in task
        assert task["section_id"] == "7025"
    
    def test_add_task_with_section(self, api_client):
        """Test creating a task directly in a section."""
        client, mock_http = api_client
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "task456",
            "content": "New task in section",
            "section_id": "7025"
        }
        mock_http.request.return_value = mock_response
        
        task = client.add_task("New task in section", section_id="7025")
        
        assert task["section_id"] == "7025"
        mock_http.request.assert_called_once_with(
            "POST",
            "https://api.todoist.com/api/v1/tasks",
            json={
                "content": "New task in section",
                "section_id": "7025"
            },
            params=None
        )
