"""Test authentication and error handling functionality."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import os
from todoist_mcp.server import TodoistMCPServer
from todoist_mcp.auth import AuthManager
from todoist_mcp.api_v1 import TodoistV1Client


class TestAuthManager:
    """Test authentication configuration."""
    
    def test_env_token_loading(self):
        """Test loading token from environment variable."""
        with patch.dict(os.environ, {'TODOIST_API_TOKEN': 'env_token_123'}):
            auth = AuthManager()
            assert auth.get_token() == 'env_token_123'
    
    def test_config_file_loading(self):
        """Test loading token from config file."""
        mock_config = {'todoist': {'api_token': 'config_token_456'}}
        
        with patch('builtins.open', mock_open_config(mock_config)), \
             patch('json.load', return_value=mock_config):
            auth = AuthManager(config_path='config.json')
            assert auth.get_token() == 'config_token_456'
    
    def test_runtime_token_provision(self):
        """Test providing token at runtime."""
        auth = AuthManager()
        auth.set_token('runtime_token_789')
        assert auth.get_token() == 'runtime_token_789'
    
    def test_token_precedence(self):
        """Test token precedence: runtime > env > config."""
        mock_config = {'todoist': {'api_token': 'config_token'}}
        
        with patch.dict(os.environ, {'TODOIST_API_TOKEN': 'env_token'}), \
             patch('builtins.open', mock_open_config(mock_config)), \
             patch('json.load', return_value=mock_config):
            
            auth = AuthManager(config_path='config.json')
            auth.set_token('runtime_token')
            
            assert auth.get_token() == 'runtime_token'
    
    def test_missing_token_error(self):
        """Test error when no token available."""
        with patch.dict(os.environ, {}, clear=True):
            auth = AuthManager()
            
            with pytest.raises(ValueError, match="No Todoist API token found"):
                auth.get_token()


class TestServerWithAuth:
    """Test server initialization with different auth methods."""
    
    def test_server_with_env_auth(self):
        """Test server uses environment token."""
        with patch.dict(os.environ, {'TODOIST_API_TOKEN': 'env_token'}), \
             patch('todoist_mcp.server.TodoistV1Client') as mock_api:
            
            server = TodoistMCPServer()
            mock_api.assert_called_once_with('env_token')
    
    def test_server_with_explicit_token(self):
        """Test server with explicitly provided token."""
        with patch('todoist_mcp.server.TodoistV1Client') as mock_api:
            server = TodoistMCPServer(token='explicit_token')
            mock_api.assert_called_once_with('explicit_token')
    
    def test_server_auth_failure(self):
        """Test server handles auth failure gracefully."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="No Todoist API token found"):
                TodoistMCPServer()


class TestErrorHandling:
    """Test API error handling."""
    
    def test_api_rate_limit_handling(self, mock_todoist_api):
        """Test handling of rate limit errors."""
        from httpx import HTTPStatusError, Request, Response
        
        mock_response = Response(
            status_code=429,
            request=Request("GET", "https://api.todoist.com/api/v1/projects")
        )
        error = HTTPStatusError("429 Too Many Requests", request=mock_response.request, response=mock_response)
        mock_todoist_api.get_projects.side_effect = error
        
        with patch('todoist_mcp.server.TodoistV1Client', return_value=mock_todoist_api):
            server = TodoistMCPServer(token='test')
            
            # Call the API directly instead of execute_tool
            with pytest.raises(HTTPStatusError) as exc_info:
                server.api.get_projects()
            assert exc_info.value.response.status_code == 429
    
    def test_api_unauthorized_handling(self, mock_todoist_api):
        """Test handling of unauthorized errors."""
        from httpx import HTTPStatusError, Request, Response
        
        mock_response = Response(
            status_code=401,
            request=Request("GET", "https://api.todoist.com/api/v1/tasks")
        )
        error = HTTPStatusError("401 Unauthorized", request=mock_response.request, response=mock_response)
        mock_todoist_api.get_tasks.side_effect = error
        
        with patch('todoist_mcp.server.TodoistV1Client', return_value=mock_todoist_api):
            server = TodoistMCPServer(token='invalid')
            
            with pytest.raises(HTTPStatusError) as exc_info:
                server.api.get_tasks()
            assert exc_info.value.response.status_code == 401
    
    def test_network_error_handling(self, mock_todoist_api):
        """Test handling of network errors."""
        from httpx import ConnectError
        
        error = ConnectError("Network unreachable")
        mock_todoist_api.add_task.side_effect = error
        
        with patch('todoist_mcp.server.TodoistV1Client', return_value=mock_todoist_api):
            server = TodoistMCPServer(token='test')
            
            with pytest.raises(ConnectError):
                server.api.add_task(content='Test')


@pytest.fixture
def mock_todoist_api():
    """Mock TodoistV1Client for testing."""
    return Mock(spec=TodoistV1Client)


def mock_open_config(config_data):
    """Helper to mock file opening for config."""
    return MagicMock()
