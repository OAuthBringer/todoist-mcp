"""Tests for Labels CRUD operations - TDD Failing Tests."""

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


class TestLabelsSupport:
    """Test suite for labels CRUD operations - ALL SHOULD FAIL INITIALLY."""
    
    @pytest.mark.asyncio
    async def test_get_labels_tool_exists(self, server):
        """Test that get_labels tool is registered."""
        tools = await server.mcp.get_tools()
        assert "get_labels" in tools
    
    @pytest.mark.asyncio
    async def test_get_label_tool_exists(self, server):
        """Test that get_label tool is registered."""
        tools = await server.mcp.get_tools()
        assert "get_label" in tools
    
    @pytest.mark.asyncio
    async def test_add_label_tool_exists(self, server):
        """Test that add_label tool is registered."""
        tools = await server.mcp.get_tools()
        assert "add_label" in tools
    
    @pytest.mark.asyncio
    async def test_update_label_tool_exists(self, server):
        """Test that update_label tool is registered."""
        tools = await server.mcp.get_tools()
        assert "update_label" in tools
    
    @pytest.mark.asyncio
    async def test_delete_label_tool_exists(self, server):
        """Test that delete_label tool is registered."""
        tools = await server.mcp.get_tools()
        assert "delete_label" in tools
    
    @pytest.mark.asyncio
    async def test_get_labels_with_pagination(self, server, mock_api_client):
        """Test getting all labels with pagination support."""
        mock_instance = mock_api_client.return_value
        mock_instance.get_labels.return_value = {
            "results": [
                {
                    "id": "label1",
                    "name": "urgent",
                    "color": "#ff0000",
                    "order": 1
                },
                {
                    "id": "label2",
                    "name": "work",
                    "color": "#0000ff",
                    "order": 2
                }
            ],
            "next_cursor": "abc123"
        }
        
        result = server.api.get_labels(limit=10, cursor="xyz")
        
        mock_instance.get_labels.assert_called_once_with(
            limit=10,
            cursor="xyz"
        )
        assert len(result["results"]) == 2
        assert result["next_cursor"] == "abc123"
    
    @pytest.mark.asyncio
    async def test_get_label_by_id(self, server, mock_api_client):
        """Test getting a single label by ID."""
        mock_instance = mock_api_client.return_value
        mock_instance.get_label.return_value = {
            "id": "label123",
            "name": "important",
            "color": "#ff9900",
            "order": 1
        }
        
        result = server.api.get_label(label_id="label123")
        
        mock_instance.get_label.assert_called_once_with(label_id="label123")
        assert result["name"] == "important"
        assert result["color"] == "#ff9900"
        assert result["order"] == 1
    
    @pytest.mark.asyncio
    async def test_add_label_with_color_and_order(self, server, mock_api_client):
        """Test creating a new label with color and order."""
        mock_instance = mock_api_client.return_value
        mock_instance.add_label.return_value = {
            "id": "new_label",
            "name": "priority",
            "color": "#ff0000",
            "order": 5
        }
        
        result = server.api.add_label(
            name="priority",
            color="#ff0000",
            order=5
        )
        
        mock_instance.add_label.assert_called_once_with(
            name="priority",
            color="#ff0000",
            order=5
        )
        assert result["name"] == "priority"
        assert result["color"] == "#ff0000"
        assert result["order"] == 5
    
    @pytest.mark.asyncio
    async def test_add_label_minimal(self, server, mock_api_client):
        """Test creating a label with just name (color and order optional)."""
        mock_instance = mock_api_client.return_value
        mock_instance.add_label.return_value = {
            "id": "new_label",
            "name": "simple",
            "color": "#808080",  # Default color
            "order": 0  # Default order
        }
        
        result = server.api.add_label(name="simple")
        
        mock_instance.add_label.assert_called_once_with(name="simple")
        assert result["name"] == "simple"
    
    @pytest.mark.asyncio
    async def test_update_label_name(self, server, mock_api_client):
        """Test updating a label's name."""
        mock_instance = mock_api_client.return_value
        mock_instance.update_label.return_value = {
            "id": "label123",
            "name": "updated_name",
            "color": "#ff0000",
            "order": 1
        }
        
        result = server.api.update_label(
            label_id="label123",
            name="updated_name"
        )
        
        mock_instance.update_label.assert_called_once_with(
            label_id="label123",
            name="updated_name"
        )
        assert result["name"] == "updated_name"
    
    @pytest.mark.asyncio
    async def test_update_label_color(self, server, mock_api_client):
        """Test updating a label's color."""
        mock_instance = mock_api_client.return_value
        mock_instance.update_label.return_value = {
            "id": "label123",
            "name": "urgent",
            "color": "#00ff00",
            "order": 1
        }
        
        result = server.api.update_label(
            label_id="label123",
            color="#00ff00"
        )
        
        mock_instance.update_label.assert_called_once_with(
            label_id="label123",
            color="#00ff00"
        )
        assert result["color"] == "#00ff00"
    
    @pytest.mark.asyncio
    async def test_update_label_order(self, server, mock_api_client):
        """Test updating a label's order."""
        mock_instance = mock_api_client.return_value
        mock_instance.update_label.return_value = {
            "id": "label123",
            "name": "urgent",
            "color": "#ff0000",
            "order": 10
        }
        
        result = server.api.update_label(
            label_id="label123",
            order=10
        )
        
        mock_instance.update_label.assert_called_once_with(
            label_id="label123",
            order=10
        )
        assert result["order"] == 10
    
    @pytest.mark.asyncio
    async def test_update_label_multiple_fields(self, server, mock_api_client):
        """Test updating multiple label fields at once."""
        mock_instance = mock_api_client.return_value
        mock_instance.update_label.return_value = {
            "id": "label123",
            "name": "new_name",
            "color": "#123456",
            "order": 3
        }
        
        result = server.api.update_label(
            label_id="label123",
            name="new_name",
            color="#123456",
            order=3
        )
        
        mock_instance.update_label.assert_called_once_with(
            label_id="label123",
            name="new_name",
            color="#123456",
            order=3
        )
        assert result["name"] == "new_name"
        assert result["color"] == "#123456"
        assert result["order"] == 3
    
    @pytest.mark.asyncio
    async def test_delete_label(self, server, mock_api_client):
        """Test deleting a label."""
        mock_instance = mock_api_client.return_value
        mock_instance.delete_label.return_value = None
        
        # Should not raise an exception
        result = server.api.delete_label(label_id="label123")
        
        mock_instance.delete_label.assert_called_once_with(label_id="label123")
        assert result is None
    
    @pytest.mark.asyncio
    async def test_labels_integration_with_tasks(self, server, mock_api_client):
        """Test that task operations properly handle label IDs."""
        mock_instance = mock_api_client.return_value
        # When adding a task with labels
        mock_instance.add_task.return_value = {
            "id": "task123",
            "content": "Task with labels",
            "labels": ["urgent", "work"]  # Label names/IDs
        }
        
        result = server.api.add_task(
            content="Task with labels",
            labels=["urgent", "work"]
        )
        
        mock_instance.add_task.assert_called_once_with(
            content="Task with labels",
            labels=["urgent", "work"]
        )
        assert result["labels"] == ["urgent", "work"]
    
    @pytest.mark.asyncio
    async def test_get_labels_empty_response(self, server, mock_api_client):
        """Test handling empty labels list."""
        mock_instance = mock_api_client.return_value
        mock_instance.get_labels.return_value = {
            "results": [],
            "next_cursor": None
        }
        
        result = server.api.get_labels()
        
        assert result["results"] == []
        assert result["next_cursor"] is None
    
    @pytest.mark.asyncio
    async def test_label_color_validation(self, server, mock_api_client):
        """Test that invalid color format raises error."""
        mock_instance = mock_api_client.return_value
        mock_instance.add_label.side_effect = ValueError("Invalid color format")
        
        with pytest.raises(ValueError, match="Invalid color format"):
            server.api.add_label(name="test", color="not-a-color")
