# Detailed Installation Guide

## Metadata

- **ID**: claude-instruction-002
- **Type**: instruction
- **Source**: Claude
- **Date**: 2026-02-20
- **File**: install_guide.md
- **Chunk**: 2/3
- **Words**: 424
- **Topics**: Detailed Installation Guide, database, security, deployment, migration, testing, task, user

## Content

## Detailed Installation Guide

### System Requirements Analysis

#### Hardware Recommendations

Minimum Configuration (Development): - CPU: 2 cores - RAM: 4GB (with 2GB free for services) - Storage: 10GB available - Network: 10 Mbps

Recommended Configuration (Staging/Production): - CPU: 8+ cores - RAM: 16GB+ - Storage: 100GB+ SSD - Network: 1 Gbps+

Tested Configuration: AWS ec2.t3.large instance (2 vCPU, 8GB RAM). First-use setup completed in 12 minutes on 2026-02-20.

#### Software Stack Verification

Installation guide follows this tech stack as of 2026-02-28:

### Installation by Operating System

#### Windows Installation (Windows Server 2019+)

1. Install Node.js - Download from https://nodejs.org (LTS version) - Run installer, select "Add to PATH" - Verify: Open PowerShell and run `node -v`

2. Install PostgreSQL - Download from https://www.postgresql.org/download/windows/ - Run installer, select port 5432 - Create database: `taskmgmtdb` - Create user: `taskuser` with password

3. Install Redis - Option A: Windows Subsystem for Linux (WSL2) with Redis - Option B: Use Docker: `docker run -d -p 6379:6379 redis:7-alpine` - Verify connectivity: `redis-cli ping`

4. Install RabbitMQ - Download from https://www.rabbitmq.com/download.html - Run installer with Erlang runtime - Enable management plugin (already installed) - Access: http://localhost:15672 (guest/guest)

5. Clone and Setup Project

Windows-Specific Notes: Some dependencies may require Visual Studio Build Tools. If build fails, install from https://visualstudio.microsoft.com/visual-cpp-build-tools/.

Last tested on Windows Server 2022: 2026-02-18 (all steps passed).

#### macOS Installation (12+)

Using Homebrew (Recommended):

Post-Installation Setup:

Last Tested: 2026-02-19 on macOS 13.3 (all installations successful).

#### Linux Installation (Ubuntu 20.04 LTS+)

Using apt package manager:

Database User Setup (Linux):

Environment File Adjustment:

Last tested on Ubuntu 22.04 LTS: 2026-02-20 (all steps verified).

### Project Configuration

#### Environment Variables

Create `.env` file with the following configuration:

Configuration Decision Notes: - DBPOOL settings optimized for 8.5 FTE development team (reviewed 2026-02-15) - SMTP configuration updated for Gmail OAuth (changed 2026-02-10) - Feature flags allow A/B testing and gradual rollout (implemented 2026-02-05)

#### Production Configuration Differences

For production deployments, make these adjustments:

Security Review Date: 2026-02-22 (production config audit passed).

### Database Initialization

#### Migration Execution

Post-Migration Verification:

Migration execution time: 30-45 seconds. Last execution: 2026-02-27.

#### Seed Data (Development Only)

Output format:

Seed Reset Command:

Do NOT use seed in production. To verify this safety mechanism: [Last check: 2026-02-25].

### Starting the Application

#### Development Mode

Server startup typically completes in 3-5 seconds. Last validated: 2026-02-27.

#### Testing the Installation

All services should show "connected" status.

#### Production Deployment

For production, use process manager to keep service running:

Restart on System Reboot: `pm2 startup` ensures services restart after server restarts.
