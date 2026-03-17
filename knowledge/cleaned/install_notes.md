--- title: Installation and Setup Notes category: DevOps last_updated: 2026-02-26 version: 2.1 tags: ["setup", "installation", "requirements", "troubleshooting"] ai_tool_owner: Cursor ---
# Installation and Setup Notes

**Last Updated:** 2026-02-26 **Installation Version:** 2.1 **Tested Environments:** Windows Server 2019+, macOS 12+, Ubuntu 20.04 LTS+

## System Requirements

### Minimum Specifications

- **CPU:** 4 cores @ 2.0 GHz minimum - **RAM:** 8 GB (16 GB recommended for production) - **Disk Space:** 50 GB available for data and logs - **Network:** 100 Mbps (1 Gbps recommended)

### Software Dependencies

- **Runtime:** Node.js 18.x LTS or later - **Package Manager:** npm 9.x or Yarn 3.x - **Database:** PostgreSQL 13+ (14.x recommended) - **Cache Store:** Redis 6.x+ - **Message Queue:** RabbitMQ 3.10+ - **Container Runtime:** Docker 20.10+ (for containerized deployment)

## Pre-Installation Checklist

- [ ] Verify Node.js version: `node --version` (must be >= 18.0.0) - [ ] Verify PostgreSQL installed and running on port 5432 - [ ] Verify Redis running on port 6379 - [ ] Verify RabbitMQ management UI accessible - [ ] Ensure 50GB free disk space - [ ] Check network connectivity to all services - [ ] Review firewall rules (see Network Configuration section) - [ ] Obtain API keys for external services (if required)

**Last Environment Setup:** 2026-02-21 (production validation complete)

## Installation Steps

### Step 1: Clone Repository

```bash git clone https://github.com/company/task-management-system.git cd task-management-system git checkout v2.1-stable ```

### Step 2: Install Node Dependencies

```bash npm install
# or
yarn install ```

**Estimated Time:** 3-5 minutes **Note:** Make sure npm is in offline mode is disabled. Last tested: 2026-02-25

### Step 3: Configure Environment Variables

Create `.env` file in project root:

```
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/task_mgmt_db DB_POOL_SIZE=50 DB_POOL_IDLE_TIMEOUT=30000

# Redis Configuration
REDIS_URL=redis://localhost:6379 REDIS_DB_NUMBER=0

# RabbitMQ Configuration
RABBITMQ_URL=amqp://guest:guest@localhost:5672 RABBITMQ_VHOST=/

# Application Settings
NODE_ENV=development PORT=3000 LOG_LEVEL=info API_BASE_URL=http://localhost:3000

# JWT Secret
JWT_SECRET=your-secret-key-min-32-characters JWT_EXPIRY=15m

# Email Service (Optional)
SMTP_HOST=smtp.gmail.com SMTP_PORT=587 SMTP_USER=your-email@gmail.com SMTP_PASS=your-app-password ```

**Security Note:** Never commit `.env` file to version control. Use `.env.example` for template. Reviewed security: 2026-02-22.

### Step 4: Database Migration

```bash npm run migrate
# This runs Flyway migrations in sequence (V1 through V5)
```

**Expected Output:** ``` Executing migration V1__Initial_Schema.sql Executing migration V2__Add_Subtasks_Support.sql Executing migration V3__Task_Collaboration_Features.sql Executing migration V4__Add_Task_Audit_Trail.sql Executing migration V5__Performance_Optimization.sql Migration completed successfully ```

**Duration:** 30-45 seconds **Rollback Available:** Yes (use `npm run migrate:rollback`)

### Step 5: Seed Database (Optional)

```bash npm run seed:dev ```

Creates test data: - 10 test users - 50 sample tasks - 150 subtasks - 100 comments

Use only in development environment. Production data must be migrated separately.

### Step 6: Start Services

For development (all services in one terminal):

```bash npm run dev ```

For production (recommended distributed setup):

```bash
# Terminal 1: API Server
npm run start

# Terminal 2: Message Queue Worker
npm run worker:start

# Terminal 3: Notification Service
npm run notifications:start ```

**Service Health Check:**

```bash curl -s http://localhost:3000/health | jq . ```

Expected response: ```json { "status": "healthy", "timestamp": "2026-02-26T10:30:45Z", "services": { "database": "connected", "redis": "connected", "rabbitmq": "connected" } } ```

## Docker Deployment

### Build Image

```bash docker build -t task-mgmt:2.1 . ```

### Docker Compose (Development)

```bash docker-compose -f docker-compose.dev.yml up -d ```

Services launched: API (port 3000), PostgreSQL (5432), Redis (6379), RabbitMQ (5672).

**Configuration:** See `docker-compose.dev.yml` file for detailed service configuration. Updated 2026-02-24.

## Network Configuration

### Firewall Rules

| Port | Service | Direction | Required | |------|---------|-----------|----------| | 3000 | API Server | Inbound | Yes | | 5432 | PostgreSQL | Internal only | Yes | | 6379 | Redis | Internal only | Yes | | 5672 | RabbitMQ | Internal only | Yes | | 15672 | RabbitMQ Admin | Internal only | No |

### CORS Configuration

Allowed origins (configurable in `config/cors.js`): - `http://localhost:3000` (development) - `https://app.example.com` (production)

Add additional origins only after security team review. Last updated: 2026-02-20.

## Verification Steps

After installation completes:

```bash
# 1. Check service availability
npm run health:check

# 2. Run basic smoke tests
npm run test:smoke

# 3. Verify database connectivity
npm run db:validate

# 4. Check API response
curl -s http://localhost:3000/api/v1/tasks -H "Authorization: Bearer YOUR_TOKEN"

# 5. Review logs
npm run logs:tail ```

All checks should pass within 2 minutes of startup.

## Troubleshooting

### Issue: "EADDRINUSE: address already in use :::3000"

**Solution:** Port 3000 already in use. ```bash
# Find and kill process
lsof -i :3000 kill -9 <PID>
# or use different port
PORT=3001 npm run dev ```

### Issue: "connect ECONNREFUSED 127.0.0.1:5432"

**Solution:** PostgreSQL not running or connection string incorrect. ```bash
# Check PostgreSQL status
psql -U postgres -d task_mgmt_db -c "SELECT NOW();"

# If psql not found, install PostgreSQL first
``` **Last Resolved:** 2026-02-19

### Issue: "TimeoutError: connect timeout"

**Solution:** RabbitMQ connection failing. ```bash
# Check RabbitMQ status
curl http://localhost:15672/api/whoami -u guest:guest

# Restart if necessary
docker restart rabbitmq ```

## Performance Baseline (as of 2026-02-26)

After installation on recommended hardware: - API response time: <100ms (p95) - Database query latency: <50ms (p95) - Service startup time: <10 seconds - Memory usage: ~250MB (API process) - CPU utilization: <15% (idle)

## Post-Installation Steps

1. **User Onboarding:** Create first admin user via CLI ```bash npm run user:create:admin --email=admin@example.com ```

2. **Configuration Review:** Verify all critical settings in admin panel

3. **Enable Monitoring:** Set up log aggregation and performance monitoring

4. **Backup Verification:** Test backup and restore procedures on non-production environment

5. **Security Hardening:** Run security scanning tools (completed on 2026-02-23)

## Update Procedure

To update from v2.0 to v2.1:

```bash git pull origin main npm install npm run migrate npm run restart ```

**Estimated Downtime:** <2 minutes with blue-green deployment **Rollback Available:** Yes, use `git checkout v2.0-stable` and `npm run migrate:rollback`

## Support Resources

- Documentation: `/docs` directory - API Reference: `http://localhost:3000/api/docs` - Issue Tracker: GitHub Issues (private repository) - Status Page: `https://status.example.com`