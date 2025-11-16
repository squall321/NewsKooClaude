# Database Operations Guide

## Overview

This guide covers all database operations for NewsKoo, including backups, restores, migrations, health checks, and optimization.

## Table of Contents

1. [Database Backup](#database-backup)
2. [Database Restore](#database-restore)
3. [Health Checks](#health-checks)
4. [Migrations](#migrations)
5. [Optimization](#optimization)
6. [Automated Backups](#automated-backups)
7. [Monitoring](#monitoring)
8. [Troubleshooting](#troubleshooting)

---

## Database Backup

### Manual Backup

```bash
# Basic backup (saves to /home/deploy/backups/db by default)
./scripts/db_backup.sh

# Backup to custom directory
./scripts/db_backup.sh /path/to/backup/directory
```

**Features:**
- Automatic compression (gzip)
- Timestamp naming: `db_backup_YYYYMMDD_HHMMSS.sql.gz`
- Automatic cleanup of backups older than 30 days
- Shows backup size and recent backups

**Output Example:**
```
Starting database backup...
Creating backup: /home/deploy/backups/db/db_backup_20250116_120000.sql
Compressing backup...
✓ Backup completed successfully!
File: /home/deploy/backups/db/db_backup_20250116_120000.sql.gz
Size: 24M
```

### Backup Retention Policy

- **Daily backups**: Kept for 30 days
- **Weekly backups**: Manual weekly backups recommended for long-term storage
- **Pre-deployment backups**: Always create before major updates

### Backup Best Practices

1. **Before deployments**: Always backup before deploying
2. **Before migrations**: Backup before running database migrations
3. **Regular schedule**: Set up automated daily backups (see below)
4. **Off-site storage**: Copy critical backups to external storage (S3, Google Cloud Storage)
5. **Test restores**: Regularly test restore procedures

---

## Database Restore

### Restore from Backup

```bash
# Restore from backup file
./scripts/db_restore.sh /path/to/db_backup_20250116_120000.sql.gz
```

**Safety Features:**
- Confirmation prompt before restore
- Creates safety backup of current database before restore
- Supports both compressed (.gz) and uncompressed (.sql) files
- Keeps safety backup for manual recovery if restore fails

**Example:**
```bash
$ ./scripts/db_restore.sh /home/deploy/backups/db/db_backup_20250115_020000.sql.gz

WARNING: This will REPLACE the current database!
Database: newskoo
Backup file: /home/deploy/backups/db/db_backup_20250115_020000.sql.gz
Are you sure you want to continue? (yes/no): yes

Creating safety backup of current database...
✓ Safety backup created: /tmp/safety_backup_20250116_123045.sql
Decompressing backup...
Restoring database...
✓ Database restored successfully!
✓ Safety backup kept at: /tmp/safety_backup_20250116_123045.sql
```

### Emergency Restore

If restore fails, you can recover from the safety backup:

```bash
cat /tmp/safety_backup_YYYYMMDD_HHMMSS.sql | \
  docker exec -i newskoo-postgres-1 psql -U newskoo -d newskoo
```

---

## Health Checks

### Run Health Check

```bash
./scripts/db_health_check.sh
```

**Checks Performed:**
1. ✓ Container status
2. ✓ Database connectivity
3. ✓ Database size
4. ✓ Table statistics
5. ✓ Row counts for key tables
6. ✓ Active connections
7. ✓ Recent activity
8. ✓ Long-running queries
9. ✓ Disk usage
10. ✓ Table bloat analysis

**Output Example:**
```
=== Database Health Check ===

1. Container Status:
✓ Container is running

2. Database Connection:
✓ Database is accepting connections

3. Database Size:
   Database size: 125 MB

4. Table Statistics:
   Total tables: 12

5. Key Table Row Counts:
   users: 1,234
   posts: 5,678
   comments: 12,345
   categories: 15
   tags: 45

6. Active Connections:
   Active connections: 3

7. Recent Activity:
   Stats reset: 2025-11-15 02:00:00

8. Long-Running Queries:
   ✓ No long-running queries

9. Disk Usage (Container):
   Disk usage: 45%

10. Table Bloat Analysis:
   Top 5 largest tables:
   [table listing...]

=== Health Check Complete ===
```

### Automated Health Checks

Add to crontab for daily health checks:

```bash
# Daily health check at 9 AM, save to log
0 9 * * * /home/deploy/NewsKooClaude/scripts/db_health_check.sh >> /home/deploy/logs/db_health.log 2>&1
```

---

## Migrations

### Migration Management

```bash
# Check current migration status
./scripts/db_migrate.sh status

# Upgrade to latest migration
./scripts/db_migrate.sh upgrade

# Create new migration
./scripts/db_migrate.sh create "add user preferences table"

# Downgrade to previous version
./scripts/db_migrate.sh downgrade -1

# Initialize migration repository (first time only)
./scripts/db_migrate.sh init
```

### Migration Workflow

**1. Create Migration:**
```bash
# Make model changes in backend/app/models/*.py
# Then generate migration
./scripts/db_migrate.sh create "descriptive message"
```

**2. Review Migration:**
```bash
# Review the generated migration file in backend/migrations/versions/
# Edit if necessary
```

**3. Test Migration:**
```bash
# Test in development first
./scripts/db_migrate.sh upgrade

# Check database
./scripts/db_health_check.sh
```

**4. Deploy Migration:**
```bash
# Backup before migration
./scripts/db_backup.sh

# Run migration
./scripts/db_migrate.sh upgrade
```

### Migration Best Practices

1. **Always backup** before running migrations
2. **Review generated migrations** - auto-generated migrations may need manual adjustments
3. **Test in development** before production
4. **One change per migration** - keep migrations focused
5. **Descriptive messages** - use clear migration names
6. **Reversible migrations** - ensure downgrade functions work

---

## Optimization

### Database Optimization

```bash
# Run all optimizations
./scripts/db_optimize.sh all

# Run specific optimization
./scripts/db_optimize.sh vacuum   # Reclaim storage
./scripts/db_optimize.sh analyze  # Update statistics
./scripts/db_optimize.sh reindex  # Rebuild indexes
```

**When to Optimize:**

- **VACUUM**: After large DELETE/UPDATE operations
- **ANALYZE**: After significant data changes, before important queries
- **REINDEX**: When index bloat is detected, query performance degrades
- **All**: Weekly maintenance window

### Performance Tuning

**PostgreSQL Configuration** (via docker-compose.yml):

```yaml
postgres:
  command:
    - "postgres"
    - "-c"
    - "shared_buffers=256MB"
    - "-c"
    - "effective_cache_size=1GB"
    - "-c"
    - "maintenance_work_mem=128MB"
    - "-c"
    - "max_connections=100"
```

**Index Optimization:**

```sql
-- Check missing indexes
SELECT schemaname, tablename, attname, n_distinct, correlation
FROM pg_stats
WHERE schemaname = 'public'
  AND n_distinct > 100
ORDER BY abs(correlation) DESC;

-- Check unused indexes
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0
  AND indexname NOT LIKE 'pg_toast%';
```

---

## Automated Backups

### Cron Setup

Add to deploy user's crontab:

```bash
# Edit crontab
crontab -e

# Add backup schedule
# Daily backup at 2 AM
0 2 * * * /home/deploy/NewsKooClaude/scripts/db_backup.sh >> /home/deploy/logs/backup.log 2>&1

# Weekly optimization on Sunday 3 AM
0 3 * * 0 /home/deploy/NewsKooClaude/scripts/db_optimize.sh all >> /home/deploy/logs/optimize.log 2>&1

# Daily health check at 9 AM
0 9 * * * /home/deploy/NewsKooClaude/scripts/db_health_check.sh >> /home/deploy/logs/health.log 2>&1
```

### Backup to Cloud Storage

**AWS S3 Backup:**

```bash
#!/bin/bash
# /home/deploy/scripts/backup_to_s3.sh

BACKUP_DIR="/home/deploy/backups/db"
LATEST_BACKUP=$(ls -t $BACKUP_DIR/db_backup_*.sql.gz | head -1)

# Upload to S3
aws s3 cp "$LATEST_BACKUP" s3://your-bucket/backups/db/

# Keep only last 90 days in S3
aws s3 ls s3://your-bucket/backups/db/ | \
  awk '{print $4}' | \
  while read file; do
    # Delete files older than 90 days
    # ... (implement date comparison)
  done
```

**Google Cloud Storage:**

```bash
gsutil cp "$LATEST_BACKUP" gs://your-bucket/backups/db/
```

---

## Monitoring

### Key Metrics to Monitor

**1. Database Size Growth:**
```sql
SELECT pg_size_pretty(pg_database_size('newskoo'));
```

**2. Table Sizes:**
```sql
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

**3. Connection Count:**
```sql
SELECT count(*) FROM pg_stat_activity WHERE datname = 'newskoo';
```

**4. Query Performance:**
```sql
SELECT query, calls, mean_exec_time, total_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
```

**5. Cache Hit Ratio:**
```sql
SELECT
    sum(heap_blks_read) as heap_read,
    sum(heap_blks_hit) as heap_hit,
    sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read)) as ratio
FROM pg_statio_user_tables;
```

### Monitoring Tools

**1. pg_stat_statements (Query Performance):**
```sql
-- Enable in postgresql.conf
shared_preload_libraries = 'pg_stat_statements'
```

**2. pgAdmin (Web UI):**
```bash
docker run -d \
  -p 5050:80 \
  -e PGADMIN_DEFAULT_EMAIL=admin@newskoo.com \
  -e PGADMIN_DEFAULT_PASSWORD=admin \
  dpage/pgadmin4
```

**3. Prometheus + Grafana (Production):**
```yaml
# Add postgres_exporter to docker-compose.yml
postgres-exporter:
  image: prometheuscommunity/postgres-exporter
  environment:
    DATA_SOURCE_NAME: "postgresql://newskoo:password@postgres:5432/newskoo?sslmode=disable"
  ports:
    - "9187:9187"
```

---

## Troubleshooting

### Common Issues

**1. Database Won't Start:**
```bash
# Check logs
docker logs newskoo-postgres-1

# Check disk space
df -h

# Check data directory permissions
docker exec newskoo-postgres-1 ls -la /var/lib/postgresql/data
```

**2. Connection Refused:**
```bash
# Check container is running
docker ps | grep postgres

# Check port is exposed
docker port newskoo-postgres-1

# Test connection
docker exec newskoo-postgres-1 psql -U newskoo -c "SELECT 1"
```

**3. Slow Queries:**
```sql
-- Find slow queries
SELECT pid, query_start, state, query
FROM pg_stat_activity
WHERE state = 'active'
  AND now() - query_start > interval '1 minute';

-- Kill slow query
SELECT pg_terminate_backend(pid);
```

**4. Lock Conflicts:**
```sql
-- Find locks
SELECT
    pid,
    usename,
    pg_blocking_pids(pid) as blocked_by,
    query
FROM pg_stat_activity
WHERE cardinality(pg_blocking_pids(pid)) > 0;
```

**5. Out of Disk Space:**
```bash
# Check database size
./scripts/db_health_check.sh

# Run VACUUM to reclaim space
./scripts/db_optimize.sh vacuum

# Clean old backups
find /home/deploy/backups -type f -mtime +30 -delete

# Clean Docker volumes
docker system prune -a --volumes
```

**6. Corruption:**
```bash
# Check for corruption
docker exec newskoo-postgres-1 psql -U newskoo -d newskoo -c "
    SELECT * FROM pg_catalog.pg_database WHERE datname = 'newskoo';
"

# REINDEX if needed
./scripts/db_optimize.sh reindex

# If severe, restore from backup
./scripts/db_restore.sh /path/to/good_backup.sql.gz
```

### Emergency Procedures

**Complete Database Failure:**

1. **Stop all services:**
   ```bash
   docker compose down
   ```

2. **Restore from backup:**
   ```bash
   docker compose up -d postgres
   ./scripts/db_restore.sh /path/to/latest_backup.sql.gz
   ```

3. **Start services:**
   ```bash
   docker compose up -d
   ```

4. **Verify:**
   ```bash
   ./scripts/db_health_check.sh
   ```

**Data Corruption:**

1. **Immediate backup:**
   ```bash
   ./scripts/db_backup.sh /home/deploy/backups/corrupted
   ```

2. **Try REINDEX:**
   ```bash
   ./scripts/db_optimize.sh reindex
   ```

3. **If fails, restore from last good backup**

---

## Additional Resources

- [PostgreSQL Official Documentation](https://www.postgresql.org/docs/)
- [PostgreSQL Performance Tuning](https://wiki.postgresql.org/wiki/Performance_Optimization)
- [Backup and Restore Best Practices](https://www.postgresql.org/docs/current/backup.html)
- [pgAdmin Documentation](https://www.pgadmin.org/docs/)

---

## Quick Reference

```bash
# Backup
./scripts/db_backup.sh

# Restore
./scripts/db_restore.sh <backup_file>

# Health Check
./scripts/db_health_check.sh

# Migrations
./scripts/db_migrate.sh status
./scripts/db_migrate.sh upgrade

# Optimize
./scripts/db_optimize.sh all
```
