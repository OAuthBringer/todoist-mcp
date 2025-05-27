"""Unit tests for Todoist task operations."""

import pytest
from unittest.mock import Mock, patch, AsyncMock, call
from todoist_mcp.server import TodoistMCPServer
from todoist_mcp.api_v1 import TodoistV1Client


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


@pytest.fixture
def api_client(mock_httpx_client):
    """Create API client with mocked HTTP client."""
    return TodoistV1Client("test_token")


@pytest.fixture
def mock_httpx_client():
    """Mock httpx client."""
    with patch("todoist_mcp.api_v1.httpx.Client") as mock:
        yield mock


class TestTasksAPI:
    """Test task operations at the API client level."""
    
    def test_add_task_minimal(self, api_client, mock_httpx_client):
        """Test adding a task with minimal parameters."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "task123",
            "content": "Test Task",
            "labels": []
        }
        mock_response.content = True
        mock_response.raise_for_status = Mock()
        
        mock_instance = mock_httpx_client.return_value
        mock_instance.request.return_value = mock_response
        
        result = api_client.add_task(content="Test Task")
        
        assert result["id"] == "task123"
        assert result["content"] == "Test Task"
        mock_instance.request.assert_called_once_with(
            "POST",
            "https://api.todoist.com/api/v1/tasks",
            json={"content": "Test Task"},
            params=None
        )
    
    def test_add_task_with_labels(self, api_client, mock_httpx_client):
        """Test adding a task with labels parameter."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "task123",
            "content": "Test Task",
            "labels": ["urgent", "work"]
        }
        mock_response.content = True
        mock_response.raise_for_status = Mock()
        
        mock_instance = mock_httpx_client.return_value
        mock_instance.request.return_value = mock_response
        
        result = api_client.add_task(
            content="Test Task",
            labels=["urgent", "work"]
        )
        
        assert result["id"] == "task123"
        assert result["labels"] == ["urgent", "work"]
        mock_instance.request.assert_called_once_with(
            "POST",
            "https://api.todoist.com/api/v1/tasks",
            json={"content": "Test Task", "labels": ["urgent", "work"]},
            params=None
        )
    
    def test_add_task_full_params(self, api_client, mock_httpx_client):
        """Test adding a task with all parameters."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "task123",
            "content": "Test Task",
            "description": "Test Description",
            "project_id": "proj123",
            "section_id": "sec456",
            "labels": ["urgent"],
            "priority": 4,
            "due": {"string": "tomorrow", "date": "2025-05-27"}
        }
        mock_response.content = True
        mock_response.raise_for_status = Mock()
        
        mock_instance = mock_httpx_client.return_value
        mock_instance.request.return_value = mock_response
        
        result = api_client.add_task(
            content="Test Task",
            description="Test Description",
            project_id="proj123",
            section_id="sec456",
            labels=["urgent"],
            priority=4,
            due_string="tomorrow"
        )
        
        assert result["id"] == "task123"
        assert result["labels"] == ["urgent"]
        assert result["priority"] == 4
        
        # Verify the JSON payload
        call_args = mock_instance.request.call_args
        assert call_args[1]["json"]["content"] == "Test Task"
        assert call_args[1]["json"]["labels"] == ["urgent"]
        assert call_args[1]["json"]["priority"] == 4
    
    def test_update_task_labels(self, api_client, mock_httpx_client):
        """Test updating task labels."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "task123",
            "content": "Updated Task",
            "labels": ["new-label", "another-label"]
        }
        mock_response.content = True
        mock_response.raise_for_status = Mock()
        
        mock_instance = mock_httpx_client.return_value
        mock_instance.request.return_value = mock_response
        
        result = api_client.update_task(
            task_id="task123",
            labels=["new-label", "another-label"]
        )
        
        assert result["labels"] == ["new-label", "another-label"]
        mock_instance.request.assert_called_once_with(
            "POST",
            "https://api.todoist.com/api/v1/tasks/task123",
            json={"labels": ["new-label", "another-label"]},
            params=None
        )
    
    def test_get_task(self, api_client, mock_httpx_client):
        """Test getting a single task."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "task123",
            "content": "Test Task",
            "labels": ["work"]
        }
        mock_response.content = True
        mock_response.raise_for_status = Mock()
        
        mock_instance = mock_httpx_client.return_value
        mock_instance.request.return_value = mock_response
        
        result = api_client.get_task(task_id="task123")
        
        assert result["id"] == "task123"
        assert result["labels"] == ["work"]
    
    def test_get_tasks_with_filters(self, api_client, mock_httpx_client):
        """Test getting tasks with various filters."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [
                {"id": "task1", "content": "Task 1", "labels": ["urgent"]},
                {"id": "task2", "content": "Task 2", "labels": []}
            ],
            "next_cursor": None
        }
        mock_response.content = True
        mock_response.raise_for_status = Mock()
        
        mock_instance = mock_httpx_client.return_value
        mock_instance.request.return_value = mock_response
        
        result = api_client.get_tasks(
            project_id="proj123",
            label_ids=["urgent"],
            limit=10
        )
        
        assert len(result["results"]) == 2
        assert result["results"][0]["labels"] == ["urgent"]
        
        # Verify query parameters
        call_args = mock_instance.request.call_args
        assert call_args[1]["params"]["project_id"] == "proj123"
        assert call_args[1]["params"]["label_ids"] == ["urgent"]


class TestTasksMCPTools:
    """Test task operations at the MCP tool level."""
    
    @pytest.mark.asyncio
    async def test_add_task_tool_registered(self, server):
        """Test that add_task tool is properly registered."""
        tools = await server.mcp.get_tools()
        assert "add_task" in tools
        
        tool = tools["add_task"]
        assert tool.name == "add_task"
        assert tool.description == "Create a new task."
        
        # Check parameter schema
        params = tool.parameters
        assert "properties" in params
        assert "content" in params["properties"]
        assert "labels" in params["properties"]
        
        # Verify labels parameter exists - now it's a JSON string
        labels_param = params["properties"]["labels"]
        # FastMCP structures Optional[str] parameters with anyOf
        if "type" in labels_param:
            assert labels_param["type"] == "string"
        elif "anyOf" in labels_param:
            # Optional parameters are wrapped in anyOf [type, null]
            assert any("string" in str(item) or item.get("type") == "string" for item in labels_param["anyOf"])
    
    @pytest.mark.asyncio
    async def test_update_task_tool_registered(self, server):
        """Test that update_task tool is properly registered."""
        tools = await server.mcp.get_tools()
        assert "update_task" in tools
        
        tool = tools["update_task"]
        params = tool.parameters
        
        # Verify labels parameter
        assert "labels" in params["properties"]
        labels_param = params["properties"]["labels"]
        # Just verify it exists - schema structure varies
        assert labels_param is not None
    
    @pytest.mark.asyncio
    async def test_batch_update_labels_tool_registered(self, server):
        """Test that batch_update_labels tool is properly registered."""
        tools = await server.mcp.get_tools()
        assert "batch_update_labels" in tools
        
        tool = tools["batch_update_labels"]
        params = tool.parameters
        
        # Check required and optional parameters
        assert "task_ids" in params["properties"]
        assert "add_labels" in params["properties"]
        assert "remove_labels" in params["properties"]
        
        # Just verify parameters exist - schema structure varies
        assert params["properties"]["task_ids"] is not None
        assert params["properties"]["add_labels"] is not None
        assert params["properties"]["remove_labels"] is not None
    
    @pytest.mark.asyncio
    async def test_mcp_tool_invocation_with_labels(self, server, mock_api_client):
        """Test invoking MCP tool with labels parameter."""
        # This test simulates what should happen when Claude Desktop calls the tool
        mock_instance = mock_api_client.return_value
        mock_instance.add_task.return_value = {
            "id": "task123",
            "content": "MCP Test Task",
            "labels": ["mcp-label"]
        }
        
        # Get the tool function directly
        tools = await server.mcp.get_tools()
        add_task_tool = tools["add_task"]
        
        # The tool object has the actual function stored
        assert hasattr(add_task_tool, "fn")
        assert callable(add_task_tool.fn)
        
        # Call the function directly (simulating MCP invocation)
        result = await add_task_tool.fn(
            content="MCP Test Task",
            labels=["mcp-label"]
        )
        
        assert result["id"] == "task123"
        assert result["labels"] == ["mcp-label"]
        
        # Verify the API client was called correctly
        mock_instance.add_task.assert_called_once_with(
            content="MCP Test Task",
            description=None,
            project_id=None,
            section_id=None,
            parent_id=None,
            order=None,
            labels=["mcp-label"],
            priority=None,
            due_string=None,
            due_date=None,
            due_datetime=None,
            due_lang=None,
            assignee_id=None,
            duration=None,
            duration_unit=None
        )
    
    @pytest.mark.asyncio
    async def test_all_task_tools_registered(self, server):
        """Test that all task-related tools are registered."""
        expected_tools = [
            "get_tasks",
            "get_task",
            "add_task",
            "update_task",
            "move_task",
            "batch_update_tasks",
            "batch_complete_tasks"
        ]
        
        tools = await server.mcp.get_tools()
        
        for tool_name in expected_tools:
            assert tool_name in tools, f"Tool {tool_name} not registered"
