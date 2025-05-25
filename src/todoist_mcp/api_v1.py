"""Unified API v1 client for Todoist."""

import httpx
from typing import Any, Dict, Optional, List, Union


class TodoistV1Client:
    """Direct client for Todoist unified API v1."""
    
    BASE_URL = "https://api.todoist.com/api/v1"
    V2_URL = "https://api.todoist.com/api/v2"
    
    def __init__(self, token: str):
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        self.client = httpx.Client(headers=self.headers)
    
    def __enter__(self):
        """Context manager support."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Ensure client is closed on exit."""
        self.close()
    
    def _url(self, endpoint: str, api_version: int = 1) -> str:
        """Construct API URL."""
        base = self.BASE_URL if api_version == 1 else self.V2_URL
        return f"{base}/{endpoint}"
    
    def _build_params(self, **kwargs) -> Dict[str, Any]:
        """Build request parameters, filtering out None values."""
        return {k: v for k, v in kwargs.items() if v is not None}
    
    def _request(self, method: str, endpoint: str, json: Optional[Dict] = None, 
                 params: Optional[Dict] = None, api_version: int = 1) -> Optional[Dict[str, Any]]:
        """Execute HTTP request with standard error handling."""
        url = self._url(endpoint, api_version)
        response = self.client.request(method, url, json=json, params=params)
        response.raise_for_status()
        
        # Handle empty responses (e.g., DELETE)
        if response.status_code == 204 or not response.content:
            return None
        
        return response.json()
    
    def _validate_comment_target(self, task_id: Optional[str], project_id: Optional[str]) -> None:
        """Validate comment target - must specify exactly one."""
        if task_id and project_id:
            raise ValueError("Comment must be for either task or project, not both")
        if not task_id and not project_id:
            raise ValueError("Must specify either task_id or project_id")
    
    def _validate_move_target(self, project_id: Optional[str], section_id: Optional[str], 
                             parent_id: Optional[str]) -> None:
        """Validate move target - must specify at least one."""
        if not any([project_id, section_id, parent_id]):
            raise ValueError("Must specify at least one target: project_id, section_id, or parent_id")
    
    def get_projects(self, limit: Optional[int] = None, cursor: Optional[str] = None) -> Dict[str, Any]:
        """Get projects with pagination support."""
        params = self._build_params(limit=limit, cursor=cursor)
        return self._request("GET", "projects", params=params)
    
    def get_project(self, project_id: str) -> Dict[str, Any]:
        """Get a single project."""
        return self._request("GET", f"projects/{project_id}")
    
    def add_project(self, name: str, parent_id: Optional[str] = None, 
                   color: Optional[str] = None) -> Dict[str, Any]:
        """Create a new project."""
        data = self._build_params(name=name, parent_id=parent_id, color=color)
        return self._request("POST", "projects", json=data)
    
    def update_project(self, project_id: str, **kwargs) -> Dict[str, Any]:
        """Update an existing project."""
        data = self._build_params(**kwargs)
        return self._request("POST", f"projects/{project_id}", json=data)
    
    def delete_project(self, project_id: str) -> None:
        """Delete a project."""
        return self._request("DELETE", f"projects/{project_id}", api_version=2)
    
    def get_tasks(self, project_id: Optional[str] = None, limit: Optional[int] = None,
                  cursor: Optional[str] = None, **filters) -> Dict[str, Any]:
        """Get tasks with pagination support."""
        params = self._build_params(
            project_id=project_id, limit=limit, cursor=cursor, **filters
        )
        return self._request("GET", "tasks", params=params)
    
    def get_task(self, task_id: str) -> Dict[str, Any]:
        """Get a single task."""
        return self._request("GET", f"tasks/{task_id}")
    
    def add_task(self, content: str, **kwargs) -> Dict[str, Any]:
        """Create a new task."""
        data = self._build_params(content=content, **kwargs)
        return self._request("POST", "tasks", json=data)
    
    def update_task(self, task_id: str, **kwargs) -> Dict[str, Any]:
        """Update an existing task."""
        data = self._build_params(**kwargs)
        return self._request("POST", f"tasks/{task_id}", json=data)
    
    def get_comments(self, task_id: Optional[str] = None, project_id: Optional[str] = None,
                    limit: Optional[int] = None, cursor: Optional[str] = None) -> Dict[str, Any]:
        """Get comments with pagination support."""
        params = self._build_params(
            task_id=task_id, project_id=project_id, limit=limit, cursor=cursor
        )
        return self._request("GET", "comments", params=params)
    
    def add_comment(self, content: str, task_id: Optional[str] = None,
                   project_id: Optional[str] = None) -> Dict[str, Any]:
        """Create a new comment."""
        self._validate_comment_target(task_id, project_id)
        data = self._build_params(content=content, task_id=task_id, project_id=project_id)
        return self._request("POST", "comments", json=data)
    
    def get_comment(self, comment_id: str) -> Dict[str, Any]:
        """Get a single comment."""
        return self._request("GET", f"comments/{comment_id}")
    
    def update_comment(self, comment_id: str, content: str) -> Dict[str, Any]:
        """Update an existing comment."""
        data = self._build_params(content=content)
        return self._request("POST", f"comments/{comment_id}", json=data)
    
    def delete_comment(self, comment_id: str) -> None:
        """Delete a comment."""
        return self._request("DELETE", f"comments/{comment_id}")
    
    def move_task(self, task_id: str, project_id: Optional[str] = None,
                  section_id: Optional[str] = None, parent_id: Optional[str] = None) -> Dict[str, Any]:
        """Move a task to a different project, section, or parent."""
        self._validate_move_target(project_id, section_id, parent_id)
        data = self._build_params(
            project_id=project_id, section_id=section_id, parent_id=parent_id
        )
        return self._request("POST", f"tasks/{task_id}/move", json=data)
    
    def close(self):
        """Close the HTTP client."""
        self.client.close()
