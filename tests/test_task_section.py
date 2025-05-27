"""Tests for Task-Section Integration - TDD Failing Tests."""

import pytest
from unittest.mock import Mock, patch
from todoist_mcp.server import TodoistMCPServer


@pytest.fixture
def mock_auth_manager():
    """Mock AuthManager."""
    with patch("todoist_mcp.server.AuthManager") as mock:
        instance = mock.return_value
        instance.get_token.return_value = "test_token"
        yield mock


@pytest.fixture
def mock_api_client():
    """Mock TodoistV1Client."""
    with patch("todoist_mcp.server.TodoistV1Client") as mock:
        yield mock


@pytest.fixture
def server(mock_auth_manager, mock_api_client):
    """Create server instance with mocked dependencies."""
    return TodoistMCPServer()


class TestTaskSectionIntegration:
    """Test suite for task-section integration - ALL SHOULD FAIL INITIALLY."""
    
    @pytest.mark.asyncio
    async def test_move_task_with_section_id_passes_parameter(self, server, mock_api_client):
        """Test that move_task correctly passes section_id to API."""
        mock_instance = mock_api_client.return_value
        mock_instance.move_task.return_value = {
            "id": "task123",
            "content": "Task in section",
            "section_id": "section456"
        }
        
        # Execute move
        result = server.api.move_task(
            task_id="task123",
            section_id="section456"
        )
        
        # Verify section_id was passed to API call
        mock_instance.move_task.assert_called_once_with(
            task_id="task123",
            section_id="section456"
        )
        assert result["section_id"] == "section456"
    
    @pytest.mark.asyncio
    async def test_get_tasks_returns_section_id_in_results(self, server, mock_api_client):
        """Test that get_tasks includes section_id in task responses."""
        mock_instance = mock_api_client.return_value
        mock_instance.get_tasks.return_value = {
            "results": [
                {
                    "id": "task1",
                    "content": "Task in section",
                    "project_id": "proj123",
                    "section_id": "section789"  # This should be included
                },
                {
                    "id": "task2",
                    "content": "Task without section",
                    "project_id": "proj123",
                    "section_id": None  # Tasks not in a section should have null
                }
            ],
            "next_cursor": None
        }
        
        # Get tasks
        result = server.api.get_tasks(project_id="proj123")
        
        # Verify section_id is present in results
        assert "section_id" in result["results"][0]
        assert result["results"][0]["section_id"] == "section789"
        assert "section_id" in result["results"][1]
        assert result["results"][1]["section_id"] is None
    
    @pytest.mark.asyncio
    async def test_get_tasks_filters_by_section_id(self, server, mock_api_client):
        """Test that get_tasks correctly filters by section_id."""
        mock_instance = mock_api_client.return_value
        # Mock should only return tasks from the requested section
        mock_instance.get_tasks.return_value = {
            "results": [
                {
                    "id": "task1",
                    "content": "Task in requested section",
                    "project_id": "proj123",
                    "section_id": "section456"
                }
            ],
            "next_cursor": None
        }
        
        # Get tasks filtered by section
        result = server.api.get_tasks(
            project_id="proj123",
            section_id="section456"
        )
        
        # Verify API was called with section_id filter
        mock_instance.get_tasks.assert_called_once_with(
            project_id="proj123",
            section_id="section456"
        )
        
        # Verify only tasks from that section returned
        assert len(result["results"]) == 1
        assert result["results"][0]["section_id"] == "section456"
    
    @pytest.mark.asyncio
    async def test_get_task_includes_section_id(self, server, mock_api_client):
        """Test that get_task includes section_id in single task response."""
        mock_instance = mock_api_client.return_value
        mock_instance.get_task.return_value = {
            "id": "task123",
            "content": "Single task",
            "project_id": "proj456",
            "section_id": "section789"
        }
        
        # Get single task
        result = server.api.get_task(task_id="task123")
        
        # Verify section_id is included
        assert "section_id" in result
        assert result["section_id"] == "section789"
    
    @pytest.mark.asyncio
    async def test_add_task_with_section_id(self, server, mock_api_client):
        """Test that add_task accepts and returns section_id."""
        mock_instance = mock_api_client.return_value
        mock_instance.add_task.return_value = {
            "id": "new_task",
            "content": "New task in section",
            "project_id": "proj123",
            "section_id": "section456"
        }
        
        # Add task to specific section
        result = server.api.add_task(
            content="New task in section",
            project_id="proj123",
            section_id="section456"
        )
        
        # Verify section_id was passed to API
        mock_instance.add_task.assert_called_once_with(
            content="New task in section",
            project_id="proj123", 
            section_id="section456"
        )
        
        # Verify section_id in response
        assert "section_id" in result
        assert result["section_id"] == "section456"
    
    @pytest.mark.asyncio
    async def test_update_task_preserves_section_id(self, server, mock_api_client):
        """Test that update_task preserves section_id in response."""
        mock_instance = mock_api_client.return_value
        mock_instance.update_task.return_value = {
            "id": "task123",
            "content": "Updated task",
            "project_id": "proj456",
            "section_id": "section789"  # Should be preserved
        }
        
        # Update task
        result = server.api.update_task(
            task_id="task123",
            content="Updated task"
        )
        
        # Verify section_id is preserved in response
        assert "section_id" in result
        assert result["section_id"] == "section789"
    
    @pytest.mark.asyncio
    async def test_move_task_from_section_to_no_section(self, server, mock_api_client):
        """Test moving task out of a section (section_id = None)."""
        mock_instance = mock_api_client.return_value
        mock_instance.move_task.return_value = {
            "id": "task123",
            "content": "Task moved out of section",
            "project_id": "proj456",
            "section_id": None  # Moved to no section
        }
        
        # Move task to no section by passing None
        result = server.api.move_task(
            task_id="task123",
            section_id=None
        )
        
        # Verify None was passed for section_id
        mock_instance.move_task.assert_called_once_with(
            task_id="task123",
            section_id=None
        )
        
        # Verify task has no section
        assert result["section_id"] is None
