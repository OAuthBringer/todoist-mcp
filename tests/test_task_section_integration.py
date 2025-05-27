"""Integration tests for Task-Section functionality - Real API Testing."""

import pytest
import os
from dotenv import load_dotenv
from todoist_mcp.server import TodoistMCPServer
from .conftest_integration import test_project_manager, cleanup_test_projects

load_dotenv()


@pytest.fixture
def server():
    """Create server instance with real API token."""
    token = os.getenv("TODOIST_API_TOKEN")
    if not token:
        pytest.skip("TODOIST_API_TOKEN not set")
    return TodoistMCPServer(token=token)


@pytest.fixture
def test_project_with_sections(server, test_project_manager):
    """Create a test project with sections."""
    project = test_project_manager("TaskSection")
    
    # Create sections
    section1 = server.api.add_section(
        project_id=project["id"],
        name="Section A"
    )
    section2 = server.api.add_section(
        project_id=project["id"],
        name="Section B"
    )
    
    return {
        "project": project,
        "section1": section1,
        "section2": section2
    }


class TestTaskSectionIntegration:
    """Integration tests for task-section operations against real API."""
    
    @pytest.mark.integration
    def test_create_task_in_section(self, server, test_project_with_sections):
        """Test creating a task directly in a section."""
        project = test_project_with_sections["project"]
        section = test_project_with_sections["section1"]
        
        # Create task in section
        task = server.api.add_task(
            content="Task in Section A",
            project_id=project["id"],
            section_id=section["id"]
        )
        
        assert task["id"] is not None
        assert task["section_id"] == section["id"]
        assert task["project_id"] == project["id"]
        
        # Verify task appears in section filter
        tasks = server.api.get_tasks(section_id=section["id"])
        task_ids = [t["id"] for t in tasks.get("results", tasks)]
        assert task["id"] in task_ids
    
    @pytest.mark.integration
    def test_move_task_between_sections(self, server, test_project_with_sections):
        """Test moving a task from one section to another."""
        project = test_project_with_sections["project"]
        section1 = test_project_with_sections["section1"]
        section2 = test_project_with_sections["section2"]
        
        # Create task in first section
        task = server.api.add_task(
            content="Task to move",
            project_id=project["id"],
            section_id=section1["id"]
        )
        
        # Move to second section
        moved_task = server.api.move_task(
            task_id=task["id"],
            section_id=section2["id"]
        )
        
        assert moved_task["section_id"] == section2["id"]
        
        # Verify task no longer in first section
        section1_tasks = server.api.get_tasks(section_id=section1["id"])
        section1_task_ids = [t["id"] for t in section1_tasks.get("results", section1_tasks)]
        assert task["id"] not in section1_task_ids
        
        # Verify task is in second section
        section2_tasks = server.api.get_tasks(section_id=section2["id"])
        section2_task_ids = [t["id"] for t in section2_tasks.get("results", section2_tasks)]
        assert task["id"] in section2_task_ids
    
    @pytest.mark.integration
    def test_move_task_to_different_project(self, server, test_project_manager):
        """Test moving a task to a different project removes section association."""
        # Create two projects
        project1 = test_project_manager("MoveSource")
        project2 = test_project_manager("MoveDestination")
        
        # Create section in first project
        section = server.api.add_section(
            project_id=project1["id"],
            name="Source Section"
        )
        
        # Create task in section
        task = server.api.add_task(
            content="Task to move projects",
            project_id=project1["id"],
            section_id=section["id"]
        )
        
        # Move to different project (should clear section_id)
        moved_task = server.api.move_task(
            task_id=task["id"],
            project_id=project2["id"]
        )
        
        # Verify task is in new project without section
        assert moved_task["project_id"] == project2["id"]
        assert moved_task["section_id"] is None
    
    @pytest.mark.integration
    def test_get_tasks_by_section(self, server, test_project_with_sections):
        """Test filtering tasks by section."""
        project = test_project_with_sections["project"]
        section1 = test_project_with_sections["section1"]
        section2 = test_project_with_sections["section2"]
        
        # Create tasks in different sections
        task1 = server.api.add_task(
            content="Task in Section A",
            project_id=project["id"],
            section_id=section1["id"]
        )
        task2 = server.api.add_task(
            content="Another task in Section A",
            project_id=project["id"],
            section_id=section1["id"]
        )
        task3 = server.api.add_task(
            content="Task in Section B",
            project_id=project["id"],
            section_id=section2["id"]
        )
        task_no_section = server.api.add_task(
            content="Task without section",
            project_id=project["id"]
        )
        
        # Get tasks from section 1
        section1_tasks = server.api.get_tasks(section_id=section1["id"])
        section1_contents = [t["content"] for t in section1_tasks.get("results", section1_tasks)]
        
        assert "Task in Section A" in section1_contents
        assert "Another task in Section A" in section1_contents
        assert "Task in Section B" not in section1_contents
        assert "Task without section" not in section1_contents
    
    @pytest.mark.integration
    def test_task_includes_section_id(self, server, test_project_with_sections):
        """Test that task responses include section_id field."""
        project = test_project_with_sections["project"]
        section = test_project_with_sections["section1"]
        
        # Create task in section
        task = server.api.add_task(
            content="Test task",
            project_id=project["id"],
            section_id=section["id"]
        )
        
        # Get single task
        fetched_task = server.api.get_task(task["id"])
        assert "section_id" in fetched_task
        assert fetched_task["section_id"] == section["id"]
        
        # Get tasks list
        tasks = server.api.get_tasks(project_id=project["id"])
        for task in tasks.get("results", tasks):
            assert "section_id" in task
    
    @pytest.mark.integration
    def test_section_deletion_behavior(self, server, test_project_manager):
        """Test task behavior when section is deleted."""
        # Create separate project for this test to avoid cleanup issues
        project = test_project_manager("SectionDeletion")
        
        # Create section and task
        section = server.api.add_section(
            project_id=project["id"],
            name="Temporary Section"
        )
        task = server.api.add_task(
            content="Task in section to delete",
            project_id=project["id"],
            section_id=section["id"]
        )
        
        # Delete section
        server.api.delete_section(section["id"])
        
        # Task should still exist and reference the deleted section
        fetched_task = server.api.get_task(task["id"])
        assert fetched_task["section_id"] == section["id"]  # Section ID remains
        assert fetched_task["project_id"] == project["id"]
        
        # Verify section is marked as deleted
        deleted_section = server.api.get_section(section["id"])
        assert deleted_section["is_deleted"] is True
