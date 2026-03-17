# Infrastructure and Deployment Constraints

## Metadata

- **ID**: claude-spec-006
- **Type**: spec
- **Source**: Claude
- **Date**: 2026-02-25
- **File**: technical_constraints.md
- **Chunk**: 2/4
- **Words**: 405
- **Topics**: Infrastructure and Deployment Constraints, Feature Limitations, database, api, performance, deployment, migration, scaling, task, user

## Content

## Infrastructure and Deployment Constraints

### Zero-Downtime Deployment Limitations

Constraint: Blue-green deployments require 2x infrastructure capacity during transition Current Status: Feasible up to 500 concurrent users; beyond that requires database-only green environment Database Migration Constraints: Long-running migrations may require manual coordination Risk Mitigation: Only perform deployment during low-traffic windows (Sunday 2-4 AM UTC) Last Deployment: 2026-02-25 (completed in 4 minutes, zero issues)

### Backup and Recovery Constraints

Constraint: Full database backup takes 15-20 minutes on current data volume (50GB) Backup Window: 3 AM UTC daily (low-traffic period) Recovery Speed: Full restoration takes 10-12 minutes, point-in-time recovery adds 5 minutes Current RTO: 15-20 minutes (acceptable for SLA 99.5%) Scalability Issue: Backup time will become problematic at 500GB+ database size Solution: Incremental backups planned, full backups moved to weekly (timeline: Q3 2026)

### Container Resource Allocation

Current Limits per Service: - API Server: 1 CPU, 512MB RAM (headroom: 200MB) - Worker Service: 1 CPU, 256MB RAM (headroom: 50MB) - Notification Service: 0.5 CPU, 256MB RAM

Scaling Triggers: Auto-scale when CPU >70% for >2 minutes or memory usage >90% Max Replicas: 10 instances per service (configured 2026-02-20) Cost Impact: Each additional replica costs ~$50/month in cloud infrastructure


## Feature Limitations

### Task Hierarchy Depth

Constraint: While unlimited nesting is theoretically supported, practical performance degrades at 10+ levels Database Impact: Each level requires additional join operation UI Rendering: Client-side rendering becomes slow beyond 8 levels (measured 2026-02-10) Guidance: Recommend maximum 5 nesting levels for optimal UX Hard Limit: Enforced at 50 levels via database constraint (prevents runaway queries)

### Bulk Operations

Constraint: Bulk update operations limited to 1,000 items (enforced at API level) Rationale: Prevent resource exhaustion from excessive audit logging Workaround: Use batch API endpoint with pagination Performance Impact: Bulk delete/status-change on 1,000 items takes ~500ms User Impact: Enterprise customers with large task volumes reported limitation (2026-02-15) Planned Solution: Async bulk operations API (target: Q2 2026)

### File Attachments

Current Status: Not implemented Identified Constraint: File storage would require dedicated object storage service Architecture Decision: Deferred to Phase 4 (post-GA) Planned Implementation: Integration with S3-compatible storage, max 10MB per file, 100MB per task User Feedback: 3 enterprise customers requested this feature (priority: medium)

### Automation and Workflows

Current Status: Not available in v2.x Constraint: Event processing infrastructure exists but no workflow engine Planned Architecture: Task-based workflow engine with retry logic and dead-letter queues Target Release: Q3 2026 (after GA stabilization) Expected Complexity: Medium (estimated 2 weeks development time)
