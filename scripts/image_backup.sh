#!/bin/bash
#
# Image Storage Backup Script
# Usage: ./image_backup.sh [backup_dir]
#

set -e

# Configuration
BACKUP_DIR="${1:-/home/deploy/backups/images}"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=90
UPLOAD_DIR="/home/deploy/NewsKooClaude/backend/uploads"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Starting image storage backup...${NC}"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Check if upload directory exists
if [ ! -d "$UPLOAD_DIR" ]; then
    echo -e "${RED}Error: Upload directory not found: $UPLOAD_DIR${NC}"
    exit 1
fi

# Calculate current size
CURRENT_SIZE=$(du -sh "$UPLOAD_DIR" | cut -f1)
echo -e "${YELLOW}Current upload directory size: $CURRENT_SIZE${NC}"

# Create backup
BACKUP_FILE="$BACKUP_DIR/images_backup_${DATE}.tar.gz"
echo -e "${YELLOW}Creating backup: $BACKUP_FILE${NC}"

tar -czf "$BACKUP_FILE" -C "$(dirname $UPLOAD_DIR)" "$(basename $UPLOAD_DIR)"

if [ $? -eq 0 ]; then
    # Calculate backup size
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)

    echo -e "${GREEN}Backup completed successfully!${NC}"
    echo -e "${GREEN}File: $BACKUP_FILE${NC}"
    echo -e "${GREEN}Size: $BACKUP_SIZE${NC}"

    # Clean old backups
    echo -e "${YELLOW}Cleaning backups older than $RETENTION_DAYS days...${NC}"
    find "$BACKUP_DIR" -name "images_backup_*.tar.gz" -mtime +$RETENTION_DAYS -delete

    # List recent backups
    echo -e "${YELLOW}Recent backups:${NC}"
    ls -lh "$BACKUP_DIR" | tail -5

    # Optional: Upload to S3/R2
    if [ -n "$S3_BUCKET" ]; then
        echo -e "${YELLOW}Uploading to S3...${NC}"
        aws s3 cp "$BACKUP_FILE" "s3://$S3_BUCKET/backups/images/" || echo -e "${YELLOW}S3 upload failed (continuing)${NC}"
    fi

else
    echo -e "${RED}Backup failed!${NC}"
    exit 1
fi
