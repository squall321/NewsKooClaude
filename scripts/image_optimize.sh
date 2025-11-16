#!/bin/bash
#
# Batch Image Optimization Script
# Usage: ./image_optimize.sh [directory]
#

set -e

# Configuration
TARGET_DIR="${1:-/home/deploy/NewsKooClaude/backend/uploads}"
JPEG_QUALITY=85
PNG_COMPRESSION=9

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Image Optimization Tool ===${NC}\n"

# Check if directory exists
if [ ! -d "$TARGET_DIR" ]; then
    echo -e "${RED}Error: Directory not found: $TARGET_DIR${NC}"
    exit 1
fi

# Check if optimization tools are installed
command -v jpegoptim >/dev/null 2>&1 || {
    echo -e "${YELLOW}jpegoptim not found. Installing...${NC}"
    apt-get update && apt-get install -y jpegoptim
}

command -v optipng >/dev/null 2>&1 || {
    echo -e "${YELLOW}optipng not found. Installing...${NC}"
    apt-get update && apt-get install -y optipng
}

# Calculate initial size
INITIAL_SIZE=$(du -sh "$TARGET_DIR" | cut -f1)
echo -e "${YELLOW}Initial directory size: $INITIAL_SIZE${NC}\n"

# Count files
JPEG_COUNT=$(find "$TARGET_DIR" -type f \( -iname "*.jpg" -o -iname "*.jpeg" \) | wc -l)
PNG_COUNT=$(find "$TARGET_DIR" -type f -iname "*.png" | wc -l)

echo -e "${YELLOW}Files to optimize:${NC}"
echo -e "  JPEG: $JPEG_COUNT"
echo -e "  PNG: $PNG_COUNT"
echo ""

# Optimize JPEGs
if [ $JPEG_COUNT -gt 0 ]; then
    echo -e "${YELLOW}Optimizing JPEG files...${NC}"
    find "$TARGET_DIR" -type f \( -iname "*.jpg" -o -iname "*.jpeg" \) -exec jpegoptim --max=$JPEG_QUALITY --strip-all {} \;
    echo -e "${GREEN}✓ JPEG optimization complete${NC}\n"
fi

# Optimize PNGs
if [ $PNG_COUNT -gt 0 ]; then
    echo -e "${YELLOW}Optimizing PNG files...${NC}"
    find "$TARGET_DIR" -type f -iname "*.png" -exec optipng -o$PNG_COMPRESSION -strip all {} \;
    echo -e "${GREEN}✓ PNG optimization complete${NC}\n"
fi

# Calculate final size
FINAL_SIZE=$(du -sh "$TARGET_DIR" | cut -f1)
echo -e "${YELLOW}Final directory size: $FINAL_SIZE${NC}"

# Calculate savings
INITIAL_BYTES=$(du -sb "$TARGET_DIR" | cut -f1)
# This is approximate since we already optimized
echo -e "${GREEN}Optimization complete!${NC}"
echo -e "${GREEN}Run this script before your initial backup to save space.${NC}"
