"""Todoist MCP Server implementation using unified API v1."""

import json
from typing import Any, Dict, Optional, List
from fastmcp import FastMCP
from .api_v1 import TodoistV1Client
from .auth import AuthManager

class TodoistMCPServer:
    """FastMCP server wrapping Todoist unified API v1."""
    
    def __init__(self, token: Optional[str] = None):
        """Initialize server with Todoist API token."""
        self.mcp = FastMCP("Todoist MCP Server")
        
        if token:
            api_token = token
        else:
            auth_manager = AuthManager()
            api_token = auth_manager.get_token()
        
        self.api = TodoistV1Client(api_token)
        self._register_core_tools()
    
    def _register_core_tools(self):
        """Register core Todoist API tools with pagination support."""
        
        @self.mcp.tool(name="get_projects")
        async def get_projects(limit: Optional[int] = None, cursor: Optional[str] = None):
            """Get projects with optional pagination."""
            return self.api.get_projects(limit=limit, cursor=cursor)
        
        @self.mcp.tool(name="get_project")
        async def get_project(project_id: str):
            """Get a single project by ID."""
            return self.api.get_project(project_id=project_id)
        
        @self.mcp.tool(name="add_project")
        async def add_project(name: str, parent_id: Optional[str] = None, color: Optional[str] = None):
            """Create a new project."""
            return self.api.add_project(name=name, parent_id=parent_id, color=color)
        
        @self.mcp.tool(name="get_tasks")
        async def get_tasks(
            project_id: Optional[str] = None,
            section_id: Optional[str] = None,
            parent_id: Optional[str] = None,
            label_ids: Optional[str] = None,  # JSON string like '["important"]'
            limit: Optional[int] = None,
            cursor: Optional[str] = None
        ):
            """Get tasks with optional pagination and filters."""
            filters = {}
            if section_id:
                filters["section_id"] = section_id
            if parent_id:
                filters["parent_id"] = parent_id
            if label_ids:
                filters["label_ids"] = label_ids  # Pass as-is (JSON string)
            
            result = self.api.get_tasks(
                project_id=project_id,
                limit=limit,
                cursor=cursor,
                **filters
            )
            return result
        
        @self.mcp.tool(name="get_task")
        async def get_task(task_id: str):
            """Get a single task by ID."""
            return self.api.get_task(task_id=task_id)
        
        @self.mcp.tool(name="add_task")
        async def add_task(content: str, description: Optional[str] = None, 
                         project_id: Optional[str] = None, section_id: Optional[str] = None,
                         parent_id: Optional[str] = None, order: Optional[int] = None,
                         labels: Optional[str] = None,  # JSON string like '["urgent", "work"]'
                         priority: Optional[int] = None,
                         due_string: Optional[str] = None, due_date: Optional[str] = None,
                         due_datetime: Optional[str] = None, due_lang: Optional[str] = None,
                         assignee_id: Optional[str] = None, duration: Optional[int] = None,
                         duration_unit: Optional[str] = None):
            """Create a new task."""
            # Parse labels from JSON string if provided
            parsed_labels = None
            if labels:
                if isinstance(labels, str):
                    try:
                        parsed_labels = json.loads(labels)
                    except json.JSONDecodeError:
                        # If it's not valid JSON, treat it as a single label
                        parsed_labels = [labels]
                else:
                    # Already a list, use as-is
                    parsed_labels = labels
            
            return self.api.add_task(
                content=content, description=description, project_id=project_id,
                section_id=section_id, parent_id=parent_id, order=order,
                labels=parsed_labels, priority=priority, due_string=due_string,
                due_date=due_date, due_datetime=due_datetime, due_lang=due_lang,
                assignee_id=assignee_id, duration=duration, duration_unit=duration_unit
            )
        
        @self.mcp.tool(name="update_task")
        async def update_task(task_id: str, content: Optional[str] = None,
                            description: Optional[str] = None, 
                            labels: Optional[str] = None,  # JSON string like '["urgent", "work"]'
                            priority: Optional[int] = None, due_string: Optional[str] = None,
                            due_date: Optional[str] = None, due_datetime: Optional[str] = None,
                            due_lang: Optional[str] = None, assignee_id: Optional[str] = None,
                            duration: Optional[int] = None, duration_unit: Optional[str] = None):
            """Update an existing task."""
            # Parse labels from JSON string if provided
            parsed_labels = None
            if labels:
                if isinstance(labels, str):
                    try:
                        parsed_labels = json.loads(labels)
                    except json.JSONDecodeError:
                        # If it's not valid JSON, treat it as a single label
                        parsed_labels = [labels]
                else:
                    # Already a list, use as-is
                    parsed_labels = labels
            
            return self.api.update_task(
                task_id=task_id, content=content, description=description,
                labels=parsed_labels, priority=priority, due_string=due_string,
                due_date=due_date, due_datetime=due_datetime, due_lang=due_lang,
                assignee_id=assignee_id, duration=duration, duration_unit=duration_unit
            )
        
        @self.mcp.tool(name="get_comments")
        async def get_comments(
            task_id: Optional[str] = None,
            project_id: Optional[str] = None,
            limit: Optional[int] = None,
            cursor: Optional[str] = None
        ):
            """Get comments for a task or project with optional pagination."""
            return self.api.get_comments(
                task_id=task_id, project_id=project_id,
                limit=limit, cursor=cursor
            )
        
        @self.mcp.tool(name="add_comment")
        async def add_comment(
            content: str,
            task_id: Optional[str] = None,
            project_id: Optional[str] = None
        ):
            """Add a comment to a task or project."""
            return self.api.add_comment(
                content=content, task_id=task_id, project_id=project_id
            )
        
        @self.mcp.tool(name="get_comment")
        async def get_comment(comment_id: str):
            """Get a single comment by ID."""
            return self.api.get_comment(comment_id=comment_id)
        
        @self.mcp.tool(name="update_comment")
        async def update_comment(comment_id: str, content: str):
            """Update an existing comment."""
            return self.api.update_comment(
                comment_id=comment_id, content=content
            )
        
        @self.mcp.tool(name="delete_comment")
        async def delete_comment(comment_id: str):
            """Delete a comment."""
            return self.api.delete_comment(comment_id=comment_id)
        
        @self.mcp.tool(name="move_task")
        async def move_task(
            task_id: str,
            project_id: Optional[str] = None,
            section_id: Optional[str] = None,
            parent_id: Optional[str] = None
        ):
            """Move a task to a different project, section, or parent."""
            return self.api.move_task(
                task_id=task_id,
                project_id=project_id,
                section_id=section_id,
                parent_id=parent_id
            )
        
        @self.mcp.tool(name="get_labels")
        async def get_labels(
            limit: Optional[int] = None,
            cursor: Optional[str] = None
        ):
            """Get labels with optional pagination."""
            return self.api.get_labels(limit=limit, cursor=cursor)
        
        @self.mcp.tool(name="get_label")
        async def get_label(label_id: str):
            """Get a single label by ID."""
            return self.api.get_label(label_id=label_id)
        
        @self.mcp.tool(name="add_label")
        async def add_label(
            name: str,
            color: Optional[str] = None,
            order: Optional[int] = None
        ):
            """Create a new label."""
            return self.api.add_label(name=name, color=color, order=order)
        
        @self.mcp.tool(name="update_label")
        async def update_label(
            label_id: str,
            name: Optional[str] = None,
            color: Optional[str] = None,
            order: Optional[int] = None
        ):
            """Update an existing label."""
            return self.api.update_label(
                label_id=label_id,
                name=name,
                color=color,
                order=order
            )
        
        @self.mcp.tool(name="delete_label")
        async def delete_label(label_id: str):
            """Delete a label."""
            return self.api.delete_label(label_id=label_id)
        
        @self.mcp.tool(name="batch_move_tasks")
        async def batch_move_tasks(
            task_ids: str,  # JSON string like '["task1", "task2"]'
            project_id: Optional[str] = None,
            section_id: Optional[str] = None
        ):
            """Batch move multiple tasks to a project or section."""
            # Parse task_ids from JSON string
            parsed_task_ids = json.loads(task_ids) if isinstance(task_ids, str) else task_ids
            
            return self.api.batch_move_tasks(
                task_ids=parsed_task_ids,
                project_id=project_id,
                section_id=section_id
            )
        
        @self.mcp.tool(name="batch_update_labels")
        async def batch_update_labels(
            task_ids: str,  # JSON string like '["task1", "task2"]'
            add_labels: Optional[str] = None,  # JSON string like '["urgent", "work"]'
            remove_labels: Optional[str] = None  # JSON string like '["old-label"]'
        ):
            """Batch update labels for multiple tasks."""
            # Parse task_ids from JSON string
            parsed_task_ids = json.loads(task_ids) if isinstance(task_ids, str) else task_ids
            
            # Parse labels from JSON strings if provided
            parsed_add_labels = None
            if add_labels:
                if isinstance(add_labels, str):
                    try:
                        parsed_add_labels = json.loads(add_labels)
                    except json.JSONDecodeError:
                        parsed_add_labels = [add_labels]
                else:
                    parsed_add_labels = add_labels
            
            parsed_remove_labels = None
            if remove_labels:
                if isinstance(remove_labels, str):
                    try:
                        parsed_remove_labels = json.loads(remove_labels)
                    except json.JSONDecodeError:
                        parsed_remove_labels = [remove_labels]
                else:
                    parsed_remove_labels = remove_labels
            
            return self.api.batch_update_labels(
                task_ids=parsed_task_ids,
                add_labels=parsed_add_labels,
                remove_labels=parsed_remove_labels
            )
        
        @self.mcp.tool(name="batch_update_tasks")
        async def batch_update_tasks(
            task_ids: str,  # JSON string like '["task1", "task2"]'
            content: Optional[str] = None,
            description: Optional[str] = None,
            labels: Optional[str] = None,  # JSON string like '["urgent", "work"]'
            priority: Optional[int] = None,
            due_string: Optional[str] = None,
            due_date: Optional[str] = None,
            due_datetime: Optional[str] = None,
            due_lang: Optional[str] = None,
            assignee_id: Optional[str] = None,
            duration: Optional[int] = None,
            duration_unit: Optional[str] = None
        ):
            """Batch update multiple tasks with same properties."""
            # Parse task_ids from JSON string
            parsed_task_ids = json.loads(task_ids) if isinstance(task_ids, str) else task_ids
            
            # Parse labels from JSON string if provided
            parsed_labels = None
            if labels:
                if isinstance(labels, str):
                    try:
                        parsed_labels = json.loads(labels)
                    except json.JSONDecodeError:
                        parsed_labels = [labels]
                else:
                    parsed_labels = labels
            
            kwargs = self.api._build_params(
                content=content, description=description, labels=parsed_labels,
                priority=priority, due_string=due_string, due_date=due_date,
                due_datetime=due_datetime, due_lang=due_lang,
                assignee_id=assignee_id, duration=duration,
                duration_unit=duration_unit
            )
            return self.api.batch_update_tasks(task_ids=parsed_task_ids, **kwargs)
        
        @self.mcp.tool(name="batch_complete_tasks")
        async def batch_complete_tasks(task_ids: str):  # JSON string like '["task1", "task2"]'
            """Batch complete multiple tasks."""
            # Parse task_ids from JSON string
            parsed_task_ids = json.loads(task_ids) if isinstance(task_ids, str) else task_ids
            
            return self.api.batch_complete_tasks(task_ids=parsed_task_ids)
        

        @self.mcp.tool(name="get_sections")
        async def get_sections(
            project_id: str,
            limit: Optional[int] = None,
            cursor: Optional[str] = None
        ):
            """Get all sections for a project with optional pagination."""
            return self.api.get_sections(
                project_id=project_id,
                limit=limit or 100,
                cursor=cursor
            )
        
        @self.mcp.tool(name="get_section")
        async def get_section(section_id: str):
            """Get a single section by ID."""
            return self.api.get_section(section_id=section_id)
        
        @self.mcp.tool(name="add_section")
        async def add_section(
            project_id: str,
            name: str,
            order: Optional[int] = None
        ):
            """Create a new section."""
            return self.api.add_section(
                project_id=project_id,
                name=name,
                order=order
            )
        
        @self.mcp.tool(name="update_section")
        async def update_section(section_id: str, name: str):
            """Update an existing section."""
            return self.api.update_section(
                section_id=section_id,
                name=name
            )
        
        @self.mcp.tool(name="delete_section")
        async def delete_section(section_id: str):
            """Delete a section."""
            return self.api.delete_section(section_id=section_id)
    
    def run(self, **kwargs):
        """Run the server."""
        try:
            self.mcp.run(**kwargs)
        finally:
            self.api.close()
