"""Authentication manager for Todoist MCP server."""

import os
import json
from typing import Optional


class AuthManager:
    """Manages authentication token for Todoist API."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize auth manager."""
        self.config_path = config_path
        self._runtime_token: Optional[str] = None
    
    def get_token(self) -> str:
        """Get API token from configured sources."""
        # Precedence: runtime > env > config
        if self._runtime_token:
            return self._runtime_token
        
        # Check environment
        env_token = os.getenv('TODOIST_API_TOKEN')
        if env_token:
            return env_token
        
        # Check config file
        if self.config_path:
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    return config['todoist']['api_token']
            except (FileNotFoundError, KeyError, json.JSONDecodeError):
                pass
        
        raise ValueError("No Todoist API token found. Set TODOIST_API_TOKEN environment variable, provide config file, or call set_token()")
    
    def set_token(self, token: str) -> None:
        """Set token at runtime."""
        self._runtime_token = token
