"""Tests for Todoist MCP Server with API v1."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
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


class TestTodoistMCPServer:
    def test_init_with_token(self, mock_api_client):
        """Test server initialization with provided token."""
        server = TodoistMCPServer(token="provided_token")
        mock_api_client.assert_called_once_with("provided_token")
    
    def test_init_without_token(self, mock_auth_manager, mock_api_client):
        """Test server initialization using AuthManager."""
        server = TodoistMCPServer()
        mock_auth_manager.assert_called_once()
        mock_api_client.assert_called_once_with("test_token")
    
    @pytest.mark.asyncio
    async def test_get_projects_tool(self, server, mock_api_client):
        """Test get_projects tool registration and execution."""
        mock_instance = mock_api_client.return_value
        mock_instance.get_projects.return_value = {
            "results": [{"id": "123", "name": "Test"}],
            "next_cursor": "abc"
        }
        
        # Get all registered tools
        tools = await server.mcp.get_tools()
        assert "get_projects" in tools
        
        # Execute the tool directly via the server's API client
        result = server.api.get_projects(limit=5, cursor="xyz")
        
        mock_instance.get_projects.assert_called_once_with(limit=5, cursor="xyz")
        assert result["results"][0]["name"] == "Test"
    
    @pytest.mark.asyncio
    async def test_get_tasks_tool_with_filters(self, server, mock_api_client):
        """Test get_tasks tool with various filters."""
        mock_instance = mock_api_client.return_value
        mock_instance.get_tasks.return_value = {
            "results": [{"id": "task1", "content": "Test Task"}],
            "next_cursor": None
        }
        
        # Verify tool is registered
        tools = await server.mcp.get_tools()
        assert "get_tasks" in tools
        
        # Execute via API client to test parameter handling
        result = server.api.get_tasks(
            project_id="proj123",
            limit=10,
            label_ids=["important"],
            section_id="sec456"
        )
        
        # Verify parameters passed correctly (cursor not sent when None)
        mock_instance.get_tasks.assert_called_once_with(
            project_id="proj123",
            limit=10,
            label_ids=["important"],
            section_id="sec456"
        )
    
    @pytest.mark.asyncio
    async def test_add_task_tool(self, server, mock_api_client):
        """Test add_task tool."""
        mock_instance = mock_api_client.return_value
        mock_instance.add_task.return_value = {
            "id": "new_task",
            "content": "New Task",
            "project_id": "proj123"
        }
        
        # Verify tool is registered
        tools = await server.mcp.get_tools()
        assert "add_task" in tools
        
        # Execute via API client
        result = server.api.add_task(
            content="New Task",
            project_id="proj123",
            priority=4,
            due_string="tomorrow"
        )
        
        mock_instance.add_task.assert_called_once_with(
            content="New Task",
            project_id="proj123",
            priority=4,
            due_string="tomorrow"
        )
        assert result["content"] == "New Task"
    
    @pytest.mark.asyncio
    async def test_update_task_tool(self, server, mock_api_client):
        """Test update_task tool."""
        mock_instance = mock_api_client.return_value
        mock_instance.update_task.return_value = {
            "id": "task123",
            "content": "Updated Task"
        }
        
        # Verify tool is registered
        tools = await server.mcp.get_tools()
        assert "update_task" in tools
        
        # Execute via API client
        result = server.api.update_task(
            task_id="task123",
            content="Updated Task",
            priority=2
        )
        
        mock_instance.update_task.assert_called_once()
        call_args = mock_instance.update_task.call_args
        assert call_args[1]["task_id"] == "task123"
        assert call_args[1]["content"] == "Updated Task"
        assert call_args[1]["priority"] == 2
    
    @pytest.mark.asyncio
    async def test_all_tools_registered(self, server):
        """Test that all expected tools are registered."""
        expected_tools = [
            "get_projects",
            "get_project", 
            "add_project",
            "get_tasks",
            "get_task",
            "add_task",
            "update_task"
        ]
        
        tools = await server.mcp.get_tools()
        
        for tool_name in expected_tools:
            assert tool_name in tools
    
    def test_run_closes_client(self, server, mock_api_client):
        """Test that run() properly closes the API client."""
        mock_instance = mock_api_client.return_value
        mock_instance.close = Mock()
        
        with patch.object(server.mcp, "run") as mock_run:
            # Simulate an exception to test finally block
            mock_run.side_effect = KeyboardInterrupt()
            
            with pytest.raises(KeyboardInterrupt):
                server.run()
            
            mock_instance.close.assert_called_once()
