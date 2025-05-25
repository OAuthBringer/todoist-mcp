"""Tests for Todoist Task Move Support - TDD Failing Tests."""

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


class TestTaskMoveSupport:
    """Test suite for task move operations - ALL SHOULD FAIL INITIALLY."""
    
    @pytest.mark.asyncio
    async def test_move_task_tool_exists(self, server):
        """Test that move_task tool is registered."""
        tools = await server.mcp.get_tools()
        assert "move_task" in tools
    
    @pytest.mark.asyncio
    async def test_move_task_to_project(self, server, mock_api_client):
        """Test moving a task to a different project."""
        mock_instance = mock_api_client.return_value
        mock_instance.move_task.return_value = {
            "id": "task123",
            "content": "Moved task",
            "project_id": "new_project456"
        }
        
        # Execute move
        result = server.api.move_task(
            task_id="task123",
            project_id="new_project456"
        )
        
        mock_instance.move_task.assert_called_once_with(
            task_id="task123",
            project_id="new_project456"
        )
        assert result["project_id"] == "new_project456"
    
    @pytest.mark.asyncio
    async def test_move_task_to_section(self, server, mock_api_client):
        """Test moving a task to a different section within same project."""
        mock_instance = mock_api_client.return_value
        mock_instance.move_task.return_value = {
            "id": "task123",
            "content": "Moved task",
            "section_id": "section789"
        }
        
        result = server.api.move_task(
            task_id="task123",
            section_id="section789"
        )
        
        mock_instance.move_task.assert_called_once_with(
            task_id="task123",
            section_id="section789"
        )
        assert result["section_id"] == "section789"
    
    @pytest.mark.asyncio
    async def test_move_task_to_project_and_section(self, server, mock_api_client):
        """Test moving a task to both new project and section."""
        mock_instance = mock_api_client.return_value
        mock_instance.move_task.return_value = {
            "id": "task123",
            "content": "Moved task",
            "project_id": "new_project456",
            "section_id": "section789"
        }
        
        result = server.api.move_task(
            task_id="task123",
            project_id="new_project456",
            section_id="section789"
        )
        
        mock_instance.move_task.assert_called_once_with(
            task_id="task123",
            project_id="new_project456",
            section_id="section789"
        )
        assert result["project_id"] == "new_project456"
        assert result["section_id"] == "section789"
    
    @pytest.mark.asyncio
    async def test_move_task_with_parent(self, server, mock_api_client):
        """Test moving a task under a different parent task."""
        mock_instance = mock_api_client.return_value
        mock_instance.move_task.return_value = {
            "id": "task123",
            "content": "Moved subtask",
            "parent_id": "parent456"
        }
        
        result = server.api.move_task(
            task_id="task123",
            parent_id="parent456"
        )
        
        mock_instance.move_task.assert_called_once_with(
            task_id="task123",
            parent_id="parent456"
        )
        assert result["parent_id"] == "parent456"
    
    @pytest.mark.asyncio
    async def test_move_task_validation_no_target(self, server, mock_api_client):
        """Test validation - must specify at least one target."""
        # Configure mock to raise validation error
        mock_instance = mock_api_client.return_value
        mock_instance.move_task.side_effect = ValueError("Must specify at least one target: project_id, section_id, or parent_id")
        
        # Should raise error when no move parameters provided
        with pytest.raises(ValueError, match="Must specify at least one"):
            server.api.move_task(task_id="task123")
    
    @pytest.mark.asyncio
    async def test_move_task_error_handling(self, server, mock_api_client):
        """Test error handling for invalid moves."""
        mock_instance = mock_api_client.return_value
        mock_instance.move_task.side_effect = Exception("API Error: Invalid project_id")
        
        with pytest.raises(Exception, match="API Error: Invalid project_id"):
            server.api.move_task(
                task_id="task123",
                project_id="invalid_project"
            )
    
    @pytest.mark.asyncio
    async def test_move_task_preserves_attributes(self, server, mock_api_client):
        """Test that move preserves task attributes like labels, priority, etc."""
        mock_instance = mock_api_client.return_value
        mock_instance.move_task.return_value = {
            "id": "task123",
            "content": "Moved task",
            "project_id": "new_project456",
            "labels": ["important", "work"],
            "priority": 4,
            "due": {"date": "2025-05-30"}
        }
        
        result = server.api.move_task(
            task_id="task123",
            project_id="new_project456"
        )
        
        # Verify task attributes preserved after move
        assert result["labels"] == ["important", "work"]
        assert result["priority"] == 4
        assert result["due"]["date"] == "2025-05-30"
