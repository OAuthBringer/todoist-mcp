"""Unified API v1 client for Todoist."""

import httpx
from typing import Any, Dict, Optional, List


class TodoistV1Client:
    """Direct client for Todoist unified API v1."""
    
    BASE_URL = "https://api.todoist.com/api/v1"
    
    def __init__(self, token: str):
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        self.client = httpx.Client(headers=self.headers)
    
    def get_projects(self, limit: Optional[int] = None, cursor: Optional[str] = None) -> Dict[str, Any]:
        """Get projects with pagination support."""
        params = {}
        if limit:
            params["limit"] = limit
        if cursor:
            params["cursor"] = cursor
        
        response = self.client.get(f"{self.BASE_URL}/projects", params=params)
        response.raise_for_status()
        return response.json()
    
    def get_project(self, project_id: str) -> Dict[str, Any]:
        """Get a single project."""
        response = self.client.get(f"{self.BASE_URL}/projects/{project_id}")
        response.raise_for_status()
        return response.json()
    
    def add_project(self, name: str, parent_id: Optional[str] = None, 
                   color: Optional[str] = None) -> Dict[str, Any]:
        """Create a new project."""
        data = {"name": name}
        if parent_id:
            data["parent_id"] = parent_id
        if color:
            data["color"] = color
        
        response = self.client.post(f"{self.BASE_URL}/projects", json=data)
        response.raise_for_status()
        return response.json()
    
    def get_tasks(self, project_id: Optional[str] = None, limit: Optional[int] = None,
                  cursor: Optional[str] = None, **filters) -> Dict[str, Any]:
        """Get tasks with pagination support."""
        params = {}
        if limit:
            params["limit"] = limit
        if cursor:
            params["cursor"] = cursor
        if project_id:
            params["project_id"] = project_id
        
        # Add other filters
        for key, value in filters.items():
            if value is not None:
                params[key] = value
        
        response = self.client.get(f"{self.BASE_URL}/tasks", params=params)
        response.raise_for_status()
        return response.json()
    
    def get_task(self, task_id: str) -> Dict[str, Any]:
        """Get a single task."""
        response = self.client.get(f"{self.BASE_URL}/tasks/{task_id}")
        response.raise_for_status()
        return response.json()
    
    def add_task(self, content: str, **kwargs) -> Dict[str, Any]:
        """Create a new task."""
        data = {"content": content}
        data.update({k: v for k, v in kwargs.items() if v is not None})
        
        response = self.client.post(f"{self.BASE_URL}/tasks", json=data)
        response.raise_for_status()
        return response.json()
    
    def update_task(self, task_id: str, **kwargs) -> Dict[str, Any]:
        """Update an existing task."""
        data = {k: v for k, v in kwargs.items() if v is not None}
        
        response = self.client.post(f"{self.BASE_URL}/tasks/{task_id}", json=data)
        response.raise_for_status()
        return response.json()
    
    def get_comments(self, task_id: Optional[str] = None, project_id: Optional[str] = None,
                    limit: Optional[int] = None, cursor: Optional[str] = None) -> Dict[str, Any]:
        """Get comments with pagination support."""
        params = {}
        if task_id:
            params["task_id"] = task_id
        if project_id:
            params["project_id"] = project_id
        if limit:
            params["limit"] = limit
        if cursor:
            params["cursor"] = cursor
        
        response = self.client.get(f"{self.BASE_URL}/comments", params=params)
        response.raise_for_status()
        return response.json()
    
    def add_comment(self, content: str, task_id: Optional[str] = None,
                   project_id: Optional[str] = None) -> Dict[str, Any]:
        """Create a new comment."""
        # Validation: must specify exactly one of task_id or project_id
        if task_id and project_id:
            raise ValueError("Comment must be for either task or project, not both")
        if not task_id and not project_id:
            raise ValueError("Must specify either task_id or project_id")
        
        data = {"content": content}
        if task_id:
            data["task_id"] = task_id
        if project_id:
            data["project_id"] = project_id
        
        response = self.client.post(f"{self.BASE_URL}/comments", json=data)
        response.raise_for_status()
        return response.json()
    
    def get_comment(self, comment_id: str) -> Dict[str, Any]:
        """Get a single comment."""
        response = self.client.get(f"{self.BASE_URL}/comments/{comment_id}")
        response.raise_for_status()
        return response.json()
    
    def update_comment(self, comment_id: str, content: str) -> Dict[str, Any]:
        """Update an existing comment."""
        data = {"content": content}
        response = self.client.post(f"{self.BASE_URL}/comments/{comment_id}", json=data)
        response.raise_for_status()
        return response.json()
    
    def delete_comment(self, comment_id: str) -> None:
        """Delete a comment."""
        response = self.client.delete(f"{self.BASE_URL}/comments/{comment_id}")
        response.raise_for_status()
        # Delete operations typically return no content
        return None
    
    def close(self):
        """Close the HTTP client."""
        self.client.close()
