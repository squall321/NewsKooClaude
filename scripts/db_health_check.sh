#!/bin/bash
#
# Database Health Check Script
# Usage: ./db_health_check.sh
#

set -e

DB_CONTAINER="newskoo-postgres-1"
DB_NAME="${POSTGRES_DB:-newskoo}"
DB_USER="${POSTGRES_USER:-newskoo}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Database Health Check ===${NC}\n"

# Check container status
echo -e "${YELLOW}1. Container Status:${NC}"
if docker ps | grep -q "$DB_CONTAINER"; then
    echo -e "${GREEN}✓ Container is running${NC}"
else
    echo -e "${RED}✗ Container is not running${NC}"
    exit 1
fi

# Check connection
echo -e "\n${YELLOW}2. Database Connection:${NC}"
if docker exec "$DB_CONTAINER" pg_isready -U "$DB_USER" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Database is accepting connections${NC}"
else
    echo -e "${RED}✗ Cannot connect to database${NC}"
    exit 1
fi

# Check database size
echo -e "\n${YELLOW}3. Database Size:${NC}"
DB_SIZE=$(docker exec "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT pg_size_pretty(pg_database_size('$DB_NAME'));" | xargs)
echo -e "   Database size: ${GREEN}$DB_SIZE${NC}"

# Check table count
echo -e "\n${YELLOW}4. Table Statistics:${NC}"
TABLE_COUNT=$(docker exec "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public';" | xargs)
echo -e "   Total tables: ${GREEN}$TABLE_COUNT${NC}"

# Check key tables row counts
echo -e "\n${YELLOW}5. Key Table Row Counts:${NC}"
for table in users posts comments categories tags; do
    ROW_COUNT=$(docker exec "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT count(*) FROM $table;" 2>/dev/null | xargs || echo "N/A")
    if [ "$ROW_COUNT" != "N/A" ]; then
        echo -e "   $table: ${GREEN}$ROW_COUNT${NC}"
    else
        echo -e "   $table: ${YELLOW}$ROW_COUNT${NC}"
    fi
done

# Check active connections
echo -e "\n${YELLOW}6. Active Connections:${NC}"
ACTIVE_CONN=$(docker exec "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT count(*) FROM pg_stat_activity WHERE datname = '$DB_NAME';" | xargs)
echo -e "   Active connections: ${GREEN}$ACTIVE_CONN${NC}"

# Check replication lag (if applicable)
echo -e "\n${YELLOW}7. Recent Activity:${NC}"
LAST_STATS=$(docker exec "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT to_char(stats_reset, 'YYYY-MM-DD HH24:MI:SS') FROM pg_stat_database WHERE datname = '$DB_NAME';" | xargs)
echo -e "   Stats reset: ${GREEN}$LAST_STATS${NC}"

# Check for long-running queries
echo -e "\n${YELLOW}8. Long-Running Queries:${NC}"
LONG_QUERIES=$(docker exec "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT count(*) FROM pg_stat_activity WHERE state = 'active' AND now() - query_start > interval '1 minute';" | xargs)
if [ "$LONG_QUERIES" -gt 0 ]; then
    echo -e "   ${YELLOW}⚠ $LONG_QUERIES long-running queries detected${NC}"
else
    echo -e "   ${GREEN}✓ No long-running queries${NC}"
fi

# Check disk usage
echo -e "\n${YELLOW}9. Disk Usage (Container):${NC}"
DISK_USAGE=$(docker exec "$DB_CONTAINER" df -h /var/lib/postgresql/data | tail -1 | awk '{print $5}')
echo -e "   Disk usage: ${GREEN}$DISK_USAGE${NC}"

# Check for bloat (approximate)
echo -e "\n${YELLOW}10. Table Bloat Analysis:${NC}"
BLOAT_QUERY="
SELECT
    schemaname || '.' || tablename AS table,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 5;
"
echo -e "   Top 5 largest tables:"
docker exec "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -c "$BLOAT_QUERY" | while IFS= read -r line; do
    echo -e "   $line"
done

echo -e "\n${BLUE}=== Health Check Complete ===${NC}"
