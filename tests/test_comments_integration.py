"""Integration tests for Todoist Comment Support - Real API Testing."""

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
    """Create a test project for comment testing."""
    return test_project_manager("Comments")


@pytest.fixture  
def test_task(server, test_project):
    """Create a test task for comment testing."""
    task = server.api.add_task(
        content="Test Task for Comments",
        project_id=test_project["id"]
    )
    yield task
    # Cleanup handled by project deletion


class TestCommentIntegration:
    """Integration tests for comment CRUD operations against real API."""
    
    @pytest.mark.integration
    def test_add_comment_to_task(self, server, test_task):
        """Test adding a comment to a real task."""
        comment = server.api.add_comment(
            content="Integration test comment on task",
            task_id=test_task["id"]
        )
        
        assert comment["id"] is not None
        assert comment["content"] == "Integration test comment on task"
        assert comment["item_id"] == test_task["id"]
        assert "posted_at" in comment
        
        # Cleanup
        server.api.delete_comment(comment_id=comment["id"])
    
    @pytest.mark.integration
    def test_add_comment_to_project(self, server, test_project):
        """Test adding a comment to a real project."""
        comment = server.api.add_comment(
            content="Integration test comment on project",
            project_id=test_project["id"]
        )
        
        assert comment["id"] is not None
        assert comment["content"] == "Integration test comment on project"
        assert comment["project_id"] == test_project["id"]
        
        # Cleanup
        server.api.delete_comment(comment_id=comment["id"])
    
    @pytest.mark.integration
    def test_get_comments_for_task(self, server, test_task):
        """Test retrieving comments for a task."""
        # Add test comments
        comment1 = server.api.add_comment(
            content="First comment", 
            task_id=test_task["id"]
        )
        comment2 = server.api.add_comment(
            content="Second comment",
            task_id=test_task["id"]
        )
        
        # Get comments
        result = server.api.get_comments(task_id=test_task["id"])
        
        assert "results" in result
        assert len(result["results"]) >= 2
        
        # Find our test comments
        comment_contents = [c["content"] for c in result["results"]]
        assert "First comment" in comment_contents
        assert "Second comment" in comment_contents
        
        # Cleanup
        server.api.delete_comment(comment_id=comment1["id"])
        server.api.delete_comment(comment_id=comment2["id"])
    
    @pytest.mark.integration
    def test_get_single_comment(self, server, test_task):
        """Test retrieving a single comment by ID."""
        # Create comment
        comment = server.api.add_comment(
            content="Single comment test",
            task_id=test_task["id"]
        )
        
        # Get comment by ID
        retrieved = server.api.get_comment(comment_id=comment["id"])
        
        assert retrieved["id"] == comment["id"]
        assert retrieved["content"] == "Single comment test"
        assert retrieved["item_id"] == test_task["id"]
        
        # Cleanup
        server.api.delete_comment(comment_id=comment["id"])
    
    @pytest.mark.integration
    def test_update_comment(self, server, test_task):
        """Test updating an existing comment."""
        # Create comment
        comment = server.api.add_comment(
            content="Original comment",
            task_id=test_task["id"]
        )
        
        # Update comment
        updated = server.api.update_comment(
            comment_id=comment["id"],
            content="Updated comment content"
        )
        
        assert updated["id"] == comment["id"]
        assert updated["content"] == "Updated comment content"
        
        # Verify update persisted
        retrieved = server.api.get_comment(comment_id=comment["id"])
        assert retrieved["content"] == "Updated comment content"
        
        # Cleanup
        server.api.delete_comment(comment_id=comment["id"])
    
    @pytest.mark.integration
    def test_delete_comment(self, server, test_task):
        """Test deleting a comment."""
        # Create comment
        comment = server.api.add_comment(
            content="Comment to delete",
            task_id=test_task["id"]
        )
        comment_id = comment["id"]
        
        # Delete comment
        result = server.api.delete_comment(comment_id=comment_id)
        assert result is None  # Successful deletion returns None
        
        # Verify deletion - comment should have is_deleted=True
        deleted_comment = server.api.get_comment(comment_id=comment_id)
        assert deleted_comment["is_deleted"] is True
    
    @pytest.mark.integration 
    def test_comment_pagination(self, server, test_task):
        """Test pagination for comments."""
        # Create multiple comments
        comments = []
        for i in range(5):
            comment = server.api.add_comment(
                content=f"Pagination test comment {i}",
                task_id=test_task["id"]
            )
            comments.append(comment)
        
        # Test pagination with limit
        result = server.api.get_comments(
            task_id=test_task["id"],
            limit=3
        )
        
        assert len(result["results"]) <= 3
        if len(result["results"]) == 3:
            assert "next_cursor" in result
        
        # Cleanup
        for comment in comments:
            server.api.delete_comment(comment_id=comment["id"])
    
    @pytest.mark.integration
    def test_comment_validation_both_ids(self, server):
        """Test validation prevents commenting on both task and project."""
        with pytest.raises(ValueError, match="Comment must be for either task or project"):
            server.api.add_comment(
                content="Invalid comment",
                task_id="some_task_id",
                project_id="some_project_id"
            )
    
    @pytest.mark.integration
    def test_comment_validation_no_ids(self, server):
        """Test validation requires either task_id or project_id."""
        with pytest.raises(ValueError, match="Must specify either task_id or project_id"):
            server.api.add_comment(content="Orphan comment")
    
    @pytest.mark.integration
    def test_comment_error_invalid_task(self, server):
        """Test error handling for invalid task ID."""
        with pytest.raises(Exception) as exc_info:
            server.api.add_comment(
                content="Comment on invalid task",
                task_id="invalid_task_id_12345"
            )
        # Todoist should return 400 or 404 for invalid IDs
        assert "400" in str(exc_info.value) or "404" in str(exc_info.value)
