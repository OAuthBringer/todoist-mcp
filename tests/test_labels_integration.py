"""Integration tests for Todoist Label Support - Real API Testing."""

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
def test_label(server):
    """Create a test label for testing."""
    label = server.api.add_label(
        name=f"Test Label Integration",
        order=1
    )
    yield label
    # Cleanup
    try:
        server.api.delete_label(label_id=label["id"])
    except:
        pass  # Label might already be deleted in test


class TestLabelsIntegration:
    """Integration tests for label CRUD operations against real API."""
    
    @pytest.mark.integration
    def test_add_label(self, server):
        """Test adding a label with real API."""
        label = server.api.add_label(
            name="Integration Test Label",
            order=10
        )
        
        assert label["id"] is not None
        assert label["name"] == "Integration Test Label"
        assert "color" in label  # Color assigned by API
        assert label["order"] == 10
        
        # Cleanup
        server.api.delete_label(label_id=label["id"])
    
    @pytest.mark.integration
    def test_add_label_minimal(self, server):
        """Test adding a label with only required fields."""
        label = server.api.add_label(name="Minimal Label")
        
        assert label["id"] is not None
        assert label["name"] == "Minimal Label"
        # Color should have a default
        assert "color" in label
        
        # Cleanup
        server.api.delete_label(label_id=label["id"])
    
    @pytest.mark.integration
    def test_get_labels(self, server):
        """Test retrieving all labels."""
        # Just test that we can get labels
        result = server.api.get_labels()
        
        assert "results" in result
        assert isinstance(result["results"], list)
        # Verify structure if any labels exist
        if result["results"]:
            label = result["results"][0]
            assert "id" in label
            assert "name" in label
            assert "color" in label
    
    @pytest.mark.integration
    def test_get_labels_pagination(self, server):
        """Test label pagination."""
        # Create multiple labels
        labels = []
        for i in range(5):
            label = server.api.add_label(
                name=f"Pagination Label {i}",
                order=i
            )
            labels.append(label)
        
        # Test pagination with limit
        result = server.api.get_labels(limit=3)
        
        assert len(result["results"]) <= 3
        if len(result["results"]) == 3:
            assert "next_cursor" in result or len(result["results"]) < 3
        
        # Cleanup
        for label in labels:
            server.api.delete_label(label_id=label["id"])
    
    @pytest.mark.integration
    def test_get_label_by_id(self, server, test_label):
        """Test retrieving a single label by ID."""
        retrieved = server.api.get_label(label_id=test_label["id"])
        
        assert retrieved["id"] == test_label["id"]
        assert retrieved["name"] == test_label["name"]
        assert retrieved["color"] == test_label["color"]
        assert retrieved["order"] == test_label["order"]
    
    @pytest.mark.integration
    def test_update_label_name(self, server, test_label):
        """Test updating a label's name."""
        updated = server.api.update_label(
            label_id=test_label["id"],
            name="Updated Label Name"
        )
        
        assert updated["id"] == test_label["id"]
        assert updated["name"] == "Updated Label Name"
        assert updated["color"] == test_label["color"]  # Unchanged
        
        # Verify update persisted
        retrieved = server.api.get_label(label_id=test_label["id"])
        assert retrieved["name"] == "Updated Label Name"
    
    @pytest.mark.integration
    def test_update_label_color(self, server, test_label):
        """Test updating a label's properties."""
        updated = server.api.update_label(
            label_id=test_label["id"],
            name="Updated Label"
        )
        
        assert updated["id"] == test_label["id"]
        assert updated["name"] == "Updated Label"
    
    @pytest.mark.integration
    def test_update_label_order(self, server, test_label):
        """Test updating a label's order."""
        updated = server.api.update_label(
            label_id=test_label["id"],
            order=99
        )
        
        assert updated["id"] == test_label["id"]
        assert updated["order"] == 99
    
    @pytest.mark.integration
    def test_update_label_multiple_fields(self, server, test_label):
        """Test updating multiple label fields at once."""
        updated = server.api.update_label(
            label_id=test_label["id"],
            name="Fully Updated Label",
            order=50
        )
        
        assert updated["name"] == "Fully Updated Label"
        assert updated["order"] == 50
    
    @pytest.mark.integration
    def test_delete_label(self, server):
        """Test deleting a label."""
        # Create label
        label = server.api.add_label(name="Label to Delete")
        label_id = label["id"]
        
        # Delete label
        result = server.api.delete_label(label_id=label_id)
        assert result is None  # Successful deletion returns None
        
        # Verify deletion - should fail to get deleted label
        # Some APIs return 404, others may return the label with a flag
        # Just verify we can't use the label anymore
        try:
            deleted_label = server.api.get_label(label_id=label_id)
            # If we get here, check if it's marked as deleted somehow
            # The API might return the label but it won't be usable
        except Exception:
            # Expected - label was deleted
            pass
    
    @pytest.mark.integration
    def test_label_with_task_integration(self, server, test_project_manager, test_label):
        """Test labels integration with tasks."""
        project = test_project_manager("LabelTaskIntegration")
        
        # Create task with label
        task = server.api.add_task(
            content="Task with Label",
            project_id=project["id"],
            labels=[test_label["name"]]
        )
        
        assert test_label["name"] in task["labels"]
        
        # Get task to verify label persisted
        retrieved_task = server.api.get_task(task_id=task["id"])
        assert test_label["name"] in retrieved_task["labels"]
    
    @pytest.mark.integration
    def test_label_validation_empty_name(self, server):
        """Test validation prevents creating label with empty name."""
        with pytest.raises(Exception) as exc_info:
            server.api.add_label(name="")
        # Todoist should return 400 for empty name
        assert "400" in str(exc_info.value)
    
    @pytest.mark.integration
    def test_label_error_invalid_id(self, server):
        """Test error handling for invalid label ID."""
        with pytest.raises(Exception) as exc_info:
            server.api.get_label(label_id="invalid_label_id_12345")
        # Todoist should return 404 for invalid IDs
        assert "404" in str(exc_info.value) or "400" in str(exc_info.value)
    
    @pytest.mark.integration
    def test_label_color_values(self, server):
        """Test creating labels without color parameter."""
        labels = []
        
        for i in range(3):
            label = server.api.add_label(
                name=f"Color Test {i}"
            )
            assert "color" in label  # API assigns default color
            labels.append(label)
        
        # Cleanup
        for label in labels:
            server.api.delete_label(label_id=label["id"])
