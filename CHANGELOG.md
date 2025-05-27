# Changelog

All notable changes to this project will be documented in this file.

## [0.4.0] - 2025-05-26

### Added
- **Sections Support**
  - `get_sections` - List sections for a project with pagination
  - `get_section` - Get single section by ID
  - `add_section` - Create new section in project
  - `update_section` - Update section name
  - `delete_section` - Delete a section
  
- **Labels Management**
  - `get_labels` - List all labels with pagination
  - `get_label` - Get single label by ID
  - `add_label` - Create new label with color and order
  - `update_label` - Update label properties
  - `delete_label` - Delete a label
  
- **Batch Operations**
  - `batch_move_tasks` - Move multiple tasks to project/section
  - `batch_update_labels` - Add/remove labels from multiple tasks
  - `batch_update_tasks` - Update multiple tasks with same properties
  - `batch_complete_tasks` - Complete multiple tasks at once
  
- Comprehensive test coverage for all new features
- Integration tests following established patterns

### Changed
- Updated API client to handle both v1 and v2 endpoints where needed
    - *Note*: The only active v2 endpoint is `DELETE /project` 
- Enhanced error handling for batch operations
- Improved documentation with API version notes

### Removed
- Search functionality was investigated but not implemented due to Todoist API limitations:
  - v1 API (used by this MCP) has no search capability
  - v2 API has search but uses incompatible ID system
  - Cross-version operations are not possible

### Technical Notes
- Discovered Todoist maintains two incompatible API versions:
  - v1 Unified API: Alphanumeric IDs (e.g., `69mF7QcCj9JmXxp8`)
  - v2 REST API: Numeric IDs (e.g., `7246645180`)
- Some features only available in v2 cannot be implemented

## [0.3.0] - 2025-05-25

### Added
- Comment CRUD operations for tasks and projects
  - `get_comments` - List comments with pagination support
  - `get_comment` - Get single comment by ID
  - `add_comment` - Add comment to task or project
  - `update_comment` - Update existing comment
  - `delete_comment` - Delete a comment
- Move task functionality
  - `move_task` - Move tasks between projects, sections, or parents
- Comprehensive test coverage for new features
- Integration tests for comment and move operations

### Changed
- Refactored API client for better code reuse
  - Extracted common HTTP operations to `_request()` method
  - DRY parameter building with `_build_params()`
  - Added context manager support (`with` statement)
  - Centralized validation logic
- Improved error handling and validation messages

## [0.2.0] - Previous Release

### Added
- Full Todoist API v1 integration
- Pagination support for all list endpoints
- Multi-auth support (environment, config file, runtime)

## [0.1.0] - Initial Release

### Added
- Basic task and project management
- FastMCP integration
- Authentication handling
