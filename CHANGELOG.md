# Changelog

All notable changes to this project will be documented in this file.

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
