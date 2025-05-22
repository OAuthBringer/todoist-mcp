"""Todoist MCP Server implementation."""

from typing import Any, Dict, Optional
from fastmcp import FastMCP
from todoist_api_python.api import TodoistAPI
from .auth import AuthManager


class TodoistMCPServer:
    """FastMCP server wrapping Todoist API."""
    
    def __init__(self, token: Optional[str] = None):
        """Initialize server with Todoist API token."""
        self.mcp = FastMCP("Todoist MCP Server")
        
        if token:
            api_token = token
        else:
            auth_manager = AuthManager()
            api_token = auth_manager.get_token()
        
        self.api = TodoistAPI(api_token)
        self._generated_tools = set()
        self._register_core_tools()
    
    def _register_core_tools(self):
        """Register core Todoist API tools manually."""
        
        @self.mcp.tool(name="get_projects")
        async def get_projects(limit: Optional[int] = None):
            return list(self.api.get_projects(limit=limit))
        
        @self.mcp.tool(name="get_project")
        async def get_project(project_id: str):
            return self.api.get_project(project_id=project_id)
        
        @self.mcp.tool(name="add_project")
        async def add_project(name: str, parent_id: Optional[str] = None, color: Optional[str] = None):
            return self.api.add_project(name=name, parent_id=parent_id, color=color)
        
        @self.mcp.tool(name="get_tasks")
        async def get_tasks(project_id: Optional[str] = None, section_id: Optional[str] = None, 
                          label_id: Optional[str] = None, filter: Optional[str] = None, 
                          lang: Optional[str] = None, ids: Optional[list] = None):
            return self.api.get_tasks(project_id=project_id, section_id=section_id,
                                    label_id=label_id, filter=filter, lang=lang, ids=ids)
        
        @self.mcp.tool(name="get_task")
        async def get_task(task_id: str):
            return self.api.get_task(task_id=task_id)
        
        @self.mcp.tool(name="add_task")
        async def add_task(content: str, description: Optional[str] = None, 
                         project_id: Optional[str] = None, section_id: Optional[str] = None,
                         parent_id: Optional[str] = None, order: Optional[int] = None,
                         label_ids: Optional[list] = None, priority: Optional[int] = None,
                         due_string: Optional[str] = None, due_date: Optional[str] = None,
                         due_datetime: Optional[str] = None, due_lang: Optional[str] = None,
                         assignee_id: Optional[str] = None, duration: Optional[int] = None,
                         duration_unit: Optional[str] = None):
            return self.api.add_task(
                content=content, description=description, project_id=project_id,
                section_id=section_id, parent_id=parent_id, order=order,
                label_ids=label_ids, priority=priority, due_string=due_string,
                due_date=due_date, due_datetime=due_datetime, due_lang=due_lang,
                assignee_id=assignee_id, duration=duration, duration_unit=duration_unit
            )
        
        @self.mcp.tool(name="update_task")
        async def update_task(task_id: str, content: Optional[str] = None,
                            description: Optional[str] = None, label_ids: Optional[list] = None,
                            priority: Optional[int] = None, due_string: Optional[str] = None,
                            due_date: Optional[str] = None, due_datetime: Optional[str] = None,
                            due_lang: Optional[str] = None, assignee_id: Optional[str] = None,
                            duration: Optional[int] = None, duration_unit: Optional[str] = None):
            return self.api.update_task(
                task_id=task_id, content=content, description=description,
                label_ids=label_ids, priority=priority, due_string=due_string,
                due_date=due_date, due_datetime=due_datetime, due_lang=due_lang,
                assignee_id=assignee_id, duration=duration, duration_unit=duration_unit
            )
        
        # Track registered tools
        self._generated_tools = {
            'get_projects', 'get_project', 'add_project',
            'get_tasks', 'get_task', 'add_task', 'update_task'
        }
    
    def has_tool(self, tool_name: str) -> bool:
        """Check if tool exists."""
        return tool_name in self._generated_tools
    
    def execute_tool(self, tool_name: str, **kwargs):
        """Execute a tool by name."""
        if not self.has_tool(tool_name):
            raise ValueError(f"Tool '{tool_name}' not found")
        
        method = getattr(self.api, tool_name)
        return method(**kwargs)
