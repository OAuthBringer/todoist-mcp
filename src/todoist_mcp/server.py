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
        
        # Get the actual API method
        tool_method = getattr(self.api, tool_name)
        result = tool_method(**kwargs)
        
        # Convert results to JSON-serializable format
        if tool_name == 'get_projects':
            # Handle both real API (ResultsPaginator) and mock (list) results
            if hasattr(result, '__iter__') and not isinstance(result, list):
                # Real API: ResultsPaginator yields pages, flatten to get individual projects
                projects = []
                for page in result:
                    projects.extend(page)
                return [self._project_to_dict(p) for p in projects]
            else:
                # Mock API: already a list of projects
                return [self._project_to_dict(p) for p in result]
        elif tool_name == 'get_project':
            return self._project_to_dict(result)
        elif tool_name in ['get_tasks', 'get_task']:
            if tool_name == 'get_tasks':
                # Handle both real API (ResultsPaginator) and mock (list) results
                if hasattr(result, '__iter__') and not isinstance(result, list):
                    # Real API: paginated results
                    tasks = []
                    for page in result:
                        tasks.extend(page)
                    return [self._task_to_dict(t) for t in tasks]
                else:
                    # Mock API: already a list
                    return [self._task_to_dict(t) for t in result]
            else:
                return self._task_to_dict(result)
        elif tool_name in ['add_project', 'add_task', 'update_task']:
            if hasattr(result, 'id'):
                return self._project_to_dict(result) if 'project' in tool_name else self._task_to_dict(result)
        
        return result
    
    def _project_to_dict(self, project):
        """Convert Project object to dictionary."""
        if isinstance(project, dict):
            return project  # Already a dict
        if isinstance(project, str):
            return project  # Mock return value
        return {
            'id': project.id,
            'name': project.name,
            'description': project.description,
            'color': project.color,
            'is_shared': project.is_shared,
            'is_favorite': project.is_favorite,
            'order': project.order
        }
    
    def _task_to_dict(self, task):
        """Convert Task object to dictionary."""
        if isinstance(task, dict):
            return task  # Already a dict
        if isinstance(task, str):
            return task  # Mock return value
        return {
            'id': task.id,
            'content': task.content,
            'description': task.description,
            'project_id': task.project_id,
            'is_completed': task.is_completed,
            'priority': task.priority
        }

    def run(self):
        """Run the MCP server."""
        self.mcp.run()

def main():
    server = TodoistMCPServer()
    server.run()
