"""Tests for Task Search Functionality - TDD Failing Tests."""

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


class TestTaskSearch:
    """Test suite for task search functionality - ALL SHOULD FAIL INITIALLY."""
    
    @pytest.mark.asyncio
    async def test_search_tasks_tool_exists(self, server):
        """Test that search_tasks tool is registered."""
        tools = await server.mcp.get_tools()
        assert "search_tasks" in tools
    
    @pytest.mark.asyncio
    async def test_search_by_content(self, server, mock_api_client):
        """Test searching tasks by content/text."""
        mock_instance = mock_api_client.return_value
        mock_instance.search_tasks.return_value = {
            "tasks": [
                {"id": "task1", "content": "Buy groceries for dinner"},
                {"id": "task2", "content": "Prepare dinner for guests"}
            ],
            "total_count": 2
        }
        
        result = server.api.search_tasks(query="dinner")
        
        mock_instance.search_tasks.assert_called_once_with(query="dinner")
        assert len(result["tasks"]) == 2
        assert all("dinner" in task["content"].lower() for task in result["tasks"])
    
    @pytest.mark.asyncio
    async def test_search_by_labels(self, server, mock_api_client):
        """Test searching tasks by labels."""
        mock_instance = mock_api_client.return_value
        mock_instance.search_tasks.return_value = {
            "tasks": [
                {"id": "task1", "content": "Review PR", "labels": ["urgent", "work"]},
                {"id": "task2", "content": "Deploy hotfix", "labels": ["urgent"]}
            ],
            "total_count": 2
        }
        
        result = server.api.search_tasks(labels=["urgent"])
        
        mock_instance.search_tasks.assert_called_once_with(labels=["urgent"])
        assert len(result["tasks"]) == 2
        assert all("urgent" in task["labels"] for task in result["tasks"])
    
    @pytest.mark.asyncio
    async def test_search_by_priority(self, server, mock_api_client):
        """Test searching tasks by priority level."""
        mock_instance = mock_api_client.return_value
        mock_instance.search_tasks.return_value = {
            "tasks": [
                {"id": "task1", "content": "Critical bug fix", "priority": 4},
                {"id": "task2", "content": "Security update", "priority": 4}
            ],
            "total_count": 2
        }
        
        result = server.api.search_tasks(priority=4)
        
        mock_instance.search_tasks.assert_called_once_with(priority=4)
        assert len(result["tasks"]) == 2
        assert all(task["priority"] == 4 for task in result["tasks"])
    
    @pytest.mark.asyncio
    async def test_search_by_due_date(self, server, mock_api_client):
        """Test searching tasks by due date."""
        mock_instance = mock_api_client.return_value
        mock_instance.search_tasks.return_value = {
            "tasks": [
                {"id": "task1", "content": "Submit report", "due": {"date": "2025-05-30"}},
                {"id": "task2", "content": "Team meeting", "due": {"date": "2025-05-30"}}
            ],
            "total_count": 2
        }
        
        result = server.api.search_tasks(due_date="2025-05-30")
        
        mock_instance.search_tasks.assert_called_once_with(due_date="2025-05-30")
        assert len(result["tasks"]) == 2
        assert all(task["due"]["date"] == "2025-05-30" for task in result["tasks"])
    
    @pytest.mark.asyncio
    async def test_search_by_date_range(self, server, mock_api_client):
        """Test searching tasks within a date range."""
        mock_instance = mock_api_client.return_value
        mock_instance.search_tasks.return_value = {
            "tasks": [
                {"id": "task1", "content": "Q2 planning", "due": {"date": "2025-05-28"}},
                {"id": "task2", "content": "Review budget", "due": {"date": "2025-05-29"}}
            ],
            "total_count": 2
        }
        
        result = server.api.search_tasks(
            due_after="2025-05-27",
            due_before="2025-05-31"
        )
        
        mock_instance.search_tasks.assert_called_once_with(
            due_after="2025-05-27",
            due_before="2025-05-31"
        )
        assert len(result["tasks"]) == 2
    
    @pytest.mark.asyncio
    async def test_search_with_multiple_filters(self, server, mock_api_client):
        """Test searching with multiple filter criteria."""
        mock_instance = mock_api_client.return_value
        mock_instance.search_tasks.return_value = {
            "tasks": [
                {"id": "task1", "content": "Fix critical bug", "priority": 4, "labels": ["bug"]}
            ],
            "total_count": 1
        }
        
        result = server.api.search_tasks(
            query="bug",
            priority=4,
            labels=["bug"]
        )
        
        mock_instance.search_tasks.assert_called_once_with(
            query="bug",
            priority=4,
            labels=["bug"]
        )
        assert len(result["tasks"]) == 1
        assert result["tasks"][0]["content"] == "Fix critical bug"
    
    @pytest.mark.asyncio
    async def test_search_with_project_filter(self, server, mock_api_client):
        """Test searching tasks within a specific project."""
        mock_instance = mock_api_client.return_value
        mock_instance.search_tasks.return_value = {
            "tasks": [
                {"id": "task1", "content": "Update README", "project_id": "proj123"}
            ],
            "total_count": 1
        }
        
        result = server.api.search_tasks(
            query="README",
            project_id="proj123"
        )
        
        mock_instance.search_tasks.assert_called_once_with(
            query="README",
            project_id="proj123"
        )
        assert result["tasks"][0]["project_id"] == "proj123"
    
    @pytest.mark.asyncio
    async def test_search_with_pagination(self, server, mock_api_client):
        """Test search with pagination support."""
        mock_instance = mock_api_client.return_value
        mock_instance.search_tasks.return_value = {
            "tasks": [{"id": f"task{i}", "content": f"Task {i}"} for i in range(10)],
            "total_count": 50,
            "next_cursor": "cursor123"
        }
        
        result = server.api.search_tasks(query="Task", limit=10)
        
        mock_instance.search_tasks.assert_called_once_with(query="Task", limit=10)
        assert len(result["tasks"]) == 10
        assert result["total_count"] == 50
        assert result["next_cursor"] == "cursor123"
    
    @pytest.mark.asyncio
    async def test_search_with_cursor(self, server, mock_api_client):
        """Test search with cursor for pagination."""
        mock_instance = mock_api_client.return_value
        mock_instance.search_tasks.return_value = {
            "tasks": [{"id": f"task{i}", "content": f"Task {i}"} for i in range(10, 20)],
            "total_count": 50,
            "next_cursor": "cursor456"
        }
        
        result = server.api.search_tasks(
            query="Task",
            limit=10,
            cursor="cursor123"
        )
        
        mock_instance.search_tasks.assert_called_once_with(
            query="Task",
            limit=10,
            cursor="cursor123"
        )
        assert len(result["tasks"]) == 10
        assert result["tasks"][0]["id"] == "task10"
    
    @pytest.mark.asyncio
    async def test_search_empty_results(self, server, mock_api_client):
        """Test search returning no results."""
        mock_instance = mock_api_client.return_value
        mock_instance.search_tasks.return_value = {
            "tasks": [],
            "total_count": 0
        }
        
        result = server.api.search_tasks(query="nonexistent")
        
        assert result["tasks"] == []
        assert result["total_count"] == 0
    
    @pytest.mark.asyncio
    async def test_search_by_completed_status(self, server, mock_api_client):
        """Test searching for completed vs active tasks."""
        mock_instance = mock_api_client.return_value
        mock_instance.search_tasks.return_value = {
            "tasks": [
                {"id": "task1", "content": "Completed task", "is_completed": True}
            ],
            "total_count": 1
        }
        
        result = server.api.search_tasks(is_completed=True)
        
        mock_instance.search_tasks.assert_called_once_with(is_completed=True)
        assert all(task["is_completed"] for task in result["tasks"])
    
    @pytest.mark.asyncio
    async def test_search_by_assignee(self, server, mock_api_client):
        """Test searching tasks by assignee."""
        mock_instance = mock_api_client.return_value
        mock_instance.search_tasks.return_value = {
            "tasks": [
                {"id": "task1", "content": "Code review", "assignee_id": "user123"}
            ],
            "total_count": 1
        }
        
        result = server.api.search_tasks(assignee_id="user123")
        
        mock_instance.search_tasks.assert_called_once_with(assignee_id="user123")
        assert result["tasks"][0]["assignee_id"] == "user123"
    
    @pytest.mark.asyncio
    async def test_search_with_sorting(self, server, mock_api_client):
        """Test search with sort options."""
        mock_instance = mock_api_client.return_value
        mock_instance.search_tasks.return_value = {
            "tasks": [
                {"id": "task1", "content": "A task", "created_at": "2025-05-26T10:00:00Z"},
                {"id": "task2", "content": "B task", "created_at": "2025-05-26T09:00:00Z"}
            ],
            "total_count": 2
        }
        
        result = server.api.search_tasks(
            query="task",
            sort_by="created_at",
            sort_order="desc"
        )
        
        mock_instance.search_tasks.assert_called_once_with(
            query="task",
            sort_by="created_at",
            sort_order="desc"
        )
        assert result["tasks"][0]["id"] == "task1"  # Newer task first
    
    @pytest.mark.asyncio
    async def test_search_validation_errors(self, server, mock_api_client):
        """Test search parameter validation."""
        mock_instance = mock_api_client.return_value
        
        # Test invalid priority
        mock_instance.search_tasks.side_effect = ValueError("Priority must be between 1 and 4")
        
        with pytest.raises(ValueError, match="Priority must be between 1 and 4"):
            server.api.search_tasks(priority=5)
        
        # Test invalid date format
        mock_instance.search_tasks.side_effect = ValueError("Invalid date format")
        
        with pytest.raises(ValueError, match="Invalid date format"):
            server.api.search_tasks(due_date="invalid-date")
