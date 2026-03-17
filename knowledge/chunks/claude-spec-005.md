# Overview

## Metadata

- **ID**: claude-spec-005
- **Type**: spec
- **Source**: Claude
- **Date**: 2026-02-15
- **File**: technical_constraints.md
- **Chunk**: 1/4
- **Words**: 520
- **Topics**: Overview, Database Constraints, Concurrency and Real-Time Constraints, database, performance, deployment, migration, monitoring, scaling, caching

## Content

## Overview

This document catalogs known technical constraints, system limitations, and architectural trade-offs that inform decision-making on feature development, capacity planning, and system design. Regular review ensures we maintain awareness of constraints and plan accordingly.


## Database Constraints

### Query Performance Limitations

#### Full-Text Search Performance
Constraint: Search queries on task descriptions on 200K+ tasks have P95 latency of 300-500ms Root Cause: PostgreSQL GiST index traversal complexity on large datasets Current Workaround: Query caching at application layer, debounced search input (500ms) Permanent Solution: Elasticsearch integration planned for Q3 2026 Decision Date: 2026-02-15 Impact: Search experience degradation with user base >50K Related File: `systemspec.md` (FR-4.2 Full-Text Search performance requirements)

#### Aggregation Query Latency
Constraint: Dashboard queries aggregating metrics across 1M+ audit log entries take 2-5 seconds Current Limit: Dashboards updated hourly (not real-time) Workaround: Materialized views refreshed every 60 minutes Planned Upgrade: Real-time metrics engine (timeline: Q3 2026) Severity: Medium (affects internal reporting, not user-facing features) Related File: `planning.md` (Success Metrics and dashboard requirements)

### Transaction Isolation Limits

Constraint: Serializable isolation level provides strongest guarantees but increases deadlock probability Configuration Decision: Use SERIALIZABLE for critical task state changes, READ COMMITTED for searching Deadlock Handling: Automatic retry with exponential backoff (max 3 attempts, 100ms base) Last Deadlock Incident: 2026-02-18 (resolved within 1 minute via auto-retry) Impact: Negligible for typical workloads

### Connection Pool Limitations

Current Configuration: - Max connections: 50 - Current peak: 38 concurrent connections (2026-02-24) - Headroom: 25% - Action Threshold: 45 connections (alert triggered) - Critical Threshold: 48 connections (circuit breaker activates)

Upgrade Path: Scale to 100 connections planned for Q2 2026 when user count hits 50K Last Scaling Event: 2026-01-20 (upgraded from 30 to 50) Related File: `installguide.md` (database configuration), `systemspec.md` (scalability requirements)


## Concurrency and Real-Time Constraints

### WebSocket Scalability Limits

Constraint: Single server can maintain ~1000 WebSocket connections Memory Impact: ~250KBction (queue buffer) Current Connection Count: 150-200 concurrent (peak 2026-02-25) Scaling Strategy: Horizontal scaling with socket.io adapter (Redis-backed) Implementation Status: Ready for deployment, currently using single-server mode Migration Timeline: Trigger when connections exceed 800 Related File: `systemspec.md` (FR-2.3 Real-Time Synchronization), `planning.md` (Phase 3 scalability objectives)

### Concurrent Edit Conflict Resolution

Constraint: Paragraph-level merging for description edits supported; character-level merging not implemented Behavior: Last-write-wins with conflict warning displayed Data Loss Risk: Up to 1 paragraph of concurrent edits (unlikely in practice) Workaround: Task locking during edit (30-second duration visible to other users) Proper Solution: CRDT (Conflict-free Replicated Data Type) implementation planned Q3 2026 Recent Incident: 2026-02-18 (user reported minor text loss in concurrent edit scenario) Related File: `system_spec.md` (FR-1.2 Task Editing), `planning.md` (Risk Assessment - Real-time Collaboration Complexity)

### Message Queue Limits

RabbitMQ Configuration: - Queue memory limit: 256MB - Message TTL: 7 days before expiration - Max messages per queue: 1M - Current accumulation rate: ~50K messages/day

Bottleneck: Notification processing service can handle ~100 messages/second Current Queue Depth: 2K-5K (steady state) Risk Condition: Notification service outage would accumulate backlog, processing blocked items for hours Mitigation: Monitoring alerts at 10K message depth, manual intervention threshold set at 50K Last Critical Incident: 2026-02-12 (resolved by restarting notification service) Planned Improvement: Horizontal scaling of notification workers (target: Q2 2026)
