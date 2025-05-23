# Todoist MCP Server

MCP server for Todoist API integration. Published to [PyPI](https://pypi.org/project/todoist-mcp/)

## Status
✅ **Full Functionality** - Now using Todoist unified API v1 with proper pagination support

## Features
- Full cursor-based pagination for tasks and projects
- Configurable limit parameter for all list endpoints
- Multi-auth support (environment, config file, runtime)
- Complete task and project management capabilities
- Error handling with detailed error messages

## Installation
```bash
pip install todoist-mcp
```

## Claude Desktop Configuration

Add to your `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "todoist": {
      "command": "uvx",
      "args": ["todoist-mcp"],
      "env": {
        "TODOIST_API_TOKEN": "your_token_here"
      }
    }
  }
}
```

## AmazonQ Developer CLI Configuration

Add to your `.amazonq/mcp.json`:

```json
{
  "mcpServers": {
    "todoist": {
      "command": "uvx",
      "args": ["todoist-mcp"],
      "env": {
        "TODOIST_API_TOKEN": "your_token_here"
      }
    }
  }
}
```

### Alternative: Using mcp-gen

For complex MCP configuration management such as in providing configurations for different contexts ot teams, use [mcp-gen](https://github.com/OAuthBringer/mcp-gen) with YAML:

See https://github.com/OAuthBringer/mcp-gen/examples for more full examples


```yaml
# mcp-config.yaml

servers:
    todoist:
      command: uvx
      args: [todoist-mcp]
      env:
        TODOIST_API_TOKEN: {{ secrets.TODOIST_API_TOKEN }}
    ```
Then generate your configuration:
```bash
`mcp-gen generate -c mcp-config.yaml -s secrets-file.yaml`
```

## Configuration
Authentication options (in order of precedence):
1. Runtime: Pass token when creating client
2. Config file: `~/.config/todoist/config.json` with `{"api_token": "your_token"}`
3. Environment: Set `TODOIST_API_TOKEN`

## Available Tools

### Projects
- `get_projects` - List projects with pagination (limit, cursor)
- `get_project` - Get single project by ID
- `add_project` - Create new project

### Tasks
- `get_tasks` - List tasks with pagination and filters
- `get_task` - Get single task by ID
- `add_task` - Create new task
- `update_task` - Update existing task

## Technical Details
- Built with FastMCP v2.3.3+
- Python 3.11+
- Direct API v1 integration using httpx
- No dependency on todoist-api-python SDK

## Development

```bash
# Clone repository
git clone https://github.com/OAuthBringer/todoist-mcp
cd todoist-mcp

# Create virtual environment
uv venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install dependencies
uv pip install -e .
uv pip install -e ".[dev]"

# Run tests
pytest
```
