#!/bin/bash
#
# Database Migration Script
# Usage: ./db_migrate.sh [action]
# Actions: status, upgrade, downgrade, init
#

set -e

ACTION="${1:-status}"
BACKEND_CONTAINER="newskoo-backend-1"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Database Migration Manager ===${NC}\n"

# Check if backend container is running
if ! docker ps | grep -q "$BACKEND_CONTAINER"; then
    echo -e "${RED}Error: Backend container is not running${NC}"
    exit 1
fi

case "$ACTION" in
    status)
        echo -e "${YELLOW}Migration Status:${NC}"
        docker exec "$BACKEND_CONTAINER" flask db current
        echo -e "\n${YELLOW}Migration History:${NC}"
        docker exec "$BACKEND_CONTAINER" flask db history
        ;;

    upgrade)
        echo -e "${YELLOW}Upgrading database to latest migration...${NC}"
        docker exec "$BACKEND_CONTAINER" flask db upgrade
        echo -e "${GREEN}✓ Database upgraded successfully${NC}"
        ;;

    downgrade)
        if [ -z "$2" ]; then
            echo -e "${RED}Error: Downgrade requires a revision argument${NC}"
            echo -e "${YELLOW}Usage: $0 downgrade <revision>${NC}"
            echo -e "${YELLOW}Example: $0 downgrade -1${NC}"
            exit 1
        fi

        REVISION="$2"
        echo -e "${YELLOW}WARNING: Downgrading database to revision: $REVISION${NC}"
        read -p "Are you sure? (yes/no): " CONFIRM

        if [ "$CONFIRM" != "yes" ]; then
            echo -e "${RED}Downgrade cancelled${NC}"
            exit 0
        fi

        docker exec "$BACKEND_CONTAINER" flask db downgrade "$REVISION"
        echo -e "${GREEN}✓ Database downgraded successfully${NC}"
        ;;

    init)
        echo -e "${YELLOW}Initializing migration repository...${NC}"
        docker exec "$BACKEND_CONTAINER" flask db init
        echo -e "${GREEN}✓ Migration repository initialized${NC}"
        ;;

    create)
        if [ -z "$2" ]; then
            echo -e "${RED}Error: Create requires a message argument${NC}"
            echo -e "${YELLOW}Usage: $0 create <message>${NC}"
            echo -e "${YELLOW}Example: $0 create 'add user preferences table'${NC}"
            exit 1
        fi

        MESSAGE="$2"
        echo -e "${YELLOW}Creating new migration: $MESSAGE${NC}"
        docker exec "$BACKEND_CONTAINER" flask db migrate -m "$MESSAGE"
        echo -e "${GREEN}✓ Migration created successfully${NC}"
        echo -e "${YELLOW}Don't forget to review the generated migration file!${NC}"
        ;;

    *)
        echo -e "${RED}Unknown action: $ACTION${NC}"
        echo -e "${YELLOW}Available actions:${NC}"
        echo -e "  status     - Show current migration status"
        echo -e "  upgrade    - Upgrade to latest migration"
        echo -e "  downgrade  - Downgrade to specific revision"
        echo -e "  init       - Initialize migration repository"
        echo -e "  create     - Create new migration"
        exit 1
        ;;
esac
