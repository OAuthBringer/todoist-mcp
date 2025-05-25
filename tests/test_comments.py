"""Tests for Todoist MCP Comment Support - TDD Failing Tests."""

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


class TestCommentSupport:
    """Test suite for comment CRUD operations - ALL SHOULD FAIL INITIALLY."""
    
    @pytest.mark.asyncio
    async def test_get_comments_tool_exists(self, server):
        """Test that get_comments tool is registered."""
        tools = await server.mcp.get_tools()
        assert "get_comments" in tools
    
    @pytest.mark.asyncio
    async def test_get_comments_for_task(self, server, mock_api_client):
        """Test retrieving comments for a specific task."""
        mock_instance = mock_api_client.return_value
        mock_instance.get_comments.return_value = {
            "results": [
                {
                    "id": "comment1",
                    "task_id": "task123",
                    "content": "This is a comment",
                    "posted": "2025-05-25T10:00:00Z"
                }
            ],
            "next_cursor": None
        }
        
        # Execute via API client
        result = server.api.get_comments(task_id="task123")
        
        mock_instance.get_comments.assert_called_once_with(task_id="task123")
        assert len(result["results"]) == 1
        assert result["results"][0]["content"] == "This is a comment"
    
    @pytest.mark.asyncio
    async def test_get_comments_for_project(self, server, mock_api_client):
        """Test retrieving comments for a specific project."""
        mock_instance = mock_api_client.return_value
        mock_instance.get_comments.return_value = {
            "results": [
                {
                    "id": "comment2",
                    "project_id": "proj123",
                    "content": "Project comment",
                    "posted": "2025-05-25T11:00:00Z"
                }
            ],
            "next_cursor": None
        }
        
        result = server.api.get_comments(project_id="proj123")
        
        mock_instance.get_comments.assert_called_once_with(project_id="proj123")
        assert result["results"][0]["project_id"] == "proj123"
    
    @pytest.mark.asyncio
    async def test_add_comment_tool_exists(self, server):
        """Test that add_comment tool is registered."""
        tools = await server.mcp.get_tools()
        assert "add_comment" in tools
    
    @pytest.mark.asyncio
    async def test_add_comment_to_task(self, server, mock_api_client):
        """Test adding a comment to a task."""
        mock_instance = mock_api_client.return_value
        mock_instance.add_comment.return_value = {
            "id": "new_comment",
            "task_id": "task123",
            "content": "New comment on task",
            "posted": "2025-05-25T12:00:00Z"
        }
        
        result = server.api.add_comment(
            content="New comment on task",
            task_id="task123"
        )
        
        mock_instance.add_comment.assert_called_once_with(
            content="New comment on task",
            task_id="task123"
        )
        assert result["content"] == "New comment on task"
        assert result["task_id"] == "task123"
    
    @pytest.mark.asyncio
    async def test_add_comment_to_project(self, server, mock_api_client):
        """Test adding a comment to a project."""
        mock_instance = mock_api_client.return_value
        mock_instance.add_comment.return_value = {
            "id": "new_comment2",
            "project_id": "proj123",
            "content": "New comment on project",
            "posted": "2025-05-25T12:30:00Z"
        }
        
        result = server.api.add_comment(
            content="New comment on project",
            project_id="proj123"
        )
        
        mock_instance.add_comment.assert_called_once_with(
            content="New comment on project",
            project_id="proj123"
        )
        assert result["project_id"] == "proj123"
    
    @pytest.mark.asyncio
    async def test_get_comment_tool_exists(self, server):
        """Test that get_comment tool is registered."""
        tools = await server.mcp.get_tools()
        assert "get_comment" in tools
    
    @pytest.mark.asyncio
    async def test_get_single_comment(self, server, mock_api_client):
        """Test retrieving a single comment by ID."""
        mock_instance = mock_api_client.return_value
        mock_instance.get_comment.return_value = {
            "id": "comment123",
            "content": "Single comment",
            "task_id": "task456",
            "posted": "2025-05-25T13:00:00Z"
        }
        
        result = server.api.get_comment(comment_id="comment123")
        
        mock_instance.get_comment.assert_called_once_with(comment_id="comment123")
        assert result["id"] == "comment123"
        assert result["content"] == "Single comment"
    
    @pytest.mark.asyncio
    async def test_update_comment_tool_exists(self, server):
        """Test that update_comment tool is registered."""
        tools = await server.mcp.get_tools()
        assert "update_comment" in tools
    
    @pytest.mark.asyncio
    async def test_update_comment(self, server, mock_api_client):
        """Test updating an existing comment."""
        mock_instance = mock_api_client.return_value
        mock_instance.update_comment.return_value = {
            "id": "comment123",
            "content": "Updated comment content",
            "task_id": "task456",
            "posted": "2025-05-25T13:00:00Z"
        }
        
        result = server.api.update_comment(
            comment_id="comment123",
            content="Updated comment content"
        )
        
        mock_instance.update_comment.assert_called_once()
        call_args = mock_instance.update_comment.call_args
        assert call_args[1]["comment_id"] == "comment123"
        assert call_args[1]["content"] == "Updated comment content"
        assert result["content"] == "Updated comment content"
    
    @pytest.mark.asyncio
    async def test_delete_comment_tool_exists(self, server):
        """Test that delete_comment tool is registered."""
        tools = await server.mcp.get_tools()
        assert "delete_comment" in tools
    
    @pytest.mark.asyncio
    async def test_delete_comment(self, server, mock_api_client):
        """Test deleting a comment."""
        mock_instance = mock_api_client.return_value
        # Todoist API typically returns no content on successful delete
        mock_instance.delete_comment.return_value = None
        
        result = server.api.delete_comment(comment_id="comment123")
        
        mock_instance.delete_comment.assert_called_once_with(comment_id="comment123")
        assert result is None  # Successful deletion returns None
    
    @pytest.mark.asyncio
    async def test_comment_pagination(self, server, mock_api_client):
        """Test pagination support for comments."""
        mock_instance = mock_api_client.return_value
        mock_instance.get_comments.return_value = {
            "results": [
                {"id": f"comment{i}", "content": f"Comment {i}"} 
                for i in range(10)
            ],
            "next_cursor": "next_page_token"
        }
        
        result = server.api.get_comments(
            task_id="task123",
            limit=10,
            cursor="current_page"
        )
        
        mock_instance.get_comments.assert_called_once_with(
            task_id="task123",
            limit=10,
            cursor="current_page"
        )
        assert len(result["results"]) == 10
        assert result["next_cursor"] == "next_page_token"
    
    @pytest.mark.asyncio
    async def test_comment_error_handling(self, server, mock_api_client):
        """Test error handling for comment operations."""
        mock_instance = mock_api_client.return_value
        mock_instance.add_comment.side_effect = Exception("API Error: Invalid task_id")
        
        with pytest.raises(Exception, match="API Error: Invalid task_id"):
            server.api.add_comment(
                content="This will fail",
                task_id="invalid_task"
            )
    
    @pytest.mark.asyncio
    async def test_comment_validation(self, server, mock_api_client):
        """Test validation - comment must be for either task or project, not both."""
        # Configure mock to raise the validation error
        mock_instance = mock_api_client.return_value
        mock_instance.add_comment.side_effect = ValueError("Comment must be for either task or project, not both")
        
        # This should raise an error when we implement validation
        with pytest.raises(ValueError, match="Comment must be for either task or project"):
            server.api.add_comment(
                content="Invalid comment",
                task_id="task123",
                project_id="proj123"  # Can't specify both!
            )
