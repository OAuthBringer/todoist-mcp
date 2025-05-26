"""Integration tests for Todoist Search Functionality - Real API Testing."""

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
def test_project(server, test_project_manager):
    """Create a test project for search testing."""
    return test_project_manager("Search")


@pytest.fixture
def test_labels(server):
    """Create test labels for search testing."""
    label1 = server.api.add_label(name="SearchLabel1")
    label2 = server.api.add_label(name="SearchLabel2")
    yield [label1, label2]
    # Cleanup
    for label in [label1, label2]:
        try:
            server.api.delete_label(label_id=label["id"])
        except:
            pass


@pytest.fixture
def test_tasks_varied(server, test_project, test_labels):
    """Create varied test tasks for search testing."""
    tasks = []
    
    # Task with unique content
    tasks.append(server.api.add_task(
        content="Task with unique keyword in content",
        project_id=test_project["id"],
        priority=1
    ))
    
    # High priority task
    tasks.append(server.api.add_task(
        content="High priority search task",
        project_id=test_project["id"],
        priority=4
    ))
    
    # Task with labels
    tasks.append(server.api.add_task(
        content="Task with labels for search",
        project_id=test_project["id"],
        labels=[test_labels[0]["name"], test_labels[1]["name"]]
    ))
    
    # Task with due date
    tasks.append(server.api.add_task(
        content="Task with due date",
        project_id=test_project["id"],
        due_string="tomorrow"
    ))
    
    # Regular task
    tasks.append(server.api.add_task(
        content="Regular task for search",
        project_id=test_project["id"]
    ))
    
    yield tasks
    # Cleanup handled by project deletion


class TestSearchIntegration:
    """Integration tests for search functionality against real API."""
    
    @pytest.mark.integration
    def test_search_by_content(self, server, test_tasks_varied, test_project):
        """Test searching tasks by content.
        
        Note: Uses client-side filtering due to Todoist API limitations.
        Project filter used to reduce dataset size.
        """
        result = server.api.search_tasks(query="unique keyword", project_id=test_project["id"])
        
        assert "tasks" in result
        assert "total_count" in result
        assert result["total_count"] >= 1
        
        # Verify we found the task with unique keyword
        found = any("unique keyword" in task["content"].lower() 
                   for task in result["tasks"])
        assert found, "Test task with 'unique keyword' not found"
    
    @pytest.mark.integration
    def test_search_by_priority(self, server, test_tasks_varied, test_project):
        """Test searching tasks by priority."""
        result = server.api.search_tasks(priority=4, project_id=test_project["id"])
        
        assert "tasks" in result
        assert result["total_count"] >= 1
        
        # All returned tasks should have priority 4
        for task in result["tasks"]:
            assert task["priority"] == 4
    
    @pytest.mark.integration
    def test_search_by_labels(self, server, test_tasks_varied, test_labels, test_project):
        """Test searching tasks by labels."""
        result = server.api.search_tasks(labels=[test_labels[0]["name"]], project_id=test_project["id"])
        
        assert "tasks" in result
        assert result["total_count"] >= 1
        
        # Check that tasks have the label
        for task in result["tasks"]:
            assert test_labels[0]["name"] in task.get("labels", [])
    
    @pytest.mark.integration
    def test_search_by_project(self, server, test_tasks_varied, test_project):
        """Test searching tasks by project."""
        result = server.api.search_tasks(project_id=test_project["id"])
        
        assert "tasks" in result
        # Should find our 5 test tasks
        assert result["total_count"] >= 5
        
        # All tasks should be from test project
        for task in result["tasks"]:
            assert task["project_id"] == test_project["id"]
    
    @pytest.mark.integration
    def test_search_with_multiple_filters(self, server, test_tasks_varied, test_project):
        """Test search with multiple filters combined."""
        result = server.api.search_tasks(
            project_id=test_project["id"],
            priority=1
        )
        
        assert "tasks" in result
        assert result["total_count"] >= 1
        
        # Verify filters are applied
        for task in result["tasks"]:
            assert task["project_id"] == test_project["id"]
            assert task["priority"] == 1
    
    @pytest.mark.integration
    def test_search_empty_results(self, server, test_project):
        """Test search with no matching results."""
        result = server.api.search_tasks(query="xyznonexistentquery123", project_id=test_project["id"])
        
        assert "tasks" in result
        assert result["total_count"] == 0
        assert result["tasks"] == []
    
    @pytest.mark.integration
    def test_search_with_due_date(self, server, test_tasks_varied, test_project):
        """Test searching tasks by due date."""
        result = server.api.search_tasks(due_date="tomorrow", project_id=test_project["id"])
        
        assert "tasks" in result
        # Should find at least our test task with due date
        assert result["total_count"] >= 1
        
        # All tasks should have a due date
        for task in result["tasks"]:
            assert task.get("due") is not None
    
    @pytest.mark.integration
    def test_search_completed_filter(self, server, test_project):
        """Test filtering by completion status."""
        # Create and complete a task
        task = server.api.add_task(
            content="Completed search test task",
            project_id=test_project["id"]
        )
        server.api._request("POST", f"tasks/{task['id']}/close")
        
        # Search for non-completed tasks
        result = server.api.search_tasks(
            project_id=test_project["id"],
            is_completed=False
        )
        
        # Completed task should not be in results
        task_ids = [t["id"] for t in result["tasks"]]
        assert task["id"] not in task_ids
    
    @pytest.mark.integration
    def test_search_with_pagination(self, server, test_project):
        """Test search pagination."""
        # Create multiple tasks
        for i in range(5):
            server.api.add_task(
                content=f"Pagination test task {i}",
                project_id=test_project["id"]
            )
        
        # Search with limit
        result = server.api.search_tasks(
            project_id=test_project["id"],
            limit=3
        )
        
        assert "tasks" in result
        assert len(result["tasks"]) <= 3
    
    @pytest.mark.integration
    def test_search_validation_invalid_priority(self, server):
        """Test search validation for invalid priority."""
        with pytest.raises(ValueError, match="Priority must be between 1 and 4"):
            server.api.search_tasks(priority=5)
    
    @pytest.mark.integration
    def test_search_by_multiple_labels(self, server, test_tasks_varied, test_labels, test_project):
        """Test searching with multiple labels (OR logic)."""
        result = server.api.search_tasks(
            labels=[test_labels[0]["name"], test_labels[1]["name"]],
            project_id=test_project["id"]
        )
        
        assert "tasks" in result
        assert result["total_count"] >= 1
        
        # Tasks should have at least one of the labels
        for task in result["tasks"]:
            task_labels = task.get("labels", [])
            has_label = any(label in task_labels for label in [test_labels[0]["name"], test_labels[1]["name"]])
            assert has_label
    
    @pytest.mark.integration
    def test_search_response_structure(self, server, test_tasks_varied, test_project):
        """Test search response has expected structure."""
        result = server.api.search_tasks(query="search", project_id=test_project["id"])
        
        assert isinstance(result, dict)
        assert "tasks" in result
        assert "total_count" in result
        assert isinstance(result["tasks"], list)
        assert isinstance(result["total_count"], int)
        
        # If tasks exist, verify their structure
        if result["tasks"]:
            task = result["tasks"][0]
            assert "id" in task
            assert "content" in task
            assert "project_id" in task
            assert "priority" in task
