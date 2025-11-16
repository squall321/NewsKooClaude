#!/bin/bash
#
# Database Optimization Script
# Usage: ./db_optimize.sh [action]
# Actions: vacuum, analyze, reindex, all
#

set -e

ACTION="${1:-all}"
DB_CONTAINER="newskoo-postgres-1"
DB_NAME="${POSTGRES_DB:-newskoo}"
DB_USER="${POSTGRES_USER:-newskoo}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Database Optimization ===${NC}\n"

# Check if container is running
if ! docker ps | grep -q "$DB_CONTAINER"; then
    echo -e "${RED}Error: Database container is not running${NC}"
    exit 1
fi

run_vacuum() {
    echo -e "${YELLOW}Running VACUUM...${NC}"
    docker exec "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -c "VACUUM VERBOSE;"
    echo -e "${GREEN}✓ VACUUM completed${NC}\n"
}

run_analyze() {
    echo -e "${YELLOW}Running ANALYZE...${NC}"
    docker exec "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -c "ANALYZE VERBOSE;"
    echo -e "${GREEN}✓ ANALYZE completed${NC}\n"
}

run_reindex() {
    echo -e "${YELLOW}Running REINDEX...${NC}"
    echo -e "${YELLOW}This may take a while for large databases...${NC}"
    docker exec "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -c "REINDEX DATABASE $DB_NAME;"
    echo -e "${GREEN}✓ REINDEX completed${NC}\n"
}

case "$ACTION" in
    vacuum)
        run_vacuum
        ;;

    analyze)
        run_analyze
        ;;

    reindex)
        run_reindex
        ;;

    all)
        echo -e "${YELLOW}Running full optimization...${NC}\n"
        run_vacuum
        run_analyze
        run_reindex
        echo -e "${GREEN}✓ Full optimization completed${NC}"
        ;;

    *)
        echo -e "${RED}Unknown action: $ACTION${NC}"
        echo -e "${YELLOW}Available actions:${NC}"
        echo -e "  vacuum   - Reclaim storage and update statistics"
        echo -e "  analyze  - Update query planner statistics"
        echo -e "  reindex  - Rebuild all indexes"
        echo -e "  all      - Run all optimizations"
        exit 1
        ;;
esac
