# Critical Implementation Notes

## Metadata

- **ID**: cursor-instruction-004
- **Type**: instruction
- **Source**: Cursor
- **Date**: 2026-02-10
- **File**: instructions.md
- **Chunk**: 2/2
- **Words**: 199
- **Topics**: Critical Implementation Notes, Known Issues and Workarounds, Version History, Support and References, database, websocket, task, user

## Content

## Critical Implementation Notes

### Task State Management

Tasks must follow strict state transitions:

State changes generate audit logs that must be immutable. As of 2026-02-10, we implemented event sourcing for all task state transitions.

### Notification System

Implement notification batching to prevent notification storms. Maximum of 3 notifications per task update group within 60-second window. Notifications must include deep links to specific task views.

### Concurrent Edit Handling

When multiple users edit the same task simultaneously: 1. Lock the task for 30 seconds after first edit 2. Show conflict warning if others attempt edit 3. Use last-write-wins with change history tracking 4. Merge algorithm for description field changes (paragraph-level)


## Known Issues and Workarounds

### Issue: Memory Leak in WebSocket Handler
Status: Fixed (2026-02-20) Workaround: Manually disconnect idle connections after 5 minutes of inactivity Resolution: Upgraded event emitter and implemented proper cleanup handlers

### Issue: Database Connection Pool Exhaustion
Status: Under Investigation Impact: Occasional service degradation during high load (>500 concurrent users) Temporary Mitigation: Implemented circuit breaker pattern for database operations


## Version History


## Support and References

For questions about specific implementation details: - Database design: See dbchanges.md - User interface: See uiguidelines.md - Installation: See install_notes.md