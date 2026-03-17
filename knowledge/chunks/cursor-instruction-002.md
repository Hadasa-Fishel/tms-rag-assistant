# Network Configuration

## Metadata

- **ID**: cursor-instruction-002
- **Type**: instruction
- **Source**: Cursor
- **Date**: 2026-02-20
- **File**: install_notes.md
- **Chunk**: 2/2
- **Words**: 229
- **Topics**: Network Configuration, Verification Steps, Troubleshooting, Performance Baseline (as of 2026-02-26), Post-Installation Steps, Update Procedure, Support Resources, database, api, performance

## Content

## Network Configuration

### Firewall Rules

### CORS Configuration

Allowed origins (configurable in `config/cors.js`): - `http://localhost:3000` (development) - `https://app.example.com` (production)

Add additional origins only after security team review. Last updated: 2026-02-20.


## Verification Steps

After installation completes:

All checks should pass within 2 minutes of startup.


## Troubleshooting

### Issue: "EADDRINUSE: address already in use :::3000"

Solution: Port 3000 already in use.

### Issue: "connect ECONNREFUSED 127.0.0.1:5432"

Solution: PostgreSQL not running or connection string incorrect.  Last Resolved: 2026-02-19

### Issue: "TimeoutError: connect timeout"

Solution: RabbitMQ connection failing.


## Performance Baseline (as of 2026-02-26)

After installation on recommended hardware: - API response time: <100ms (p95) - Database query latency: <50ms (p95) - Service startup time: <10 seconds - Memory usage: ~250MB (API process) - CPU utilization: <15% (idle)


## Post-Installation Steps

1. User Onboarding: Create first admin user via CLI

2. Configuration Review: Verify all critical settings in admin panel

3. Enable Monitoring: Set up log aggregation and performance monitoring

4. Backup Verification: Test backup and restore procedures on non-production environment

5. Security Hardening: Run security scanning tools (completed on 2026-02-23)


## Update Procedure

To update from v2.0 to v2.1:

Estimated Downtime: <2 minutes with blue-green deployment Rollback Available: Yes, use `git checkout v2.0-stable` and `npm run migrate:rollback`


## Support Resources

- Documentation: `/docs` directory - API Reference: `http://localhost:3000/api/docs` - Issue Tracker: GitHub Issues (private repository) - Status Page: `https://status.example.com`