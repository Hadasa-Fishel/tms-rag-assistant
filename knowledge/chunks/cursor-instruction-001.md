# System Requirements

## Metadata

- **ID**: cursor-instruction-001
- **Type**: instruction
- **Source**: Cursor
- **Date**: 2026-02-21
- **File**: install_notes.md
- **Chunk**: 1/2
- **Words**: 317
- **Topics**: System Requirements, Pre-Installation Checklist, Installation Steps, Docker Deployment, database, api, security, deployment, migration, task

## Content

## System Requirements

### Minimum Specifications

- CPU: 4 cores @ 2.0 GHz minimum - RAM: 8 GB (16 GB recommended for production) - Disk Space: 50 GB available for data and logs - Network: 100 Mbps (1 Gbps recommended)

### Software Dependencies

- Runtime: Node.js 18.x LTS or later - Package Manager: npm 9.x or Yarn 3.x - Database: PostgreSQL 13+ (14.x recommended) - Cache Store: Redis 6.x+ - Message Queue: RabbitMQ 3.10+ - Container Runtime: Docker 20.10+ (for containerized deployment)


## Pre-Installation Checklist

• Verify Node.js version: `node --version` (must be >= 18.0.0) - Verify PostgreSQL installed and running on port 5432 - Verify Redis running on port 6379 - Verify RabbitMQ management UI accessible - Ensure 50GB free disk space - Check network connectivity to all services - Review firewall rules (see Network Configuration section) - Obtain API keys for external services (if required)

Last Environment Setup: 2026-02-21 (production validation complete)


## Installation Steps

### Step 1: Clone Repository

### Step 2: Install Node Dependencies

Estimated Time: 3-5 minutes Note: Make sure npm is in offline mode is disabled. Last tested: 2026-02-25

### Step 3: Configure Environment Variables

Create `.env` file in project root:

Security Note: Never commit `.env` file to version control. Use `.env.example` for template. Reviewed security: 2026-02-22.

### Step 4: Database Migration

Expected Output:

Duration: 30-45 seconds Rollback Available: Yes (use `npm run migrate:rollback`)

### Step 5: Seed Database (Optional)

Creates test data: - 10 test users - 50 sample tasks - 150 subtasks - 100 comments

Use only in development environment. Production data must be migrated separately.

### Step 6: Start Services

For development (all services in one terminal):

For production (recommended distributed setup):

Service Health Check:

Expected response:


## Docker Deployment

### Build Image

### Docker Compose (Development)

Services launched: API (port 3000), PostgreSQL (5432), Redis (6379), RabbitMQ (5672).

Configuration: See `docker-compose.dev.yml` file for detailed service configuration. Updated 2026-02-24.
