---
title: Technical Constraints and Limitations
category: Specifications
last_updated: 2026-02-26
version: 1.8
tags: ["constraints", "limitations", "trade-offs", "architecture", "scalability"]
ai_tool_owner: Claude_Code
---

# Technical Constraints and Limitations

**Document Version:** 1.8  
**Last Updated:** 2026-02-26  
**Scope:** Known Limitations and Architectural Constraints  
**Audience:** Development Team, Product Management, Technical Leadership

## Overview

This document catalogs known technical constraints, system limitations, and architectural trade-offs that inform decision-making on feature development, capacity planning, and system design. Regular review ensures we maintain awareness of constraints and plan accordingly.

## Database Constraints

### Query Performance Limitations

#### Full-Text Search Performance
**Constraint:** Search queries on task descriptions on 200K+ tasks have P95 latency of 300-500ms  
**Root Cause:** PostgreSQL GiST index traversal complexity on large datasets  
**Current Workaround:** Query caching at application layer, debounced search input (500ms)  
**Permanent Solution:** Elasticsearch integration planned for Q3 2026  
**Decision Date:** 2026-02-15  
**Impact:** Search experience degradation with user base >50K  
**Related File:** `system_spec.md` (FR-4.2 Full-Text Search performance requirements)  

#### Aggregation Query Latency
**Constraint:** Dashboard queries aggregating metrics across 1M+ audit log entries take 2-5 seconds  
**Current Limit:** Dashboards updated hourly (not real-time)  
**Workaround:** Materialized views refreshed every 60 minutes  
**Planned Upgrade:** Real-time metrics engine (timeline: Q3 2026)  
**Severity:** Medium (affects internal reporting, not user-facing features)  
**Related File:** `planning.md` (Success Metrics and dashboard requirements)

### Transaction Isolation Limits

**Constraint:** Serializable isolation level provides strongest guarantees but increases deadlock probability  
**Configuration Decision:** Use SERIALIZABLE for critical task state changes, READ COMMITTED for searching  
**Deadlock Handling:** Automatic retry with exponential backoff (max 3 attempts, 100ms base)  
**Last Deadlock Incident:** 2026-02-18 (resolved within 1 minute via auto-retry)  
**Impact:** Negligible for typical workloads

### Connection Pool Limitations

**Current Configuration:**
- Max connections: 50
- Current peak: 38 concurrent connections (2026-02-24)
- Headroom: 25%
- Action Threshold: 45 connections (alert triggered)
- Critical Threshold: 48 connections (circuit breaker activates)

**Upgrade Path:** Scale to 100 connections planned for Q2 2026 when user count hits 50K  
**Last Scaling Event:** 2026-01-20 (upgraded from 30 to 50)  
**Related File:** `install_guide.md` (database configuration), `system_spec.md` (scalability requirements)

## Concurrency and Real-Time Constraints

### WebSocket Scalability Limits

**Constraint:** Single server can maintain ~1000 WebSocket connections  
**Memory Impact:** ~250KBction (queue buffer)
**Current Connection Count:** 150-200 concurrent (peak 2026-02-25)  
**Scaling Strategy:** Horizontal scaling with socket.io adapter (Redis-backed)  
**Implementation Status:** Ready for deployment, currently using single-server mode  
**Migration Timeline:** Trigger when connections exceed 800  
**Related File:** `system_spec.md` (FR-2.3 Real-Time Synchronization), `planning.md` (Phase 3 scalability objectives)

### Concurrent Edit Conflict Resolution

**Constraint:** Paragraph-level merging for description edits supported; character-level merging not implemented  
**Behavior:** Last-write-wins with conflict warning displayed  
**Data Loss Risk:** Up to 1 paragraph of concurrent edits (unlikely in practice)  
**Workaround:** Task locking during edit (30-second duration visible to other users)  
**Proper Solution:** CRDT (Conflict-free Replicated Data Type) implementation planned Q3 2026  
**Recent Incident:** 2026-02-18 (user reported minor text loss in concurrent edit scenario)  
**Related File:** `system_spec.md` (FR-1.2 Task Editing), `planning.md` (Risk Assessment - Real-time Collaboration Complexity)

### Message Queue Limits

**RabbitMQ Configuration:**
- Queue memory limit: 256MB
- Message TTL: 7 days before expiration
- Max messages per queue: 1M
- Current accumulation rate: ~50K messages/day

**Bottleneck:** Notification processing service can handle ~100 messages/second  
**Current Queue Depth:** 2K-5K (steady state)  
**Risk Condition:** Notification service outage would accumulate backlog, processing blocked items for hours  
**Mitigation:** Monitoring alerts at 10K message depth, manual intervention threshold set at 50K  
**Last Critical Incident:** 2026-02-12 (resolved by restarting notification service)  
**Planned Improvement:** Horizontal scaling of notification workers (target: Q2 2026)

## Infrastructure and Deployment Constraints

### Zero-Downtime Deployment Limitations

**Constraint:** Blue-green deployments require 2x infrastructure capacity during transition  
**Current Status:** Feasible up to 500 concurrent users; beyond that requires database-only green environment  
**Database Migration Constraints:** Long-running migrations may require manual coordination  
**Risk Mitigation:** Only perform deployment during low-traffic windows (Sunday 2-4 AM UTC)  
**Last Deployment:** 2026-02-25 (completed in 4 minutes, zero issues)

### Backup and Recovery Constraints

**Constraint:** Full database backup takes 15-20 minutes on current data volume (50GB)  
**Backup Window:** 3 AM UTC daily (low-traffic period)  
**Recovery Speed:** Full restoration takes 10-12 minutes, point-in-time recovery adds 5 minutes  
**Current RTO:** 15-20 minutes (acceptable for SLA 99.5%)  
**Scalability Issue:** Backup time will become problematic at 500GB+ database size  
**Solution:** Incremental backups planned, full backups moved to weekly (timeline: Q3 2026)

### Container Resource Allocation

**Current Limits per Service:**
- API Server: 1 CPU, 512MB RAM (headroom: 200MB)
- Worker Service: 1 CPU, 256MB RAM (headroom: 50MB)
- Notification Service: 0.5 CPU, 256MB RAM

**Scaling Triggers:** Auto-scale when CPU >70% for >2 minutes or memory usage >90%  
**Max Replicas:** 10 instances per service (configured 2026-02-20)  
**Cost Impact:** Each additional replica costs ~$50/month in cloud infrastructure

## Feature Limitations

### Task Hierarchy Depth

**Constraint:** While unlimited nesting is theoretically supported, practical performance degrades at 10+ levels  
**Database Impact:** Each level requires additional join operation  
**UI Rendering:** Client-side rendering becomes slow beyond 8 levels (measured 2026-02-10)  
**Guidance:** Recommend maximum 5 nesting levels for optimal UX  
**Hard Limit:** Enforced at 50 levels via database constraint (prevents runaway queries)

### Bulk Operations

**Constraint:** Bulk update operations limited to 1,000 items (enforced at API level)  
**Rationale:** Prevent resource exhaustion from excessive audit logging  
**Workaround:** Use batch API endpoint with pagination  
**Performance Impact:** Bulk delete/status-change on 1,000 items takes ~500ms  
**User Impact:** Enterprise customers with large task volumes reported limitation (2026-02-15)  
**Planned Solution:** Async bulk operations API (target: Q2 2026)

### File Attachments

**Current Status:** Not implemented  
**Identified Constraint:** File storage would require dedicated object storage service  
**Architecture Decision:** Deferred to Phase 4 (post-GA)  
**Planned Implementation:** Integration with S3-compatible storage, max 10MB per file, 100MB per task  
**User Feedback:** 3 enterprise customers requested this feature (priority: medium)

### Automation and Workflows

**Current Status:** Not available in v2.x  
**Constraint:** Event processing infrastructure exists but no workflow engine  
**Planned Architecture:** Task-based workflow engine with retry logic and dead-letter queues  
**Target Release:** Q3 2026 (after GA stabilization)  
**Expected Complexity:** Medium (estimated 2 weeks development time)

## Browser and Client Constraints

### Supported Browsers

**Minimum Requirements:**
- Chrome/Chromium: v90+
- Firefox: v88+
- Safari: v14+
- Edge: v90+

**Constraint:** IE11 and older versions not supported (EOL support decision: 2026-01-15)  
**Legacy Browser Support:** Limited to community support only  
**User Impact:** <0.1% of traffic on unsupported browsers (measured 2026-02-01)

### Mobile Client Constraints

**Current Status:** Web-only (responsive design)  
**Constraint:** Mobile app not available (in development Phase 3)  
**User Request Volume:** 65% of beta users requested native app  
**Planned Release:** iOS app (target: Q2 2026), Android (target: Q3 2026)  
**Architecture:** React Native or Flutter (decision pending, evaluation in progress)

### Offline Mode Limitations

**Current Status:** Not available  
**Constraint:** All operations require active internet ction  
**Consideration:** Offline support with sync-on-reconnect on feature roadmap  
**Complexity:** Medium-High (requires local database + reconciliation logic)  
**Timeline:** Post-GA, estimated Q3 2026

## Integration and API Constraints

### Rate Limiting

**API Rate Limits (per user):**
- Authenticated: 100 requests/minute
- Unauthenticated: 10 requests/minute
- Bulk operations: 10 bulk operations/minute

**Burst Allowance:** 150 requests allowed if burst detected  
**Enforcement:** Token bucket algorithm, returns 429 Too Many Requests  
**Enterprise Exception:** Custom limits negotiated with sales  
**Impact:** Few users affected; alerts for heavy users (2026-02-20)

### Webhook Delivery Guarantees

**Status:** Webhooks in development (estimated completion: 2026-03-20)  
**Planned Behavior:** At-least-once delivery (may deliver duplicate events)  
**Retry Strategy:** Exponential backoff (5, 25, 125 seconds) with 24-hour cutoff  
**Constraint:** No ordering guarantee for concurrent webhooks  
**Known Issue:** Consumer must handle duplicate events idempotently

### Third-Party API Dependencies

**Current Integrations:**
- Email: SendGrid (dependency)
- Analytics: Mixpanel (optional)
- Error tracking: Sentry (optional)

**Email Service Fallback:** None (complete outage if SendGrid unreachable)  
**Mitigation:** Queue emails with 48-hour retry window  
**Last Incident:** 2026-02-08 (SendGrid latency caused 30-minute email delay)  
**Planned Resolution:** Implement email queue with multi-provider failover (Q3 2026)

## Data and Storage Constraints

### Database Size Growth

**Current Size:** 50GB (as of 2026-02-26)  
**Growth Rate:** ~1GB per week
**Projected Size (Q2 2026 launch):** ~65GB  
**Hard Limit:** 500GB before sharding required  
**Sharding Timeline:** Q4 2026 if growth rate continues  
**Mitigation Strategy:** Implement data archival policy for tasks >2 years old (planned Q2 2026)

### Audit Log Retention

**Constraint:** Audit logs stored indefinitely (compliance requirement)  
**Current Volume:** 2.1M entries (130MB)  
**Projection:** 5M+ entries by Q2 2026  
**Storage Impact:** Audit logs occupy ~260MB of 50GB database  
**Archival Consideration:** Move to cold storage after 1 year (not yet implemented)  
**Compliance Risk:** GDPR retention limits for deleted users' data under review

### Cache Eviction Policies

**Redis Configuration:**
- Eviction Policy: LRU (Least Recently Used)
- Memory Limit: 2GB per node
- TTL: 5 minutes for task cache, 15 minutes for user session

**Constraint:** No cache persistence (data lost on restart)  
**Impact:** Application restart causes cache warming delay (~2-3 minutes to restore warm state)  
**Workaround:** Implement cache pre-warming on startup (completed 2026-02-10)

## Known Performance Bottlenecks

| Bottleneck | Severity | Impact | Workaround | Priority |
|------------|----------|--------|-----------|----------|
| Full-text search on large datasets | Medium | Search latency 300-500ms | Query caching | 2026-Q3 |
| Aggregation queries for dashboards | Medium | Dashboard updating slow | Materialized views | 2026-Q3 |
| WebSocket limit at 1000 connections | Low | Limited concurrent users | Horizontal scaling ready | 2026-Q2 |
| Bulk operations on 1000+ items | Medium | User patience/UX | Async API planned | 2026-Q2 |
| Email delivery latency | Low | Notifications delayed | Multi-provider failover | 2026-Q3 |

## Compliance and Security Constraints

### Data Residency Limitations

**Constraint:** All data must reside in US East region (GDPR-complicit)  
**Impact:** No direct EU data center (latency for EU users ~100ms)  
**Mitigation:** EU data center planned for Q3 2026 (compliance update: 2026-02-20)  
**Cost Impact:** Additional $8K/month infrastructure cost

### Audit Log Immutability

**Constraint:** Audit logs cannot be modified (cryptographic hash verification planned)  
**Current Status:** Software enforcement only  
**Planned Enhancement:** Blockchain-backed verification (timeline: Q4 2026)  
**Compliance Requirement:** Monthly audit log integrity checks (initiated 2026-02-20)

## Recommendation for Feature Decisions

When evaluating new features, assess against these constraints:

1. **Will this scale to 100x current user base?**
2. **What is the impact on database query performance?**
3. **Does this require architectural changes?**
4. **What are the compliance implications?**
5. **Can this be implemented with current infrastructure budget?**

**Last Review Date:** 2026-02-26  
**Next Review Scheduled:** 2026-03-26 (post-Phase 3 checkpoint)
