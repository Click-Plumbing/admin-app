#!/bin/bash

# Create backup directories if they don't exist
mkdir -p backups/db

# Get current timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Backup the application files (excluding virtual environment, instance directory, and other unnecessary files)
tar --exclude='./venv' \
    --exclude='./instance' \
    --exclude='./backups' \
    --exclude='__pycache__' \
    --exclude='.DS_Store' \
    -czf "backups/clickplumbing_backup_${TIMESTAMP}.tar.gz" .

# Backup the database
if [ -f "instance/clickplumbing.db" ]; then
    cp instance/clickplumbing.db "backups/db/clickplumbing_${TIMESTAMP}.db"
    echo "Database backup created: backups/db/clickplumbing_${TIMESTAMP}.db"
else
    echo "Warning: Database file not found"
fi

# Remove backups older than 30 days
find backups -name "clickplumbing_backup_*.tar.gz" -type f -mtime +30 -delete
find backups/db -name "clickplumbing_*.db" -type f -mtime +30 -delete

echo "Backup completed: backups/clickplumbing_backup_${TIMESTAMP}.tar.gz"
