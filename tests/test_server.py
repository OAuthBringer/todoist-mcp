"""Test core FastMCP tool generation functionality."""

import pytest
from unittest.mock import Mock, patch
from fastmcp import FastMCP
from todoist_api_python.api import TodoistAPI
from todoist_mcp.server import TodoistMCPServer


class TestTodoistMCPServer:
    """Test core server functionality."""
    
    def test_server_initialization(self):
        """Test server initializes with TodoistAPI."""
        with patch('todoist_mcp.server.TodoistAPI') as mock_api_class:
            server = TodoistMCPServer("test_token")
            
            assert server is not None
            assert hasattr(server, 'mcp')
            assert isinstance(server.mcp, FastMCP)
            mock_api_class.assert_called_once_with("test_token")
    
    def test_auto_tool_generation(self):
        """Test tools are auto-generated from TodoistAPI methods."""
        with patch('todoist_api_python.api.TodoistAPI') as mock_api_class:
            server = TodoistMCPServer("test_token")
            
            # Should have tools for key API methods
            expected_tools = [
                'get_projects', 'get_project', 'add_project',
                'get_tasks', 'get_task', 'add_task', 'update_task'
            ]
            
            for tool_name in expected_tools:
                assert server.has_tool(tool_name), f"Missing tool: {tool_name}"
    
    def test_tool_execution_calls_api(self, mock_todoist_api):
        """Test tool execution calls underlying API method."""
        with patch('todoist_mcp.server.TodoistAPI', return_value=mock_todoist_api):
            server = TodoistMCPServer("test_token")
            
            # Execute get_projects tool
            result = server.execute_tool('get_projects')
            
            mock_todoist_api.get_projects.assert_called_once()
            assert result == mock_todoist_api.get_projects.return_value
    
    def test_tool_execution_with_args(self, mock_todoist_api):
        """Test tool execution passes arguments to API method."""
        with patch('todoist_mcp.server.TodoistAPI', return_value=mock_todoist_api):
            server = TodoistMCPServer("test_token")
            
            # Execute add_task tool with arguments
            server.execute_tool('add_task', content="Test task", project_id="proj_1")
            
            mock_todoist_api.add_task.assert_called_once_with(
                content="Test task", project_id="proj_1"
            )
    
    def test_private_methods_excluded(self):
        """Test private methods are not exposed as tools."""
        with patch('todoist_api_python.api.TodoistAPI') as mock_api_class:
            server = TodoistMCPServer("test_token")
            
            # Private methods should not be tools
            assert not server.has_tool('_private_method')
            assert not server.has_tool('__init__')
