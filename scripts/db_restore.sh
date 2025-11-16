#!/bin/bash
#
# Database Restore Script
# Usage: ./db_restore.sh <backup_file>
#

set -e

# Check arguments
if [ $# -eq 0 ]; then
    echo "Usage: $0 <backup_file>"
    echo "Example: $0 /path/to/db_backup_20250116_120000.sql.gz"
    exit 1
fi

BACKUP_FILE="$1"
DB_CONTAINER="newskoo-postgres-1"
DB_NAME="${POSTGRES_DB:-newskoo}"
DB_USER="${POSTGRES_USER:-newskoo}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    echo -e "${RED}Error: Backup file not found: $BACKUP_FILE${NC}"
    exit 1
fi

# Check if container is running
if ! docker ps | grep -q "$DB_CONTAINER"; then
    echo -e "${RED}Error: Database container is not running${NC}"
    exit 1
fi

# Confirm restore
echo -e "${YELLOW}WARNING: This will REPLACE the current database!${NC}"
echo -e "${YELLOW}Database: $DB_NAME${NC}"
echo -e "${YELLOW}Backup file: $BACKUP_FILE${NC}"
read -p "Are you sure you want to continue? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo -e "${RED}Restore cancelled${NC}"
    exit 0
fi

# Create safety backup before restore
echo -e "${YELLOW}Creating safety backup of current database...${NC}"
SAFETY_BACKUP="/tmp/safety_backup_$(date +%Y%m%d_%H%M%S).sql"
docker exec -t "$DB_CONTAINER" pg_dump -U "$DB_USER" -d "$DB_NAME" > "$SAFETY_BACKUP"
echo -e "${GREEN}Safety backup created: $SAFETY_BACKUP${NC}"

# Decompress if needed
if [[ "$BACKUP_FILE" == *.gz ]]; then
    echo -e "${YELLOW}Decompressing backup...${NC}"
    TMP_FILE="/tmp/restore_$(date +%Y%m%d_%H%M%S).sql"
    gunzip -c "$BACKUP_FILE" > "$TMP_FILE"
    RESTORE_FILE="$TMP_FILE"
else
    RESTORE_FILE="$BACKUP_FILE"
fi

# Restore database
echo -e "${YELLOW}Restoring database...${NC}"
cat "$RESTORE_FILE" | docker exec -i "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}Database restored successfully!${NC}"
    echo -e "${GREEN}Safety backup kept at: $SAFETY_BACKUP${NC}"

    # Clean up temp file
    if [ -n "$TMP_FILE" ] && [ -f "$TMP_FILE" ]; then
        rm "$TMP_FILE"
    fi
else
    echo -e "${RED}Restore failed!${NC}"
    echo -e "${YELLOW}You can restore from safety backup:${NC}"
    echo -e "${YELLOW}  cat $SAFETY_BACKUP | docker exec -i $DB_CONTAINER psql -U $DB_USER -d $DB_NAME${NC}"
    exit 1
fi
