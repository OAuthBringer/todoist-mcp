"""Live integration tests - no mocks, real API calls only."""

import pytest
import os
from todoist_mcp.server import TodoistMCPServer


@pytest.mark.integration
class TestLiveIntegration:
    """Live integration tests requiring real Todoist API."""
    
    @pytest.fixture(scope="class")
    def live_server(self):
        """Create server with real API token."""
        if not os.getenv('TODOIST_API_TOKEN'):
            pytest.skip("TODOIST_API_TOKEN not set - skipping live integration tests")
        
        return TodoistMCPServer()
    
    def test_live_server_initialization(self, live_server):
        """Test server initializes with live API."""
        assert live_server is not None
        assert hasattr(live_server, 'api')
        assert hasattr(live_server, 'mcp')
        
        # Verify all tools available
        expected_tools = [
            'get_projects', 'get_project', 'add_project',
            'get_tasks', 'get_task', 'add_task', 'update_task'
        ]
        for tool in expected_tools:
            assert live_server.has_tool(tool)
    
    def test_live_get_projects(self, live_server):
        """Test live API call to get projects."""
        projects = live_server.execute_tool('get_projects')
        
        assert isinstance(projects, list)
        assert len(projects) >= 1  # Should have at least Inbox
        
        project = projects[0]
        assert 'id' in project
        assert 'name' in project
    
    def test_live_get_tasks(self, live_server):
        """Test live API call to get tasks."""
        tasks = live_server.execute_tool('get_tasks')
        
        assert isinstance(tasks, list)
        # Tasks may be empty, just verify structure if any exist
        if tasks:
            task = tasks[0]
            assert 'id' in task
            assert 'content' in task
    
    def test_live_task_lifecycle(self, live_server):
        """Test complete task creation, update, cleanup."""
        # Create test task
        task_content = "Integration test task - safe to delete"
        new_task = live_server.execute_tool('add_task', content=task_content)
        
        assert new_task['content'] == task_content
        assert 'id' in new_task
        task_id = new_task['id']
        
        try:
            # Verify task exists
            retrieved_task = live_server.execute_tool('get_task', task_id=task_id)
            assert retrieved_task['id'] == task_id
            assert retrieved_task['content'] == task_content
            
            # Update task
            updated_content = "Updated integration test task"
            live_server.execute_tool('update_task', task_id=task_id, content=updated_content)
            
            # Verify update
            updated_task = live_server.execute_tool('get_task', task_id=task_id)
            assert updated_task['content'] == updated_content
            
        finally:
            # Cleanup - complete the task
            live_server.api.complete_task(task_id)
    
    def test_live_auth_methods(self):
        """Test different authentication methods."""
        token = os.getenv('TODOIST_API_TOKEN')
        if not token:
            pytest.skip("No token available for auth testing")
            
        # Test explicit token
        server_explicit = TodoistMCPServer(token=token)
        projects_explicit = server_explicit.execute_tool('get_projects')
        assert isinstance(projects_explicit, list)
        
        # Test environment-based auth
        server_env = TodoistMCPServer()
        projects_env = server_env.execute_tool('get_projects')
        assert isinstance(projects_env, list)
        
        # Should get same results
        assert len(projects_explicit) == len(projects_env)


class TestCodeQuality:
    """Code quality verification."""
    
    def test_clean_imports(self):
        """Test all imports work cleanly."""
        from todoist_mcp.server import TodoistMCPServer
        from todoist_mcp.auth import AuthManager
        
        assert TodoistMCPServer is not None
        assert AuthManager is not None
    
    def test_server_interface(self):
        """Test server provides expected interface."""
        # Test interface without requiring real token
        server = TodoistMCPServer(token="fake_token_for_interface_test")
        
        assert hasattr(server, 'has_tool')
        assert hasattr(server, 'execute_tool')
        assert callable(server.has_tool)
        assert callable(server.execute_tool)
        
        # Test tool checking
        assert server.has_tool('get_projects')
        assert not server.has_tool('nonexistent_tool')
    
    def test_auth_interface(self):
        """Test auth manager interface."""
        from todoist_mcp.auth import AuthManager
        
        auth = AuthManager()
        assert hasattr(auth, 'get_token')
        assert hasattr(auth, 'set_token')
        assert callable(auth.get_token)
        assert callable(auth.set_token)
        
        # Test runtime token
        auth.set_token('test_token')
        assert auth.get_token() == 'test_token'
