"""Integration tests for Todoist Batch Operations - Real API Testing."""

import pytest
import os
from dotenv import load_dotenv
from todoist_mcp.server import TodoistMCPServer
from todoist_mcp.auth import AuthManager
from .conftest_integration import test_project_manager, cleanup_test_projects

# Load environment variables from .env file
load_dotenv()


@pytest.fixture
def server():
    """Create server instance with real API token."""
    # Use real token from environment or auth manager
    token = os.getenv("TODOIST_API_TOKEN")
    if not token:
        auth_manager = AuthManager()
        token = auth_manager.get_token()
    
    return TodoistMCPServer(token=token)


@pytest.fixture
def test_project_source(server, test_project_manager):
    """Create a source test project for batch operations."""
    return test_project_manager("BatchSource")


@pytest.fixture  
def test_project_target(server, test_project_manager):
    """Create a target test project for batch operations."""
    return test_project_manager("BatchTarget")


@pytest.fixture
def test_tasks(server, test_project_source):
    """Create test tasks for batch operations."""
    tasks = []
    for i in range(5):
        task = server.api.add_task(
            content=f"Batch Test Task {i}",
            project_id=test_project_source["id"],
            priority=2 if i % 2 == 0 else 1
        )
        tasks.append(task)
    yield tasks
    # Cleanup handled by project deletion


@pytest.fixture
def test_label(server):
    """Create a test label for batch operations."""
    label = server.api.add_label(name="Batch Test Label")
    yield label
    # Cleanup
    try:
        server.api.delete_label(label_id=label["id"])
    except:
        pass


class TestBatchOperationsIntegration:
    """Integration tests for batch operations against real API."""
    
    @pytest.mark.integration
    def test_batch_move_tasks_to_project(self, server, test_tasks, test_project_target):
        """Test batch moving tasks to a different project."""
        task_ids = [task["id"] for task in test_tasks[:3]]
        
        result = server.api.batch_move_tasks(
            task_ids=task_ids,
            project_id=test_project_target["id"]
        )
        
        assert "moved" in result
        assert "failed" in result
        assert len(result["moved"]) == 3
        assert len(result["failed"]) == 0
        
        # Verify tasks were moved
        for task_id in task_ids:
            task = server.api.get_task(task_id=task_id)
            assert task["project_id"] == test_project_target["id"]
    
    @pytest.mark.integration
    def test_batch_move_tasks_to_section(self, server, test_tasks, test_project_target):
        """Test batch moving tasks to a section."""
        # Create a section
        section = server.api.add_section(
            project_id=test_project_target["id"],
            name="Batch Target Section"
        )
        
        task_ids = [task["id"] for task in test_tasks[:2]]
        
        result = server.api.batch_move_tasks(
            task_ids=task_ids,
            section_id=section["id"]
        )
        
        assert len(result["moved"]) == 2
        assert len(result["failed"]) == 0
        
        # Verify tasks were moved to section
        for task_id in task_ids:
            task = server.api.get_task(task_id=task_id)
            assert task["section_id"] == section["id"]
            assert task["project_id"] == test_project_target["id"]
    
    @pytest.mark.integration
    def test_batch_move_partial_failure(self, server, test_tasks, test_project_target):
        """Test batch move with some invalid task IDs."""
        task_ids = [test_tasks[0]["id"], "invalid_task_123", test_tasks[1]["id"]]
        
        result = server.api.batch_move_tasks(
            task_ids=task_ids,
            project_id=test_project_target["id"]
        )
        
        assert len(result["moved"]) == 2
        assert len(result["failed"]) == 1
        assert result["failed"][0]["task_id"] == "invalid_task_123"
        assert "error" in result["failed"][0]
    
    @pytest.mark.integration
    def test_batch_update_labels_add(self, server, test_tasks, test_label):
        """Test batch adding labels to tasks."""
        task_ids = [task["id"] for task in test_tasks[:3]]
        
        result = server.api.batch_update_labels(
            task_ids=task_ids,
            add_labels=[test_label["name"]]
        )
        
        assert len(result["updated"]) == 3
        assert len(result["failed"]) == 0
        
        # Verify labels were added
        for task_id in task_ids:
            task = server.api.get_task(task_id=task_id)
            assert test_label["name"] in task["labels"]
    
    @pytest.mark.integration
    def test_batch_update_labels_remove(self, server, test_tasks, test_label):
        """Test batch removing labels from tasks."""
        # First add labels to tasks
        task_ids = [task["id"] for task in test_tasks[:3]]
        for task_id in task_ids:
            server.api.update_task(task_id=task_id, labels=[test_label["name"]])
        
        # Now batch remove
        result = server.api.batch_update_labels(
            task_ids=task_ids,
            remove_labels=[test_label["name"]]
        )
        
        assert len(result["updated"]) == 3
        assert len(result["failed"]) == 0
        
        # Verify labels were removed
        for task_id in task_ids:
            task = server.api.get_task(task_id=task_id)
            assert test_label["name"] not in task["labels"]
    
    @pytest.mark.integration
    def test_batch_update_labels_add_and_remove(self, server, test_tasks, test_label):
        """Test batch add and remove labels simultaneously."""
        # Create another label
        label2 = server.api.add_label(name="Batch Label 2")
        
        # Add first label to tasks
        task_ids = [task["id"] for task in test_tasks[:2]]
        for task_id in task_ids:
            server.api.update_task(task_id=task_id, labels=[test_label["name"]])
        
        # Batch update: remove first label, add second
        result = server.api.batch_update_labels(
            task_ids=task_ids,
            add_labels=[label2["name"]],
            remove_labels=[test_label["name"]]
        )
        
        assert len(result["updated"]) == 2
        
        # Verify changes
        for task_id in task_ids:
            task = server.api.get_task(task_id=task_id)
            assert test_label["name"] not in task["labels"]
            assert label2["name"] in task["labels"]
        
        # Cleanup
        server.api.delete_label(label_id=label2["id"])
    
    @pytest.mark.integration
    def test_batch_update_tasks_priority(self, server, test_tasks):
        """Test batch updating task priority."""
        task_ids = [task["id"] for task in test_tasks[:3]]
        
        result = server.api.batch_update_tasks(
            task_ids=task_ids,
            priority=4
        )
        
        assert len(result["updated"]) == 3
        assert len(result["failed"]) == 0
        
        # Verify priority was updated
        for task_id in task_ids:
            task = server.api.get_task(task_id=task_id)
            assert task["priority"] == 4
    
    @pytest.mark.integration
    def test_batch_update_tasks_multiple_fields(self, server, test_tasks):
        """Test batch updating multiple task fields."""
        task_ids = [task["id"] for task in test_tasks[:2]]
        
        result = server.api.batch_update_tasks(
            task_ids=task_ids,
            priority=3,
            description="Batch updated description"
        )
        
        assert len(result["updated"]) == 2
        
        # Verify updates
        for task_id in task_ids:
            task = server.api.get_task(task_id=task_id)
            assert task["priority"] == 3
            assert task["description"] == "Batch updated description"
    
    @pytest.mark.integration
    def test_batch_complete_tasks(self, server, test_tasks):
        """Test batch completing tasks."""
        task_ids = [task["id"] for task in test_tasks[:3]]
        
        result = server.api.batch_complete_tasks(task_ids=task_ids)
        
        assert len(result["completed"]) == 3
        assert len(result["failed"]) == 0
        
        # Completed tasks may not be retrievable or have different structure
        # Just verify the operation succeeded
    
    @pytest.mark.integration
    def test_batch_complete_with_failures(self, server, test_tasks):
        """Test batch complete with invalid task."""
        # Mix valid and invalid task IDs
        task_ids = [test_tasks[0]["id"], "invalid_task_456", test_tasks[1]["id"]]
        
        result = server.api.batch_complete_tasks(task_ids=task_ids)
        
        assert len(result["completed"]) == 2
        assert len(result["failed"]) == 1
        assert result["failed"][0]["task_id"] == "invalid_task_456"
        assert "error" in result["failed"][0]
    
    @pytest.mark.integration
    def test_batch_operations_empty_list(self, server, test_project_target):
        """Test batch operations with empty task list."""
        with pytest.raises(ValueError, match="Task list cannot be empty"):
            server.api.batch_move_tasks([], project_id=test_project_target["id"])
        
        with pytest.raises(ValueError, match="Task list cannot be empty"):
            server.api.batch_update_labels([], add_labels=["test"])
        
        with pytest.raises(ValueError, match="Task list cannot be empty"):
            server.api.batch_complete_tasks([])
    
    @pytest.mark.integration
    def test_batch_operations_max_limit(self, server, test_project_source):
        """Test batch operations respect 100 task limit."""
        # Create list of 101 task IDs (even if they don't exist)
        task_ids = [f"fake_id_{i}" for i in range(101)]
        
        with pytest.raises(ValueError, match="Maximum 100 tasks"):
            server.api.batch_move_tasks(
                task_ids=task_ids,
                project_id=test_project_source["id"]
            )
    
    @pytest.mark.integration
    def test_batch_validation_errors(self, server):
        """Test batch operation validation errors."""
        # No target specified for move
        with pytest.raises(ValueError, match="Must specify either project_id or section_id"):
            server.api.batch_move_tasks(["task123"])
        
        # No labels specified for update
        with pytest.raises(ValueError, match="Must specify either add_labels or remove_labels"):
            server.api.batch_update_labels(["task123"])
        
        # No update params for batch update
        with pytest.raises(ValueError, match="No update parameters provided"):
            server.api.batch_update_tasks(["task123"])
