# Overview

## Metadata

- **ID**: cursor-instruction-003
- **Type**: instruction
- **Source**: Cursor
- **Date**: 2026-02-15
- **File**: instructions.md
- **Chunk**: 1/2
- **Words**: 340
- **Topics**: Overview, Core Implementation Guidelines, Development Checklist, Testing Requirements, Deployment Workflow, database, api, authentication, performance, security

## Content

## Overview

This document provides comprehensive implementation instructions for the Task Management System (TMS). The system is designed to handle complex task workflows with real-time collaboration features and advanced prioritization capabilities.


## Core Implementation Guidelines

### Architecture Pattern

The system follows an event-driven microservices architecture with the following key principles:

- Asynchronous Processing: All long-running operations must use message queues (RabbitMQ) to prevent blocking - Database Transactions: Critical task state changes require ACID compliance with snapshot isolation level - Real-time Updates: WebSocket connections for live collaboration must implement reconnection logic with exponential backoff - Caching Strategy: Redis caching layer with 5-minute TTL for frequently accessed task lists

### Authentication Flow

Implement OAuth 2.0 with JWT tokens. Token lifetime should be set to 15 minutes with refresh token rotation enabled. Multi-factor authentication is mandatory for admin accounts as of 2026-02-15.


## Development Checklist

• Setup PostgreSQL database with connection pooling (max 50 connections) - Configure Redis cluster with automatic failover - Implement message queue with persistent storage - Setup API rate limiting (100 requests/minute per user) - Configure CORS for allowed domains - Enable request signing for inter-service communication - Setup centralized logging with ELK stack - Configure monitoring dashboards (Grafana)


## Testing Requirements

### Unit Tests
All business logic must have minimum 85% code coverage. Use dependency injection for testability.

### Integration Tests
Test database transactions, message processing, and external API calls. Database tests must use transaction rollback for isolation.

### End-to-End Tests
Simulate complete workflows including user authentication, task creation, sub-task management, and notification delivery.


## Deployment Workflow

### Pre-deployment

- Run full test suite with coverage analysis - Perform static code analysis and security scanning - Execute performance benchmarks (target: <200ms API response time) - Review database migration scripts for rollback compatibility

### Staging Environment

Deploy to staging with production-equivalent configuration. Run smoke tests and performance tests. Monitor for 48 hours before production release.

### Production Deployment

Use blue-green deployment strategy. Maintain service availability during zero-downtime deployments. Database migrations must complete within maintenance window (Sunday 2-4 AM UTC).
