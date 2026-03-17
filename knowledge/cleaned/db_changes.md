--- title: Database Schema Changes and Evolution category: Database last_updated: 2026-02-25 version: 1.5 tags: ["sql", "schema", "migrations", "tables", "history"] ai_tool_owner: Cursor ---

# Database Schema Changes and Evolution

**Last Updated:** 2026-02-25 **Database System:** PostgreSQL 14.x **Migration Tool:** Flyway

## Migration History

### Migration V1__Initial_Schema.sql (2026-01-10)

Created foundational tables for task management:

```sql CREATE TABLE users ( id UUID PRIMARY KEY, email VARCHAR(255) UNIQUE NOT NULL, password_hash VARCHAR(255) NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP );

CREATE TABLE tasks ( id UUID PRIMARY KEY, user_id UUID NOT NULL REFERENCES users(id), title VARCHAR(255) NOT NULL, description TEXT, status VARCHAR(50) DEFAULT 'DRAFT', priority INT DEFAULT 0, due_date TIMESTAMP, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (user_id) REFERENCES users(id) );

CREATE TABLE task_labels ( id UUID PRIMARY KEY, task_id UUID NOT NULL, label_text VARCHAR(100), color_hex VARCHAR(7), FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE ); ```

### Migration V2__Add_Subtasks_Support.sql (2026-01-20)

Added nested task structure:

```sql CREATE TABLE subtasks ( id UUID PRIMARY KEY, parent_task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE, title VARCHAR(255) NOT NULL, completed BOOLEAN DEFAULT FALSE, completion_percentage INT DEFAULT 0, assigned_to UUID REFERENCES users(id), created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP );

CREATE INDEX idx_subtasks_parent ON subtasks(parent_task_id); CREATE INDEX idx_subtasks_assigned_to ON subtasks(assigned_to); ```

**Rationale:** Direct task dependencies required UI changes to allow nested hierarchies. Initial estimate: 1-2 subtasks per task. Revised to support up to 10 levels deep after requirements review on 2026-01-18.

### Migration V3__Task_Collaboration_Features.sql (2026-02-01)

Added multi-user collaboration:

```sql CREATE TABLE task_assignees ( id UUID PRIMARY KEY, task_id UUID NOT NULL, user_id UUID NOT NULL, assigned_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP, role VARCHAR(50) DEFAULT 'COLLABORATOR', FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE, FOREIGN KEY (user_id) REFERENCES users(id) );

CREATE TABLE task_comments ( id UUID PRIMARY KEY, task_id UUID NOT NULL, user_id UUID NOT NULL, content TEXT NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE, FOREIGN KEY (user_id) REFERENCES users(id) );

CREATE INDEX idx_task_comments_task ON task_comments(task_id); CREATE INDEX idx_task_comments_created ON task_comments(created_at DESC); ```

### Migration V4__Add_Task_Audit_Trail.sql (2026-02-10)

Implemented immutable audit logging:

```sql CREATE TABLE task_audit_log ( id UUID PRIMARY KEY, task_id UUID NOT NULL, user_id UUID, action VARCHAR(100) NOT NULL, old_value JSONB, new_value JSONB, change_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP, ip_address INET, FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE );

CREATE INDEX idx_audit_log_task ON task_audit_log(task_id); CREATE INDEX idx_audit_log_timestamp ON task_audit_log(change_timestamp DESC); ```

**Change Request Date:** 2026-02-08 **Rationale:** Compliance requirements and debugging need full change history. JSONB storage selected for flexibility in tracking different field changes.

### Migration V5__Performance_Optimization.sql (2026-02-23)

Added denormalized statistics and improved query performance:

```sql CREATE TABLE task_stats ( task_id UUID PRIMARY KEY, total_subtasks INT DEFAULT 0, completed_subtasks INT DEFAULT 0, comment_count INT DEFAULT 0, assignee_count INT DEFAULT 0, last_activity TIMESTAMP, FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE );

CREATE INDEX idx_tasks_priority_status ON tasks(priority DESC, status); CREATE INDEX idx_tasks_user_updated ON tasks(user_id, updated_at DESC); ```

**Decision:** Added materialized view with hourly refresh to prevent heavy aggregation queries. Decision made 2026-02-22 after identifying slow dashboard queries (>5s response times).

## Schema Change Log

| Date | Migration | Type | Rationale | |------|-----------|------|-----------| | 2026-01-10 | V1 | Initial | Bootstrap schema | | 2026-01-20 | V2 | Feature | Subtask support requirement | | 2026-02-01 | V3 | Feature | Collaboration enhancement | | 2026-02-10 | V4 | Compliance | Audit trail requirement | | 2026-02-23 | V5 | Optimization | Performance improvement |

## Current Data Volumes (as of 2026-02-25)

- Users: ~15,000 - Tasks: ~250,000 - Subtasks: ~420,000 - Comments: ~800,000 - Audit log entries: ~2.1M

## Performance Considerations

### Query Optimization

All frequently accessed queries must complete within 200ms. Current critical queries: - Get user's active tasks: 45ms (with index) - Get task with dependencies: 120ms - Get task comments with pagination: 80ms

### Backup and Recovery

Daily incremental backups at 2 AM UTC with weekly full backups. Point-in-time recovery enabled for 30 days. Last backup verification: 2026-02-25.

### Connection Pool Settings

``` Max connections: 50 Min idle: 5 Max idle time: 30 seconds Query timeout: 30 seconds Connection timeout: 5 seconds ```

## Future Schema Considerations

- Addition of time-tracking fields (estimated hours, actual hours) - Custom fields support for enterprise tier users - Full-text search indexing for task descriptions - Task template system for recurring task patterns

## Rollback Procedures

All migrations include down scripts for rollback. Last tested: 2026-02-24.

Current rollback time estimate: <5 minutes for Migrations V2-V5.

Migration V1 rollback would result in complete data loss (no down script, initial schema).