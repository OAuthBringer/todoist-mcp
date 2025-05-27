"""Integration tests for Todoist Sections Support - Real API Testing."""

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
    """Create a test project for section testing."""
    return test_project_manager("Sections")


class TestSectionsIntegration:
    """Integration tests for sections CRUD operations against real API."""
    
    @pytest.mark.integration
    def test_add_section(self, server, test_project):
        """Test creating a new section in a real project."""
        section = server.api.add_section(
            project_id=test_project["id"],
            name="Test Section"
        )
        
        assert section["id"] is not None
        assert section["name"] == "Test Section"
        assert section["project_id"] == test_project["id"]
        assert "section_order" in section
        
        # Cleanup
        server.api.delete_section(section["id"])
    
    @pytest.mark.integration
    def test_add_section_with_order(self, server, test_project):
        """Test creating a section with specific order."""
        section = server.api.add_section(
            project_id=test_project["id"],
            name="Ordered Section",
            order=5
        )
        
        assert section["name"] == "Ordered Section"
        # Order parameter affects position but API returns section_order
        assert "section_order" in section
        
        # Cleanup
        server.api.delete_section(section["id"])
    
    @pytest.mark.integration
    def test_get_sections(self, server, test_project):
        """Test retrieving all sections for a project."""
        # Create test sections
        section1 = server.api.add_section(
            project_id=test_project["id"],
            name="Section One"
        )
        section2 = server.api.add_section(
            project_id=test_project["id"],
            name="Section Two"
        )
        
        # Get sections
        sections = server.api.get_sections(test_project["id"])
        
        # Check if response is paginated or direct list
        if isinstance(sections, dict) and "results" in sections:
            sections = sections["results"]
        
        assert isinstance(sections, list)
        assert len(sections) >= 2
        
        # Find our test sections
        section_names = [s["name"] for s in sections]
        assert "Section One" in section_names
        assert "Section Two" in section_names
        
        # Cleanup
        server.api.delete_section(section1["id"])
        server.api.delete_section(section2["id"])
    
    @pytest.mark.integration
    def test_get_section(self, server, test_project):
        """Test retrieving a single section by ID."""
        # Create section
        section = server.api.add_section(
            project_id=test_project["id"],
            name="Single Section Test"
        )
        
        # Get section by ID
        retrieved = server.api.get_section(section["id"])
        
        assert retrieved["id"] == section["id"]
        assert retrieved["name"] == "Single Section Test"
        assert retrieved["project_id"] == test_project["id"]
        
        # Cleanup
        server.api.delete_section(section["id"])
    
    @pytest.mark.integration
    def test_update_section(self, server, test_project):
        """Test updating an existing section."""
        # Create section
        section = server.api.add_section(
            project_id=test_project["id"],
            name="Original Name"
        )
        
        # Update section
        result = server.api.update_section(
            section_id=section["id"],
            name="Updated Name"
        )
        
        # Update returns the updated section
        assert result["name"] == "Updated Name"
        
        # Verify update persisted
        retrieved = server.api.get_section(section["id"])
        assert retrieved["name"] == "Updated Name"
        
        # Cleanup
        server.api.delete_section(section["id"])
    
    @pytest.mark.integration
    def test_delete_section(self, server, test_project):
        """Test deleting a section."""
        # Create section
        section = server.api.add_section(
            project_id=test_project["id"],
            name="Section to Delete"
        )
        section_id = section["id"]
        
        # Delete section
        result = server.api.delete_section(section_id)
        assert result is None  # Successful deletion returns None
        
        # Verify deletion - deleted sections have is_deleted=True
        deleted_section = server.api.get_section(section_id)
        assert deleted_section["is_deleted"] is True
    
    @pytest.mark.integration
    def test_task_in_section(self, server, test_project):
        """Test creating and filtering tasks by section."""
        # Create section
        section = server.api.add_section(
            project_id=test_project["id"],
            name="Tasks Section"
        )
        
        # Create task in section
        task = server.api.add_task(
            content="Task in section",
            project_id=test_project["id"],
            section_id=section["id"]
        )
        
        assert task["section_id"] == section["id"]
        
        # Get tasks filtered by section
        tasks = server.api.get_tasks(section_id=section["id"])
        task_contents = [t["content"] for t in tasks.get("results", tasks)]
        assert "Task in section" in task_contents
        
        # Cleanup
        try:
            # Delete task first
            server.api._request("POST", f"tasks/{task['id']}/close")
        except:
            pass
        server.api.delete_section(section["id"])
    
    @pytest.mark.integration
    def test_move_task_to_section(self, server, test_project):
        """Test moving a task to a different section."""
        # Create two sections
        section1 = server.api.add_section(
            project_id=test_project["id"],
            name="Source Section"
        )
        section2 = server.api.add_section(
            project_id=test_project["id"],
            name="Target Section"
        )
        
        # Create task in first section
        task = server.api.add_task(
            content="Task to move",
            project_id=test_project["id"],
            section_id=section1["id"]
        )
        
        # Move task to second section
        moved_task = server.api.move_task(
            task_id=task["id"],
            section_id=section2["id"]
        )
        
        assert moved_task["section_id"] == section2["id"]
        
        # Cleanup
        try:
            server.api._request("POST", f"tasks/{task['id']}/close")
        except:
            pass
        server.api.delete_section(section1["id"])
        server.api.delete_section(section2["id"])
    
    @pytest.mark.integration
    def test_section_order(self, server, test_project):
        """Test section ordering."""
        # Create multiple sections
        sections = []
        for i in range(3):
            section = server.api.add_section(
                project_id=test_project["id"],
                name=f"Section {i}"
            )
            sections.append(section)
        
        # Get all sections
        all_sections = server.api.get_sections(test_project["id"])
        
        # Check if response is paginated or direct list
        if isinstance(all_sections, dict) and "results" in all_sections:
            all_sections = all_sections["results"]
        
        # Verify we have our sections
        created_ids = {s["id"] for s in sections}
        retrieved_ids = {s["id"] for s in all_sections}
        assert created_ids.issubset(retrieved_ids)
        
        # Cleanup
        for section in sections:
            server.api.delete_section(section["id"])
    
    @pytest.mark.integration
    def test_section_validation_empty_name(self, server, test_project):
        """Test validation prevents empty section names."""
        # Client-side validation should catch this
        with pytest.raises(ValueError) as exc_info:
            server.api.update_section(
                section_id="dummy_id",
                name=""
            )
        assert "Section name cannot be empty" in str(exc_info.value)
    
    @pytest.mark.integration
    def test_section_error_invalid_project(self, server):
        """Test error handling for invalid project ID."""
        with pytest.raises(Exception) as exc_info:
            server.api.add_section(
                project_id="invalid_project_12345",
                name="Test Section"
            )
        # Todoist should return 400 or 404 for invalid project
        assert "400" in str(exc_info.value) or "404" in str(exc_info.value)
