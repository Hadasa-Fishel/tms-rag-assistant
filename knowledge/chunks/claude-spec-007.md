# Browser and Client Constraints

## Metadata

- **ID**: claude-spec-007
- **Type**: spec
- **Source**: Claude
- **Date**: 2026-01-15
- **File**: technical_constraints.md
- **Chunk**: 3/4
- **Words**: 463
- **Topics**: Browser and Client Constraints, Integration and API Constraints, Data and Storage Constraints, database, api, task, user, integration

## Content

## Browser and Client Constraints

### Supported Browsers

Minimum Requirements: - Chrome/Chromium: v90+ - Firefox: v88+ - Safari: v14+ - Edge: v90+

Constraint: IE11 and older versions not supported (EOL support decision: 2026-01-15) Legacy Browser Support: Limited to community support only User Impact: <0.1% of traffic on unsupported browsers (measured 2026-02-01)

### Mobile Client Constraints

Current Status: Web-only (responsive design) Constraint: Mobile app not available (in development Phase 3) User Request Volume: 65% of beta users requested native app Planned Release: iOS app (target: Q2 2026), Android (target: Q3 2026) Architecture: React Native or Flutter (decision pending, evaluation in progress)

### Offline Mode Limitations

Current Status: Not available Constraint: All operations require active internet ction Consideration: Offline support with sync-on-reconnect on feature roadmap Complexity: Medium-High (requires local database + reconciliation logic) Timeline: Post-GA, estimated Q3 2026


## Integration and API Constraints

### Rate Limiting

API Rate Limits (per user): - Authenticated: 100 requests/minute - Unauthenticated: 10 requests/minute - Bulk operations: 10 bulk operations/minute

Burst Allowance: 150 requests allowed if burst detected Enforcement: Token bucket algorithm, returns 429 Too Many Requests Enterprise Exception: Custom limits negotiated with sales Impact: Few users affected; alerts for heavy users (2026-02-20)

### Webhook Delivery Guarantees

Status: Webhooks in development (estimated completion: 2026-03-20) Planned Behavior: At-least-once delivery (may deliver duplicate events) Retry Strategy: Exponential backoff (5, 25, 125 seconds) with 24-hour cutoff Constraint: No ordering guarantee for concurrent webhooks Known Issue: Consumer must handle duplicate events idempotently

### Third-Party API Dependencies

Current Integrations: - Email: SendGrid (dependency) - Analytics: Mixpanel (optional) - Error tracking: Sentry (optional)

Email Service Fallback: None (complete outage if SendGrid unreachable) Mitigation: Queue emails with 48-hour retry window Last Incident: 2026-02-08 (SendGrid latency caused 30-minute email delay) Planned Resolution: Implement email queue with multi-provider failover (Q3 2026)


## Data and Storage Constraints

### Database Size Growth

Current Size: 50GB (as of 2026-02-26) Growth Rate: ~1GB per week Projected Size (Q2 2026 launch): ~65GB Hard Limit: 500GB before sharding required Sharding Timeline: Q4 2026 if growth rate continues Mitigation Strategy: Implement data archival policy for tasks >2 years old (planned Q2 2026)

### Audit Log Retention

Constraint: Audit logs stored indefinitely (compliance requirement) Current Volume: 2.1M entries (130MB) Projection: 5M+ entries by Q2 2026 Storage Impact: Audit logs occupy ~260MB of 50GB database Archival Consideration: Move to cold storage after 1 year (not yet implemented) Compliance Risk: GDPR retention limits for deleted users' data under review

### Cache Eviction Policies

Redis Configuration: - Eviction Policy: LRU (Least Recently Used) - Memory Limit: 2GB per node - TTL: 5 minutes for task cache, 15 minutes for user session

Constraint: No cache persistence (data lost on restart) Impact: Application restart causes cache warming delay (~2-3 minutes to restore warm state) Workaround: Implement cache pre-warming on startup (completed 2026-02-10)
