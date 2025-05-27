"""Tests for Batch Operations - TDD Failing Tests."""

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


class TestBatchOperations:
    """Test suite for batch operations - ALL SHOULD FAIL INITIALLY."""
    
    @pytest.mark.asyncio
    async def test_batch_move_tasks_tool_exists(self, server):
        """Test that batch_move_tasks tool is registered."""
        tools = await server.mcp.get_tools()
        assert "batch_move_tasks" in tools
    
    @pytest.mark.asyncio
    async def test_batch_move_tasks_to_project(self, server, mock_api_client):
        """Test batch moving multiple tasks to a different project."""
        mock_instance = mock_api_client.return_value
        mock_instance.batch_move_tasks.return_value = {
            "moved": ["task1", "task2", "task3"],
            "failed": []
        }
        
        result = server.api.batch_move_tasks(
            task_ids=["task1", "task2", "task3"],
            project_id="new_project"
        )
        
        mock_instance.batch_move_tasks.assert_called_once_with(
            task_ids=["task1", "task2", "task3"],
            project_id="new_project"
        )
        assert len(result["moved"]) == 3
        assert len(result["failed"]) == 0
    
    @pytest.mark.asyncio
    async def test_batch_move_tasks_to_section(self, server, mock_api_client):
        """Test batch moving tasks to a different section."""
        mock_instance = mock_api_client.return_value
        mock_instance.batch_move_tasks.return_value = {
            "moved": ["task1", "task2"],
            "failed": []
        }
        
        result = server.api.batch_move_tasks(
            task_ids=["task1", "task2"],
            section_id="section123"
        )
        
        mock_instance.batch_move_tasks.assert_called_once_with(
            task_ids=["task1", "task2"],
            section_id="section123"
        )
        assert result["moved"] == ["task1", "task2"]
    
    @pytest.mark.asyncio
    async def test_batch_move_tasks_partial_failure(self, server, mock_api_client):
        """Test batch move with some tasks failing."""
        mock_instance = mock_api_client.return_value
        mock_instance.batch_move_tasks.return_value = {
            "moved": ["task1", "task3"],
            "failed": [{"task_id": "task2", "error": "Task not found"}]
        }
        
        result = server.api.batch_move_tasks(
            task_ids=["task1", "task2", "task3"],
            project_id="proj123"
        )
        
        assert len(result["moved"]) == 2
        assert len(result["failed"]) == 1
        assert result["failed"][0]["task_id"] == "task2"
    
    @pytest.mark.asyncio
    async def test_batch_update_labels_tool_exists(self, server):
        """Test that batch_update_labels tool is registered."""
        tools = await server.mcp.get_tools()
        assert "batch_update_labels" in tools
    
    @pytest.mark.asyncio
    async def test_batch_update_labels_add(self, server, mock_api_client):
        """Test batch adding labels to multiple tasks."""
        mock_instance = mock_api_client.return_value
        mock_instance.batch_update_labels.return_value = {
            "updated": ["task1", "task2", "task3"],
            "failed": []
        }
        
        result = server.api.batch_update_labels(
            task_ids=["task1", "task2", "task3"],
            add_labels=["urgent", "work"]
        )
        
        mock_instance.batch_update_labels.assert_called_once_with(
            task_ids=["task1", "task2", "task3"],
            add_labels=["urgent", "work"]
        )
        assert len(result["updated"]) == 3
    
    @pytest.mark.asyncio
    async def test_batch_update_labels_remove(self, server, mock_api_client):
        """Test batch removing labels from multiple tasks."""
        mock_instance = mock_api_client.return_value
        mock_instance.batch_update_labels.return_value = {
            "updated": ["task1", "task2"],
            "failed": []
        }
        
        result = server.api.batch_update_labels(
            task_ids=["task1", "task2"],
            remove_labels=["low-priority"]
        )
        
        mock_instance.batch_update_labels.assert_called_once_with(
            task_ids=["task1", "task2"],
            remove_labels=["low-priority"]
        )
        assert result["updated"] == ["task1", "task2"]
    
    @pytest.mark.asyncio
    async def test_batch_update_labels_add_and_remove(self, server, mock_api_client):
        """Test batch adding and removing labels simultaneously."""
        mock_instance = mock_api_client.return_value
        mock_instance.batch_update_labels.return_value = {
            "updated": ["task1", "task2"],
            "failed": []
        }
        
        result = server.api.batch_update_labels(
            task_ids=["task1", "task2"],
            add_labels=["urgent"],
            remove_labels=["maybe", "someday"]
        )
        
        mock_instance.batch_update_labels.assert_called_once_with(
            task_ids=["task1", "task2"],
            add_labels=["urgent"],
            remove_labels=["maybe", "someday"]
        )
    
    @pytest.mark.asyncio
    async def test_batch_update_tasks_tool_exists(self, server):
        """Test that batch_update_tasks tool is registered."""
        tools = await server.mcp.get_tools()
        assert "batch_update_tasks" in tools
    
    @pytest.mark.asyncio
    async def test_batch_update_tasks_priority(self, server, mock_api_client):
        """Test batch updating priority for multiple tasks."""
        mock_instance = mock_api_client.return_value
        mock_instance.batch_update_tasks.return_value = {
            "updated": ["task1", "task2", "task3"],
            "failed": []
        }
        
        result = server.api.batch_update_tasks(
            task_ids=["task1", "task2", "task3"],
            priority=4
        )
        
        mock_instance.batch_update_tasks.assert_called_once_with(
            task_ids=["task1", "task2", "task3"],
            priority=4
        )
        assert len(result["updated"]) == 3
    
    @pytest.mark.asyncio
    async def test_batch_update_tasks_multiple_fields(self, server, mock_api_client):
        """Test batch updating multiple fields for tasks."""
        mock_instance = mock_api_client.return_value
        mock_instance.batch_update_tasks.return_value = {
            "updated": ["task1", "task2"],
            "failed": []
        }
        
        result = server.api.batch_update_tasks(
            task_ids=["task1", "task2"],
            priority=3,
            due_string="tomorrow",
            assignee_id="user123"
        )
        
        mock_instance.batch_update_tasks.assert_called_once_with(
            task_ids=["task1", "task2"],
            priority=3,
            due_string="tomorrow",
            assignee_id="user123"
        )
    
    @pytest.mark.asyncio
    async def test_batch_complete_tasks_tool_exists(self, server):
        """Test that batch_complete_tasks tool is registered."""
        tools = await server.mcp.get_tools()
        assert "batch_complete_tasks" in tools
    
    @pytest.mark.asyncio
    async def test_batch_complete_tasks(self, server, mock_api_client):
        """Test batch completing multiple tasks."""
        mock_instance = mock_api_client.return_value
        mock_instance.batch_complete_tasks.return_value = {
            "completed": ["task1", "task2", "task3", "task4"],
            "failed": []
        }
        
        result = server.api.batch_complete_tasks(
            task_ids=["task1", "task2", "task3", "task4"]
        )
        
        mock_instance.batch_complete_tasks.assert_called_once_with(
            task_ids=["task1", "task2", "task3", "task4"]
        )
        assert len(result["completed"]) == 4
        assert len(result["failed"]) == 0
    
    @pytest.mark.asyncio
    async def test_batch_complete_tasks_with_failures(self, server, mock_api_client):
        """Test batch complete with some failures."""
        mock_instance = mock_api_client.return_value
        mock_instance.batch_complete_tasks.return_value = {
            "completed": ["task1", "task3"],
            "failed": [
                {"task_id": "task2", "error": "Already completed"},
                {"task_id": "task4", "error": "Task not found"}
            ]
        }
        
        result = server.api.batch_complete_tasks(
            task_ids=["task1", "task2", "task3", "task4"]
        )
        
        assert len(result["completed"]) == 2
        assert len(result["failed"]) == 2
        assert any(f["task_id"] == "task2" for f in result["failed"])
        assert any(f["task_id"] == "task4" for f in result["failed"])
    
    @pytest.mark.asyncio
    async def test_batch_operations_empty_list(self, server, mock_api_client):
        """Test batch operations with empty task list."""
        mock_instance = mock_api_client.return_value
        mock_instance.batch_move_tasks.side_effect = ValueError("Task list cannot be empty")
        
        with pytest.raises(ValueError, match="Task list cannot be empty"):
            server.api.batch_move_tasks(task_ids=[], project_id="proj123")
    
    @pytest.mark.asyncio
    async def test_batch_operations_max_limit(self, server, mock_api_client):
        """Test batch operations respect maximum task limit."""
        # Create list of 101 task IDs (assuming 100 is the limit)
        task_ids = [f"task{i}" for i in range(101)]
        
        mock_instance = mock_api_client.return_value
        mock_instance.batch_complete_tasks.side_effect = ValueError("Maximum 100 tasks allowed per batch")
        
        with pytest.raises(ValueError, match="Maximum 100 tasks allowed"):
            server.api.batch_complete_tasks(task_ids=task_ids)
