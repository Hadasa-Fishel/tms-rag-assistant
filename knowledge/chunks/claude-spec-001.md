# System Overview

## Metadata

- **ID**: claude-spec-001
- **Type**: spec
- **Source**: Claude
- **Date**: 2026-02-20
- **File**: system_spec.md
- **Chunk**: 1/4
- **Words**: 811
- **Topics**: System Overview, Functional Requirements, database, performance, websocket, task, user, workflow

## Content

## System Overview

The Task Management System is a modern, scalable web application designed to enable individuals and teams to organize, prioritize, and collaborate on task-based work. The system provides real-time synchronization, advanced filtering, and comprehensive audit trails for compliance requirements.


## Functional Requirements

### FR-1: Task Management

#### FR-1.1 Task Creation
- Users can create tasks with title (required), description (optional), due date, and priority level - Tasks automatically assigned to creating user - Initial status: DRAFT - Validation: Title must be 1-255 characters, due date must be future date (optional) - Error Codes: `400` (Bad Request - invalid input), `401` (Unauthorized - not authenticated), `403` (Forbidden - no create permission) - Expected Performance: <100ms creation time - Last Verified: 2026-02-20

#### FR-1.2 Task Editing
- Task owner and assignees can modify task properties - Concurrent edit detection with conflict resolution - Change history automatically recorded in audit table - Field-level granularity for audit logging - Last modification timestamp updated on save - Database transaction isolation: SERIALIZABLE for critical updates - Error Codes: `400` (Bad Request - invalid field), `403` (Forbidden - insufficient permissions), `409` (Conflict - concurrent modification), `404` (Not Found - task doesn't exist) - Expected Performance: <150ms for updates with audit logging - Implementation Date: 2026-01-20

#### FR-1.3 Task Status Workflow

Alternative path: Any state → BLOCKED (requires reason field, minimum 10 characters)

Status transitions trigger notifications to assignees and watchers. State machine validation enforced at application layer (database constraints added 2026-02-10).

#### FR-1.4 Task Deletion
- Soft-delete implementation (tasks marked as deleted, not removed) - Cascade behavior: Subtasks, comments, and audit logs preserved - Hard-delete available only to administrators after 90-day grace period - Deleted task data accessible only via audit logs - Error Codes: `403` (Forbidden - insufficient permissions), `404` (Not Found - task doesn't exist), `410` (Gone - task permanently deleted) - Changed to soft-delete on 2026-02-08 for compliance requirements

### FR-2: Collaboration Features

#### FR-2.1 Task Assignment
- Multiple users can be assigned to single task - Roles: OWNER, ASSIGNEE, REVIEWER, WATCHER - Role defines allowed actions (OWNER can delete, REVIEWER can only view) - Assignment notifications sent immediately - Unassignment triggers notification - Error Codes: `400` (Bad Request - invalid role), `403` (Forbidden - cannot assign users), `404` (Not Found - user or task doesn't exist), `422` (Unprocessable Entity - max assignees exceeded) - Database constraint (2026-02-01): Maximum 50 assignees per task

#### FR-2.2 Comments and Discussions
- Users can add comments to tasks (max 5000 characters) - Thread replies supported with nesting limit of 1 level - Comment edit capability (only by author, limited to 5 hours post-creation) - Comment deletion soft-delete, preserves edit history - @mention notification system implemented (2026-02-15) - Comment indexing for full-text search (PostgreSQL GiST index) - Error Codes: `400` (Bad Request - comment too long), `403` (Forbidden - cannot edit others' comments), `404` (Not Found - comment doesn't exist), `410` (Gone - comment permanently deleted)

#### FR-2.3 Real-Time Synchronization
- WebSocket connections for live updates - Automatic reconnection with exponential backoff (250ms, 500ms, 1000ms max) - Message acknowledgment required (timeout: 5 seconds) - Heartbeat interval: 30 seconds (detects stale connections) - Maximum 10MB message queue per client (prevents memory bloat) - Error Codes: `503` (Service Unavailable - WebSocket service down), `1006` (Abnormal Closure), `1011` (Server Error) - Implemented: 2026-01-25; Memory leak fix: 2026-02-20

### FR-3: Task Hierarchy and Dependencies

#### FR-3.1 Subtasks
- Support unlimited nesting depth (practical limit: 10 levels) - Subtask completion percentage: 0-100 - Parent task completion auto-calculated from subtasks - Constraint: Cannot create subtask under COMPLETED parent - Delete parent task cascades subtask deletion (with audit trail) - Database structure: Adjacency list model with materialized path support (added 2026-02-23)

#### FR-3.2 Task Dependencies
- Task A cannot be started until Task B is completed (blocking relations) - Cycle detection prevents circular dependencies - Dependency violations trigger warning but not block (designed 2026-02-18) - Daily dependency audit report

### FR-4: Search and Filtering

#### FR-4.1 Basic Filtering
- Filter by: Status, Priority, Assignee, Due Date Range, Labels - Multi-select support (OR logic within category, AND between categories) - Saved filter presets (up to 10 per user) - Filter count indicator - Error Codes: `400` (Bad Request - invalid filter syntax), `422` (Unprocessable Entity - invalid date range)

#### FR-4.2 Full-Text Search
- Search task titles and descriptions - Partial matching and fuzzy search support - Database: PostgreSQL full-text search (tsvector fields) - Index updated on every task modification - Error Codes: `400` (Bad Request - search query too long), `503` (Service Unavailable - search index unavailable) - Response time target: <500ms for 250K task database - Verified: 2026-02-24 (avg 320ms performance)

#### FR-4.3 Sorting Options
- Primary sort: Due date, Priority, Creation date, Last modified - Secondary sort: By assignee name or task status - Sort order: Ascending or descending, persistent per user
