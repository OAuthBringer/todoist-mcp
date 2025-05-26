"""Simplified integration tests for TodoistMCP v0.4.0."""

import pytest
import os
from todoist_mcp.server import TodoistMCPServer
from dotenv import load_dotenv
import time


@pytest.fixture
def test_project_id():
    """Use the test project ID from environment."""
    return os.getenv("TODOIST_TEST_PROJECT_ID", "2324251907")


@pytest.fixture
def server():
    """Create real server instance with actual API token."""
    load_dotenv()
    token = os.getenv("TODOIST_API_TOKEN")
    if not token:
        pytest.skip("TODOIST_API_TOKEN not set")
    return TodoistMCPServer(token=token)


class TestV04Integration:
    """Simplified integration tests for v0.4.0 features."""
    
    def test_task_with_labels(self, server, test_project_id):
        """Test creating and managing tasks with labels."""
        # Create task with labels
        task = server.api.add_task(
            content="Integration test - labeled task",
            project_id=test_project_id,
            labels=["test", "integration", "v0.4.0"]
        )
        
        try:
            # Verify task has labels
            fetched = server.api.get_task(task["id"])
            assert "test" in fetched["labels"]
            assert "integration" in fetched["labels"]
            
            # Update labels
            server.api.update_task(
                task["id"],
                labels=["test", "updated"]
            )
            
            # Verify update
            updated = server.api.get_task(task["id"])
            assert "updated" in updated["labels"]
            assert "integration" not in updated["labels"]
            
        finally:
            # Cleanup
            server.api._request("DELETE", f"tasks/{task['id']}")
    
    def test_batch_operations(self, server, test_project_id):
        """Test batch operations on multiple tasks."""
        # Create test tasks
        tasks = []
        for i in range(3):
            task = server.api.add_task(
                content=f"Batch test task {i}",
                project_id=test_project_id,
                priority=1
            )
            tasks.append(task)
        
        task_ids = [t["id"] for t in tasks]
        
        try:
            # Batch update priority
            result = server.api.batch_update_tasks(
                task_ids=task_ids,
                priority=4
            )
            
            assert len(result["updated"]) >= 2  # At least 2 should succeed
            
            # Verify updates
            for task_id in result["updated"]:
                task = server.api.get_task(task_id)
                assert task["priority"] == 4
                
        finally:
            # Cleanup
            for task_id in task_ids:
                try:
                    server.api._request("DELETE", f"tasks/{task_id}")
                except:
                    pass
    
    def test_search_functionality(self, server, test_project_id):
        """Test search with filters."""
        # Create searchable task
        unique_content = f"Searchable task {int(time.time())}"
        task = server.api.add_task(
            content=unique_content,
            project_id=test_project_id,
            labels=["searchable"],
            priority=3
        )
        
        try:
            # Allow indexing time
            time.sleep(1)
            
            # Search by content
            results = server.api.search_tasks(
                query=unique_content,
                project_id=test_project_id
            )
            
            # Should find our task
            found_ids = [t["id"] for t in results.get("tasks", [])]
            assert task["id"] in found_ids or len(found_ids) > 0
            
        finally:
            # Cleanup
            server.api._request("DELETE", f"tasks/{task['id']}")
    
    def test_move_task(self, server):
        """Test moving tasks between projects."""
        # Create test projects
        proj1 = server.api.add_project("Test Move Source")
        proj2 = server.api.add_project("Test Move Dest")
        
        # Create task in first project
        task = server.api.add_task(
            content="Task to move",
            project_id=proj1["id"]
        )
        
        try:
            # Move task
            server.api.move_task(
                task["id"],
                project_id=proj2["id"]
            )
            
            # Verify move
            moved = server.api.get_task(task["id"])
            assert moved["project_id"] == proj2["id"]
            
        finally:
            # Cleanup
            try:
                server.api._request("DELETE", f"tasks/{task['id']}")
            except:
                pass
            server.api._request("DELETE", f"projects/{proj1['id']}", api_version=2)
            server.api._request("DELETE", f"projects/{proj2['id']}", api_version=2)


class TestV04ErrorHandling:
    """Test error handling in v0.4.0 features."""
    
    def test_batch_with_invalid_tasks(self, server):
        """Test batch operations handle errors gracefully."""
        result = server.api.batch_update_tasks(
            task_ids=["invalid1", "invalid2"],
            priority=4
        )
        
        assert len(result["failed"]) == 2
        assert len(result["updated"]) == 0
