"""Integration tests for Todoist Task Move Support - Real API Testing."""

import pytest
import os
from dotenv import load_dotenv
from todoist_mcp.server import TodoistMCPServer
from .conftest_integration import test_project_manager, cleanup_test_projects

# Load environment variables
load_dotenv()


@pytest.fixture
def server():
    """Create server instance with real API token."""
    token = os.getenv("TODOIST_API_TOKEN")
    if not token:
        raise ValueError("TODOIST_API_TOKEN not found in environment")
    return TodoistMCPServer(token=token)


@pytest.fixture
def test_projects(server, test_project_manager):
    """Create test projects for move testing."""
    project1 = test_project_manager("Move_Source")
    project2 = test_project_manager("Move_Target")
    return (project1, project2)


@pytest.fixture
def test_task(server, test_projects):
    """Create a test task in source project."""
    source_project, _ = test_projects
    task = server.api.add_task(
        content="Task to Move",
        project_id=source_project["id"],
        labels=["test", "move"],
        priority=3
    )
    yield task


class TestMoveIntegration:
    """Integration tests for task move operations against real API."""
    
    @pytest.mark.integration
    def test_move_task_to_different_project(self, server, test_projects, test_task):
        """Test moving a task to a different project."""
        _, target_project = test_projects
        
        # Move task
        result = server.api.move_task(
            task_id=test_task["id"],
            project_id=target_project["id"]
        )
        
        assert result["id"] == test_task["id"]
        assert result["project_id"] == target_project["id"]
        assert result["content"] == "Task to Move"
        # Verify attributes preserved
        assert set(result["labels"]) == {"test", "move"}
        assert result["priority"] == 3
    
    @pytest.mark.integration
    def test_move_task_validation_no_target(self, server, test_task):
        """Test validation when no target specified."""
        with pytest.raises(ValueError, match="Must specify at least one"):
            server.api.move_task(task_id=test_task["id"])
    
    @pytest.mark.integration
    def test_move_task_to_invalid_project(self, server, test_task):
        """Test error handling for invalid project ID."""
        with pytest.raises(Exception) as exc_info:
            server.api.move_task(
                task_id=test_task["id"],
                project_id="invalid_project_id_99999"
            )
        # Todoist should return 400 or 404
        assert "400" in str(exc_info.value) or "404" in str(exc_info.value)
    
    @pytest.mark.integration
    def test_move_subtask_to_parent(self, server, test_projects):
        """Test moving a subtask under a different parent."""
        source_project, _ = test_projects
        
        # Create parent and child tasks
        parent1 = server.api.add_task(
            content="Parent Task 1",
            project_id=source_project["id"]
        )
        parent2 = server.api.add_task(
            content="Parent Task 2",
            project_id=source_project["id"]
        )
        subtask = server.api.add_task(
            content="Subtask to Move",
            project_id=source_project["id"],
            parent_id=parent1["id"]
        )
        
        # Move subtask to different parent
        result = server.api.move_task(
            task_id=subtask["id"],
            parent_id=parent2["id"]
        )
        
        assert result["parent_id"] == parent2["id"]
        assert result["content"] == "Subtask to Move"
    
    @pytest.mark.integration 
    def test_move_task_multiple_times(self, server, test_projects):
        """Test moving a task multiple times."""
        project1, project2 = test_projects
        
        # Create task
        task = server.api.add_task(
            content="Multi-Move Task",
            project_id=project1["id"]
        )
        
        # Move to project2
        result1 = server.api.move_task(
            task_id=task["id"],
            project_id=project2["id"]
        )
        assert result1["project_id"] == project2["id"]
        
        # Move back to project1
        result2 = server.api.move_task(
            task_id=task["id"],
            project_id=project1["id"]
        )
        assert result2["project_id"] == project1["id"]
    
    @pytest.mark.integration
    def test_move_task_preserves_comments(self, server, test_projects, test_task):
        """Test that comments are preserved when moving tasks."""
        _, target_project = test_projects
        
        # Add comment to task
        comment = server.api.add_comment(
            content="Comment on task before move",
            task_id=test_task["id"]
        )
        
        # Move task
        server.api.move_task(
            task_id=test_task["id"],
            project_id=target_project["id"]
        )
        
        # Verify comment still exists
        retrieved = server.api.get_comment(comment_id=comment["id"])
        assert retrieved["content"] == "Comment on task before move"
        assert retrieved["item_id"] == test_task["id"]
        
        # Cleanup
        server.api.delete_comment(comment_id=comment["id"])
    
    @pytest.mark.integration
    @pytest.mark.skip(reason="API v1 doesn't support updating task completion status")
    def test_move_completed_task(self, server, test_projects):
        """Test moving a completed task."""
        project1, project2 = test_projects
        
        # Create and complete task
        task = server.api.add_task(
            content="Completed Task to Move", 
            project_id=project1["id"]
        )
        # Complete task using correct field name
        completed = server.api.update_task(
            task_id=task["id"],
            checked=True
        )
        
        # Try to move completed task
        with pytest.raises(Exception) as exc_info:
            server.api.move_task(
                task_id=task["id"],
                project_id=project2["id"]
            )
        # API should reject moving completed tasks
        assert "400" in str(exc_info.value) or "completed" in str(exc_info.value).lower()
