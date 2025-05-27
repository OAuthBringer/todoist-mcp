"""Test suite for sections management functionality."""

import pytest
from unittest.mock import patch


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
    from todoist_mcp.server import TodoistMCPServer
    return TodoistMCPServer()


class TestSectionsSupport:
    """Test suite for sections operations."""
    
    @pytest.mark.asyncio
    async def test_get_sections_tool_exists(self, server):
        """Test that get_sections tool is registered."""
        tools = await server.mcp.get_tools()
        assert "get_sections" in tools
    
    @pytest.mark.asyncio
    async def test_get_section_tool_exists(self, server):
        """Test that get_section tool is registered."""
        tools = await server.mcp.get_tools()
        assert "get_section" in tools
    
    @pytest.mark.asyncio
    async def test_add_section_tool_exists(self, server):
        """Test that add_section tool is registered."""
        tools = await server.mcp.get_tools()
        assert "add_section" in tools
    
    @pytest.mark.asyncio
    async def test_update_section_tool_exists(self, server):
        """Test that update_section tool is registered."""
        tools = await server.mcp.get_tools()
        assert "update_section" in tools
    
    @pytest.mark.asyncio
    async def test_delete_section_tool_exists(self, server):
        """Test that delete_section tool is registered."""
        tools = await server.mcp.get_tools()
        assert "delete_section" in tools
    
    @pytest.mark.asyncio
    async def test_get_sections(self, server, mock_api_client):
        """Test getting all sections for a project."""
        # Setup mock response
        mock_instance = mock_api_client.return_value
        mock_instance.get_sections.return_value = [
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
        
        # Execute via server.api
        sections = server.api.get_sections("2203306141")
        
        # Verify
        assert len(sections) == 2
        assert sections[0]["name"] == "Groceries"
        assert sections[1]["name"] == "Household"
        mock_instance.get_sections.assert_called_once_with(
            "2203306141"
        )
    
    @pytest.mark.asyncio
    async def test_get_sections_with_pagination(self, server, mock_api_client):
        """Test getting sections with pagination parameters."""
        # Setup mock
        mock_instance = mock_api_client.return_value
        mock_instance.get_sections.return_value = [
            {"id": "7025", "name": "Section 1"},
            {"id": "7026", "name": "Section 2"}
        ]
        
        # Execute with pagination
        sections = server.api.get_sections("2203306141", limit=50, cursor="test_cursor")
        
        # Verify
        assert len(sections) == 2
        mock_instance.get_sections.assert_called_once_with(
            "2203306141", limit=50, cursor="test_cursor"
        )
    
    @pytest.mark.asyncio
    async def test_get_section(self, server, mock_api_client):
        """Test getting a single section by ID."""
        # Setup mock
        mock_instance = mock_api_client.return_value
        mock_instance.get_section.return_value = {
            "id": "7025",
            "project_id": "2203306141",
            "order": 1,
            "name": "Groceries"
        }
        
        # Execute
        section = server.api.get_section("7025")
        
        # Verify
        assert section["id"] == "7025"
        assert section["name"] == "Groceries"
        mock_instance.get_section.assert_called_once_with("7025")
    
    @pytest.mark.asyncio
    async def test_add_section(self, server, mock_api_client):
        """Test creating a new section."""
        # Setup mock
        mock_instance = mock_api_client.return_value
        mock_instance.add_section.return_value = {
            "id": "7027",
            "project_id": "2203306141",
            "order": 3,
            "name": "Electronics"
        }
        
        # Execute
        section = server.api.add_section("2203306141", "Electronics", order=3)
        
        # Verify
        assert section["id"] == "7027"
        assert section["name"] == "Electronics"
        assert section["order"] == 3
        mock_instance.add_section.assert_called_once_with(
            "2203306141", "Electronics", order=3
        )
    
    @pytest.mark.asyncio
    async def test_add_section_without_order(self, server, mock_api_client):
        """Test creating a section without specifying order."""
        # Setup mock
        mock_instance = mock_api_client.return_value
        mock_instance.add_section.return_value = {
            "id": "7028",
            "project_id": "2203306141",
            "order": 4,
            "name": "Books"
        }
        
        # Execute
        section = server.api.add_section("2203306141", "Books")
        
        # Verify
        assert section["name"] == "Books"
        mock_instance.add_section.assert_called_once_with(
            "2203306141", "Books"
        )
    
    @pytest.mark.asyncio
    async def test_update_section(self, server, mock_api_client):
        """Test updating a section's name."""
        # Setup mock
        mock_instance = mock_api_client.return_value
        mock_instance.update_section.return_value = None  # 204 returns None
        
        # Execute
        result = server.api.update_section("7025", "Fresh Produce")
        
        # Verify
        assert result is None
        mock_instance.update_section.assert_called_once_with(
            "7025", "Fresh Produce"
        )
    
    @pytest.mark.asyncio
    async def test_delete_section(self, server, mock_api_client):
        """Test deleting a section."""
        # Setup mock
        mock_instance = mock_api_client.return_value
        mock_instance.delete_section.return_value = None  # 204 returns None
        
        # Execute
        result = server.api.delete_section("7025")
        
        # Verify
        assert result is None
        mock_instance.delete_section.assert_called_once_with("7025")
    
    @pytest.mark.asyncio
    async def test_section_error_handling(self, server, mock_api_client):
        """Test error handling for sections."""
        # Setup mock to raise exception
        mock_instance = mock_api_client.return_value
        mock_instance.get_sections.side_effect = Exception("Project not found")
        
        # Execute and verify
        with pytest.raises(Exception) as excinfo:
            server.api.get_sections("invalid_project")
        
        assert "Project not found" in str(excinfo.value)
    
    @pytest.mark.asyncio
    async def test_update_section_validation(self, server, mock_api_client):
        """Test section update validation."""
        # Setup mock to raise ValueError
        mock_instance = mock_api_client.return_value
        mock_instance.update_section.side_effect = ValueError("Section name cannot be empty")
        
        # Execute and verify
        with pytest.raises(ValueError) as excinfo:
            server.api.update_section("7025", "")
        
        assert "Section name cannot be empty" in str(excinfo.value)
