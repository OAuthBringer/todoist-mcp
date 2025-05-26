# Task-Section Integration

The task-section integration functionality is fully implemented:

- `move_task` accepts and passes `section_id` parameter
- `get_tasks` filters by `section_id` when provided
- `add_task` accepts `section_id` for creating tasks in sections
- All task responses preserve `section_id` field

Tests in `test_task_section_integration.py` verify this functionality.
