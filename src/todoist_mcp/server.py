"""Todoist MCP Server implementation using unified API v1."""

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
            result = self.api.get_projects(limit=limit, cursor=cursor)
            return result
        
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
                         labels: Optional[List[str]] = None, priority: Optional[int] = None,
                         due_string: Optional[str] = None, due_date: Optional[str] = None,
                         due_datetime: Optional[str] = None, due_lang: Optional[str] = None,
                         assignee_id: Optional[str] = None, duration: Optional[int] = None,
                         duration_unit: Optional[str] = None):
            """Create a new task."""
            return self.api.add_task(
                content=content, description=description, project_id=project_id,
                section_id=section_id, parent_id=parent_id, order=order,
                labels=labels, priority=priority, due_string=due_string,
                due_date=due_date, due_datetime=due_datetime, due_lang=due_lang,
                assignee_id=assignee_id, duration=duration, duration_unit=duration_unit
            )
        
        @self.mcp.tool(name="update_task")
        async def update_task(task_id: str, content: Optional[str] = None,
                            description: Optional[str] = None, labels: Optional[List[str]] = None,
                            priority: Optional[int] = None, due_string: Optional[str] = None,
                            due_date: Optional[str] = None, due_datetime: Optional[str] = None,
                            due_lang: Optional[str] = None, assignee_id: Optional[str] = None,
                            duration: Optional[int] = None, duration_unit: Optional[str] = None):
            """Update an existing task."""
            return self.api.update_task(
                task_id=task_id, content=content, description=description,
                labels=labels, priority=priority, due_string=due_string,
                due_date=due_date, due_datetime=due_datetime, due_lang=due_lang,
                assignee_id=assignee_id, duration=duration, duration_unit=duration_unit
            )
    
    def run(self, **kwargs):
        """Run the server."""
        try:
            self.mcp.run(**kwargs)
        finally:
            self.api.close()
