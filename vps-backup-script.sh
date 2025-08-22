#!/bin/bash

# VPS Complete Backup Script
# This script creates a comprehensive backup of your VPS server

set -e  # Exit on any error

# Configuration
BACKUP_DATE=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="/tmp/vps_backup_${BACKUP_DATE}"
BACKUP_ARCHIVE="/tmp/vps_complete_backup_${BACKUP_DATE}.tar.gz"
LOG_FILE="/tmp/backup_${BACKUP_DATE}.log"

echo "Starting VPS backup at $(date)" | tee -a "$LOG_FILE"
echo "Backup directory: $BACKUP_DIR" | tee -a "$LOG_FILE"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Function to log messages
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_message "Creating backup directory structure..."

# 1. Backup home directories (including root)
log_message "Backing up home directories..."
mkdir -p "$BACKUP_DIR/home_backup"
if [ -d "/home" ]; then
    cp -rp /home/* "$BACKUP_DIR/home_backup/" 2>/dev/null || true
fi
cp -rp /root "$BACKUP_DIR/root_backup" 2>/dev/null || true

# 2. Backup web applications and important directories
log_message "Backing up web applications..."
mkdir -p "$BACKUP_DIR/applications"
# Common web directories
for dir in /var/www /opt /srv; do
    if [ -d "$dir" ]; then
        cp -rp "$dir" "$BACKUP_DIR/applications/" 2>/dev/null || true
    fi
done

# 3. Backup system configuration
log_message "Backing up system configuration..."
mkdir -p "$BACKUP_DIR/system_config"
cp -rp /etc "$BACKUP_DIR/system_config/" 2>/dev/null || true

# 4. Backup installed packages list
log_message "Creating installed packages list..."
mkdir -p "$BACKUP_DIR/system_info"

# For Ubuntu/Debian systems
if command -v dpkg &> /dev/null; then
    dpkg --get-selections > "$BACKUP_DIR/system_info/installed_packages_dpkg.txt"
    apt list --installed > "$BACKUP_DIR/system_info/installed_packages_apt.txt" 2>/dev/null || true
fi

# For RedHat/CentOS systems
if command -v rpm &> /dev/null; then
    rpm -qa > "$BACKUP_DIR/system_info/installed_packages_rpm.txt"
fi

if command -v yum &> /dev/null; then
    yum list installed > "$BACKUP_DIR/system_info/installed_packages_yum.txt" 2>/dev/null || true
fi

# 5. Backup systemd services
log_message "Backing up systemd services..."
systemctl list-unit-files > "$BACKUP_DIR/system_info/systemd_services.txt" 2>/dev/null || true
systemctl list-units --state=running > "$BACKUP_DIR/system_info/running_services.txt" 2>/dev/null || true

# 6. Backup crontabs
log_message "Backing up crontabs..."
mkdir -p "$BACKUP_DIR/crontabs"
for user in $(cut -f1 -d: /etc/passwd); do
    crontab -u "$user" -l > "$BACKUP_DIR/crontabs/crontab_$user.txt" 2>/dev/null || true
done
cp -rp /etc/cron* "$BACKUP_DIR/crontabs/" 2>/dev/null || true

# 7. Backup databases (if any)
log_message "Backing up databases..."
mkdir -p "$BACKUP_DIR/databases"

# MySQL/MariaDB backup
if command -v mysqldump &> /dev/null && systemctl is-active mysql &> /dev/null; then
    log_message "Found MySQL/MariaDB, creating backup..."
    mysqldump --all-databases --single-transaction --routines --triggers > "$BACKUP_DIR/databases/mysql_all_databases.sql" 2>/dev/null || true
fi

# PostgreSQL backup
if command -v pg_dumpall &> /dev/null && systemctl is-active postgresql &> /dev/null; then
    log_message "Found PostgreSQL, creating backup..."
    sudo -u postgres pg_dumpall > "$BACKUP_DIR/databases/postgresql_all_databases.sql" 2>/dev/null || true
fi

# 8. Backup nginx/apache configuration
log_message "Backing up web server configurations..."
mkdir -p "$BACKUP_DIR/webserver"
if [ -d "/etc/nginx" ]; then
    cp -rp /etc/nginx "$BACKUP_DIR/webserver/" 2>/dev/null || true
fi
if [ -d "/etc/apache2" ]; then
    cp -rp /etc/apache2 "$BACKUP_DIR/webserver/" 2>/dev/null || true
fi

# 9. Backup SSL certificates
log_message "Backing up SSL certificates..."
mkdir -p "$BACKUP_DIR/ssl"
if [ -d "/etc/letsencrypt" ]; then
    cp -rp /etc/letsencrypt "$BACKUP_DIR/ssl/" 2>/dev/null || true
fi
if [ -d "/etc/ssl" ]; then
    cp -rp /etc/ssl "$BACKUP_DIR/ssl/" 2>/dev/null || true
fi

# 10. System information
log_message "Collecting system information..."
uname -a > "$BACKUP_DIR/system_info/system_info.txt"
df -h > "$BACKUP_DIR/system_info/disk_usage.txt"
free -h > "$BACKUP_DIR/system_info/memory_info.txt"
lscpu > "$BACKUP_DIR/system_info/cpu_info.txt"
netstat -tuln > "$BACKUP_DIR/system_info/network_ports.txt" 2>/dev/null || ss -tuln > "$BACKUP_DIR/system_info/network_ports.txt"
iptables -L > "$BACKUP_DIR/system_info/iptables_rules.txt" 2>/dev/null || true

# 11. Backup logs (recent ones)
log_message "Backing up recent logs..."
mkdir -p "$BACKUP_DIR/logs"
find /var/log -name "*.log" -mtime -7 -exec cp {} "$BACKUP_DIR/logs/" \; 2>/dev/null || true

# 12. Create backup manifest
log_message "Creating backup manifest..."
find "$BACKUP_DIR" -type f -exec ls -la {} \; > "$BACKUP_DIR/backup_manifest.txt"
echo "Backup created on: $(date)" >> "$BACKUP_DIR/backup_info.txt"
echo "Server hostname: $(hostname)" >> "$BACKUP_DIR/backup_info.txt"
echo "Server IP: $(hostname -I)" >> "$BACKUP_DIR/backup_info.txt"

# 13. Create compressed archive
log_message "Creating compressed archive..."
cd /tmp
tar -czf "$BACKUP_ARCHIVE" "$(basename "$BACKUP_DIR")" --exclude='*.sock' --exclude='proc/*' --exclude='sys/*' --exclude='dev/*'

# 14. Calculate archive size and checksum
ARCHIVE_SIZE=$(du -h "$BACKUP_ARCHIVE" | cut -f1)
ARCHIVE_CHECKSUM=$(sha256sum "$BACKUP_ARCHIVE" | cut -d' ' -f1)

log_message "Backup completed successfully!"
log_message "Archive location: $BACKUP_ARCHIVE"
log_message "Archive size: $ARCHIVE_SIZE"
log_message "SHA256 checksum: $ARCHIVE_CHECKSUM"

# Clean up temporary backup directory
rm -rf "$BACKUP_DIR"

echo ""
echo "=========================================="
echo "VPS BACKUP COMPLETED SUCCESSFULLY"
echo "=========================================="
echo "Archive: $BACKUP_ARCHIVE"
echo "Size: $ARCHIVE_SIZE"
echo "Checksum: $ARCHIVE_CHECKSUM"
echo "Log file: $LOG_FILE"
echo ""
echo "To download this backup to your local machine, run:"
echo "scp root@your-server-ip:$BACKUP_ARCHIVE /local/backup/path/"
echo ""
echo "Or use rsync for better transfer:"
echo "rsync -avz --progress root@your-server-ip:$BACKUP_ARCHIVE /local/backup/path/"
echo "=========================================="
