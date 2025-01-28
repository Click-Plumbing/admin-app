# Click Plumbing Admin Portal

A comprehensive web application for managing plumbing machines, parts, and user access.

## Features

1. Machine and Part Maintenance Tracking
   - Machine management with customer details and location
   - Parts tracking with QR code support
   - Warranty tracking

2. Health Monitoring
   - Real-time machine operational data
   - Sensor data tracking (flow, pressure, temperature)

3. User Management
   - Role-based access control (Admin, Engineer, Account Manager)
   - Machine assignment capabilities

4. Audit Logging
   - Comprehensive action tracking

## Quick Start

The easiest way to start the application is to use the launcher script:

```bash
python launcher.py
```

This will automatically:
1. Create a virtual environment if it doesn't exist
2. Install all required dependencies
3. Initialize the database
4. Start the Flask application

The launcher provides a user-friendly interface with status updates and handles all the setup steps automatically.

## Manual Setup

If you prefer to set up the application manually, follow these steps:

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   ```

4. Initialize the database:
   ```bash
   flask db upgrade
   ```

5. Run the application:
   ```bash
   flask run
   ```

## Backups

The application includes an automated backup system:

### Manual Backup
To create a backup manually, run:
```bash
./backup.sh
```

This will:
1. Create a compressed backup of all application files in `backups/clickplumbing_backup_[TIMESTAMP].tar.gz`
2. Create a copy of the database in `backups/db/clickplumbing_[TIMESTAMP].db`
3. Automatically remove backups older than 30 days

### Automated Backups
To set up automated daily backups, add the following to your crontab:
```bash
0 0 * * * cd /path/to/click/plumbing/qr/code && ./backup.sh
```

### Restoring from Backup
To restore from a backup:
1. Extract the application files:
   ```bash
   tar -xzf backups/clickplumbing_backup_[TIMESTAMP].tar.gz -C /path/to/restore
   ```
2. Copy the database file:
   ```bash
   cp backups/db/clickplumbing_[TIMESTAMP].db instance/clickplumbing.db
   ```

## Default Admin Credentials

- Email: admin@admin.com
- Password: admin123

**Important**: Change these credentials immediately after first login.

## Security Notice

This is an administrative portal. Please ensure:
1. Strong passwords are used
2. Regular security audits are performed
3. Access is restricted to authorized personnel only
