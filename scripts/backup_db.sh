#!/bin/bash
# PostgreSQL backup script for MasterBot Platform
# Creates compressed backup and removes backups older than 7 days
#
# Usage: ./scripts/backup_db.sh
#
# Setup cron job (daily at 3:00 AM):
# crontab -e
# 0 3 * * * cd /path/to/masterbot-platform && ./scripts/backup_db.sh >> /var/log/masterbot_backup.log 2>&1

set -e

# Configuration
BACKUP_DIR="${BACKUP_DIR:-./backups}"
DAYS_TO_KEEP="${DAYS_TO_KEEP:-7}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Create backup directory if not exists
mkdir -p "$BACKUP_DIR"

BACKUP_FILE="${BACKUP_DIR}/masterbot_${TIMESTAMP}.sql.gz"

echo "$(date): Starting database backup..."

# Create backup using pg_dump inside postgres container
docker compose exec -T postgres pg_dump \
    -U "${DB_USER}" \
    -d "${DB_NAME}" \
    --no-owner \
    --no-acl \
    | gzip > "$BACKUP_FILE"

# Check if backup was created successfully
if [ -f "$BACKUP_FILE" ] && [ -s "$BACKUP_FILE" ]; then
    SIZE=$(ls -lh "$BACKUP_FILE" | awk '{print $5}')
    echo "$(date): Backup created successfully: $BACKUP_FILE ($SIZE)"
else
    echo "$(date): ERROR - Backup failed!"
    exit 1
fi

# Remove old backups
echo "$(date): Removing backups older than $DAYS_TO_KEEP days..."
find "$BACKUP_DIR" -name "masterbot_*.sql.gz" -type f -mtime +$DAYS_TO_KEEP -delete

# Count remaining backups
BACKUP_COUNT=$(ls -1 "$BACKUP_DIR"/masterbot_*.sql.gz 2>/dev/null | wc -l)
echo "$(date): Backup complete. Total backups: $BACKUP_COUNT"
