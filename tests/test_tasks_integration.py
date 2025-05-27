"""Integration tests for Todoist task operations - Real API Testing."""

import pytest
import os
import time
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
def test_label_fixture(server):
    """Create test labels for integration tests."""
    labels = []
    label_names = ["TaskTestLabel1", "TaskTestLabel2", "TaskTestLabel3"]
    
    for name in label_names:
        label = server.api.add_label(name=name)
        labels.append(label)
    
    yield labels
    
    # Cleanup
    for label in labels:
        try:
            server.api.delete_label(label_id=label["id"])
        except:
            pass


class TestTasksIntegration:
    """Integration tests for task CRUD operations against real API."""
    
    @pytest.mark.integration
    def test_add_task_minimal(self, server):
        """Test adding a task with minimal parameters."""
        task = server.api.add_task(content="Integration Test Task Minimal")
        
        assert task["id"] is not None
        assert task["content"] == "Integration Test Task Minimal"
        assert "labels" in task
        assert isinstance(task["labels"], list)
        
        # Verify task was created by fetching it
        retrieved = server.api.get_task(task_id=task["id"])
        assert retrieved["content"] == "Integration Test Task Minimal"
    
    @pytest.mark.integration
    def test_add_task_with_project(self, server, test_project_manager):
        """Test adding a task to a specific project."""
        project = test_project_manager("TaskTestProject")
        
        task = server.api.add_task(
            content="Task in Project",
            project_id=project["id"]
        )
        
        assert task["project_id"] == project["id"]
        assert task["content"] == "Task in Project"
    
    @pytest.mark.integration
    def test_add_task_with_single_label(self, server, test_label_fixture):
        """Test adding a task with a single label."""
        label = test_label_fixture[0]
        
        task = server.api.add_task(
            content="Task with Single Label",
            labels=[label["name"]]
        )
        
        assert label["name"] in task["labels"]
        assert len(task["labels"]) == 1
        
        # Verify label persisted
        retrieved = server.api.get_task(task_id=task["id"])
        assert label["name"] in retrieved["labels"]
    
    @pytest.mark.integration
    def test_add_task_with_multiple_labels(self, server, test_label_fixture):
        """Test adding a task with multiple labels."""
        label_names = [label["name"] for label in test_label_fixture[:2]]
        
        task = server.api.add_task(
            content="Task with Multiple Labels",
            labels=label_names
        )
        
        assert len(task["labels"]) == 2
        for label_name in label_names:
            assert label_name in task["labels"]
    
    @pytest.mark.integration
    def test_add_task_full_parameters(self, server, test_project_manager, test_label_fixture):
        """Test adding a task with all parameters."""
        project = test_project_manager("TaskTestFullParams")
        label = test_label_fixture[0]
        
        task = server.api.add_task(
            content="Full Parameter Task",
            description="This is a detailed description of the task",
            project_id=project["id"],
            labels=[label["name"]],
            priority=4,
            due_string="tomorrow 2pm"
        )
        
        assert task["content"] == "Full Parameter Task"
        assert task["description"] == "This is a detailed description of the task"
        assert task["project_id"] == project["id"]
        assert label["name"] in task["labels"]
        assert task["priority"] == 4
        assert task["due"] is not None
    
    @pytest.mark.integration
    def test_update_task_add_labels(self, server, test_label_fixture):
        """Test updating a task to add labels."""
        # Create task without labels
        task = server.api.add_task(content="Task to Update with Labels")
        assert len(task.get("labels", [])) == 0
        
        # Update task to add labels
        label_names = [label["name"] for label in test_label_fixture[:2]]
        updated = server.api.update_task(
            task_id=task["id"],
            labels=label_names
        )
        
        assert len(updated["labels"]) == 2
        for label_name in label_names:
            assert label_name in updated["labels"]
    
    @pytest.mark.integration
    def test_update_task_change_labels(self, server, test_label_fixture):
        """Test updating a task to change its labels."""
        # Create task with initial labels
        initial_labels = [test_label_fixture[0]["name"]]
        task = server.api.add_task(
            content="Task with Labels to Change",
            labels=initial_labels
        )
        
        # Change to different labels
        new_labels = [test_label_fixture[1]["name"], test_label_fixture[2]["name"]]
        updated = server.api.update_task(
            task_id=task["id"],
            labels=new_labels
        )
        
        assert len(updated["labels"]) == 2
        assert test_label_fixture[0]["name"] not in updated["labels"]
        for label_name in new_labels:
            assert label_name in updated["labels"]
    
    @pytest.mark.integration
    def test_update_task_remove_labels(self, server, test_label_fixture):
        """Test updating a task to remove all labels."""
        # Create task with labels
        label_names = [label["name"] for label in test_label_fixture[:2]]
        task = server.api.add_task(
            content="Task to Remove Labels",
            labels=label_names
        )
        assert len(task["labels"]) == 2
        
        # Remove all labels
        updated = server.api.update_task(
            task_id=task["id"],
            labels=[]
        )
        
        assert len(updated["labels"]) == 0
    
    @pytest.mark.integration
    def test_get_tasks_filter_by_label(self, server, test_project_manager, test_label_fixture):
        """Test filtering tasks by label."""
        project = test_project_manager("TaskFilterProject")
        label = test_label_fixture[0]
        
        # Create tasks with and without the label
        task_with_label = server.api.add_task(
            content="Task with Target Label",
            project_id=project["id"],
            labels=[label["name"]]
        )
        
        task_without_label = server.api.add_task(
            content="Task without Target Label",
            project_id=project["id"]
        )
        
        # Filter by label - Note: label_ids parameter might need special handling
        # The API expects label names, not IDs for filtering
        results = server.api.get_tasks(
            project_id=project["id"]
        )
        
        # Manual filtering since API v1 doesn't support server-side label filtering
        filtered = [t for t in results["results"] if label["name"] in t.get("labels", [])]
        
        assert len(filtered) >= 1
        assert any(t["id"] == task_with_label["id"] for t in filtered)
        assert not any(t["id"] == task_without_label["id"] for t in filtered)
    
    @pytest.mark.integration
    def test_batch_update_labels_add(self, server, test_project_manager, test_label_fixture):
        """Test batch adding labels to multiple tasks."""
        project = test_project_manager("BatchLabelProject")
        
        # Create tasks without labels
        task_ids = []
        for i in range(3):
            task = server.api.add_task(
                content=f"Batch Task {i}",
                project_id=project["id"]
            )
            task_ids.append(task["id"])
        
        # Batch add labels
        labels_to_add = [label["name"] for label in test_label_fixture[:2]]
        result = server.api.batch_update_labels(
            task_ids=task_ids,
            add_labels=labels_to_add
        )
        
        assert len(result["updated"]) == 3
        assert len(result["failed"]) == 0
        
        # Verify labels were added
        for task_id in task_ids:
            task = server.api.get_task(task_id=task_id)
            for label_name in labels_to_add:
                assert label_name in task["labels"]
    
    @pytest.mark.integration
    def test_batch_update_labels_remove(self, server, test_project_manager, test_label_fixture):
        """Test batch removing labels from multiple tasks."""
        project = test_project_manager("BatchRemoveLabelProject")
        label_names = [label["name"] for label in test_label_fixture]
        
        # Create tasks with labels
        task_ids = []
        for i in range(3):
            task = server.api.add_task(
                content=f"Batch Task Remove {i}",
                project_id=project["id"],
                labels=label_names
            )
            task_ids.append(task["id"])
        
        # Batch remove specific labels
        labels_to_remove = [test_label_fixture[0]["name"]]
        result = server.api.batch_update_labels(
            task_ids=task_ids,
            remove_labels=labels_to_remove
        )
        
        assert len(result["updated"]) == 3
        
        # Verify labels were removed
        for task_id in task_ids:
            task = server.api.get_task(task_id=task_id)
            assert test_label_fixture[0]["name"] not in task["labels"]
            assert test_label_fixture[1]["name"] in task["labels"]
            assert test_label_fixture[2]["name"] in task["labels"]
    
    @pytest.mark.integration
    def test_batch_update_tasks_with_labels(self, server, test_project_manager, test_label_fixture):
        """Test batch updating multiple tasks including labels."""
        project = test_project_manager("BatchUpdateProject")
        
        # Create tasks
        task_ids = []
        for i in range(3):
            task = server.api.add_task(
                content=f"Original Task {i}",
                project_id=project["id"]
            )
            task_ids.append(task["id"])
        
        # Batch update with new labels
        new_labels = [label["name"] for label in test_label_fixture[:2]]
        result = server.api.batch_update_tasks(
            task_ids=task_ids,
            labels=new_labels,
            priority=3
        )
        
        assert len(result["updated"]) == 3
        
        # Verify updates
        for task_id in task_ids:
            task = server.api.get_task(task_id=task_id)
            assert task["priority"] == 3
            assert len(task["labels"]) == 2
            for label_name in new_labels:
                assert label_name in task["labels"]
    
    @pytest.mark.integration
    def test_mcp_tool_interface(self, server, test_label_fixture):
        """Test MCP tool interface with labels - simulating Claude Desktop usage."""
        # This test specifically targets the MCP tool interface issue
        import asyncio
        
        async def test_mcp_tools():
            # Get the MCP tools
            tools = await server.mcp.get_tools()
            
            # Test add_task tool
            add_task_tool = tools["add_task"]
            label_names = [label["name"] for label in test_label_fixture[:2]]
            
            # Call the tool function directly (simulating MCP call)
            result = await add_task_tool.fn(
                content="MCP Tool Test Task",
                labels=label_names
            )
            
            assert result["id"] is not None
            assert len(result["labels"]) == 2
            for label_name in label_names:
                assert label_name in result["labels"]
            
            # Test update_task tool
            update_task_tool = tools["update_task"]
            new_labels = [test_label_fixture[2]["name"]]
            
            updated = await update_task_tool.fn(
                task_id=result["id"],
                labels=new_labels
            )
            
            assert len(updated["labels"]) == 1
            assert test_label_fixture[2]["name"] in updated["labels"]
            
            # Test batch_update_labels tool
            batch_tool = tools["batch_update_labels"]
            batch_result = await batch_tool.fn(
                task_ids=[result["id"]],
                add_labels=[test_label_fixture[0]["name"]]
            )
            
            assert len(batch_result["updated"]) == 1
            assert batch_result["updated"][0] == result["id"]
        
        # Run the async test
        asyncio.run(test_mcp_tools())
    
    @pytest.mark.integration
    def test_task_with_nonexistent_label(self, server):
        """Test adding a task with a label that doesn't exist."""
        # Todoist API should handle this gracefully
        task = server.api.add_task(
            content="Task with Nonexistent Label",
            labels=["this-label-does-not-exist-12345"]
        )
        
        # The API might create the label or ignore it
        assert task["id"] is not None
        # Check how the API handled the nonexistent label
        print(f"Labels on task: {task.get('labels', [])}")
