#!/bin/bash
# PostgreSQL restore script for MasterBot Platform
# Restores database from a backup file
#
# Usage: ./scripts/restore_db.sh backups/masterbot_20250204_030000.sql.gz

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <backup_file.sql.gz>"
    echo ""
    echo "Available backups:"
    ls -lh backups/masterbot_*.sql.gz 2>/dev/null || echo "No backups found in ./backups/"
    exit 1
fi

BACKUP_FILE="$1"

if [ ! -f "$BACKUP_FILE" ]; then
    echo "ERROR: Backup file not found: $BACKUP_FILE"
    exit 1
fi

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

echo "WARNING: This will replace all data in database '${DB_NAME}'!"
echo "Backup file: $BACKUP_FILE"
echo ""
read -p "Are you sure? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Restore cancelled."
    exit 0
fi

echo "$(date): Stopping services that use the database..."
docker compose stop master_bot impulse_service bablo_service miniapp_gateway || true

echo "$(date): Restoring database from $BACKUP_FILE..."

# Decompress and restore
gunzip -c "$BACKUP_FILE" | docker compose exec -T postgres psql \
    -U "${DB_USER}" \
    -d "${DB_NAME}" \
    --quiet

echo "$(date): Database restored successfully!"

echo "$(date): Starting services..."
docker compose up -d master_bot impulse_service bablo_service miniapp_gateway

echo "$(date): Restore complete!"
