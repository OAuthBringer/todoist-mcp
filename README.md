# Todoist MCP Server

MCP server for Todoist API integration. Published to [PyPI](https://pypi.org/project/todoist-mcp/)

## Status
✅ **Full Functionality** - Now using Todoist unified API v1 with proper pagination support

**v0.4.0** - Major expansion: Sections support, Labels management, and Batch operations

### Important API Notes
Todoist has numerous API versions with incompatible ID systems:
- **v1 Unified API** (Todoist official ): Uses alphanumeric IDs (e.g., `69mF7QcCj9JmXxp8`)
- **v2 REST API**: Uses numeric IDs (e.g., `7246645180`)

This incompatibility means certain features like server-side search are not available in this MCP implementation, as search only exists in v2 but returns IDs incompatible with v1 operations.

## Features
- Full cursor-based pagination for all endpoints
- Configurable limit parameter for all list endpoints
- Multi-auth support (environment, config file, runtime)
- Complete task and project management capabilities
- **Sections support** (v0.4.0): CRUD operations for project sections
- **Labels management** (v0.4.0): CRUD operations for labels
- **Batch operations** (v0.4.0): Move, update, complete multiple tasks at once
- Comment CRUD operations for tasks and projects
- Move tasks between projects, sections, and parents
- Error handling with detailed error messages

### Limitations
- No server-side search (due to v1/v2 API incompatibility)
- Client-side filtering only for task queries

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
- `add_task` - Create new task with all properties
- `update_task` - Update existing task
- `move_task` - Move task to different project, section, or parent

### Sections (v0.4.0)
- `get_sections` - List sections for a project with pagination
- `get_section` - Get single section by ID
- `add_section` - Create new section in project
- `update_section` - Update section name
- `delete_section` - Delete a section

### Labels (v0.4.0)
- `get_labels` - List all labels with pagination
- `get_label` - Get single label by ID
- `add_label` - Create new label
- `update_label` - Update label properties
- `delete_label` - Delete a label

### Batch Operations (v0.4.0)
- `batch_move_tasks` - Move multiple tasks to project/section
- `batch_update_labels` - Add/remove labels from multiple tasks
- `batch_update_tasks` - Update multiple tasks with same properties
- `batch_complete_tasks` - Complete multiple tasks at once

### Comments
- `get_comments` - List comments for task/project with pagination
- `get_comment` - Get single comment by ID
- `add_comment` - Add comment to task or project
- `update_comment` - Update existing comment
- `delete_comment` - Delete a comment

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
