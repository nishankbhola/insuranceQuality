#!/bin/bash

# Backup Verification Script
# Run this after downloading your backup to verify its integrity

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local status=$1
    local message=$2
    case $status in
        "OK")
            echo -e "${GREEN}✓${NC} $message"
            ;;
        "WARNING")
            echo -e "${YELLOW}⚠${NC} $message"
            ;;
        "ERROR")
            echo -e "${RED}✗${NC} $message"
            ;;
        "INFO")
            echo -e "ℹ $message"
            ;;
    esac
}

# Check if backup file is provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 <backup-file.tar.gz>"
    echo "Example: $0 vps_complete_backup_20241201_143022.tar.gz"
    exit 1
fi

BACKUP_FILE="$1"

print_status "INFO" "Starting backup verification for: $BACKUP_FILE"
echo "========================================"

# 1. Check if backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    print_status "ERROR" "Backup file not found: $BACKUP_FILE"
    exit 1
fi
print_status "OK" "Backup file exists"

# 2. Check file size
BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
print_status "INFO" "Backup file size: $BACKUP_SIZE"

# 3. Test archive integrity
print_status "INFO" "Testing archive integrity..."
if tar -tzf "$BACKUP_FILE" > /dev/null 2>&1; then
    print_status "OK" "Archive integrity test passed"
else
    print_status "ERROR" "Archive integrity test failed"
    exit 1
fi

# 4. Extract and examine contents (to temporary directory)
TEMP_DIR=$(mktemp -d)
print_status "INFO" "Extracting backup to temporary directory: $TEMP_DIR"

tar -xzf "$BACKUP_FILE" -C "$TEMP_DIR"

# Find the backup directory (should be the only directory in temp)
BACKUP_DIR=$(find "$TEMP_DIR" -maxdepth 1 -type d -name "vps_backup_*")

if [ -z "$BACKUP_DIR" ]; then
    print_status "ERROR" "Could not find backup directory in archive"
    rm -rf "$TEMP_DIR"
    exit 1
fi

print_status "OK" "Found backup directory: $(basename "$BACKUP_DIR")"

# 5. Check essential directories exist
echo ""
print_status "INFO" "Checking backup contents..."

essential_dirs=("system_config" "system_info" "root_backup")
for dir in "${essential_dirs[@]}"; do
    if [ -d "$BACKUP_DIR/$dir" ]; then
        print_status "OK" "Found $dir directory"
    else
        print_status "WARNING" "Missing $dir directory"
    fi
done

# 6. Check if applications are backed up
if [ -d "$BACKUP_DIR/applications" ]; then
    print_status "OK" "Applications directory found"
    app_count=$(find "$BACKUP_DIR/applications" -mindepth 1 -maxdepth 1 -type d | wc -l)
    print_status "INFO" "Application directories found: $app_count"
else
    print_status "WARNING" "No applications directory found"
fi

# 7. Check system information files
echo ""
print_status "INFO" "Checking system information files..."

info_files=("system_info.txt" "disk_usage.txt" "memory_info.txt" "installed_packages_apt.txt" "systemd_services.txt")
for file in "${info_files[@]}"; do
    if [ -f "$BACKUP_DIR/system_info/$file" ]; then
        print_status "OK" "Found $file"
    else
        print_status "WARNING" "Missing $file"
    fi
done

# 8. Check for databases
if [ -d "$BACKUP_DIR/databases" ]; then
    print_status "OK" "Database backup directory found"
    db_files=$(find "$BACKUP_DIR/databases" -name "*.sql" | wc -l)
    if [ "$db_files" -gt 0 ]; then
        print_status "OK" "Found $db_files database dump files"
    else
        print_status "INFO" "No database dump files found (may not have databases)"
    fi
else
    print_status "INFO" "No database backup directory (may not have databases)"
fi

# 9. Check backup manifest and info
if [ -f "$BACKUP_DIR/backup_manifest.txt" ]; then
    print_status "OK" "Backup manifest found"
    file_count=$(wc -l < "$BACKUP_DIR/backup_manifest.txt")
    print_status "INFO" "Total files in backup: $file_count"
else
    print_status "WARNING" "Backup manifest missing"
fi

if [ -f "$BACKUP_DIR/backup_info.txt" ]; then
    print_status "OK" "Backup info found"
    echo ""
    print_status "INFO" "Backup information:"
    while IFS= read -r line; do
        echo "    $line"
    done < "$BACKUP_DIR/backup_info.txt"
else
    print_status "WARNING" "Backup info missing"
fi

# 10. Calculate total extracted size
echo ""
extracted_size=$(du -sh "$BACKUP_DIR" | cut -f1)
print_status "INFO" "Extracted backup size: $extracted_size"

# 11. Quick content preview
echo ""
print_status "INFO" "Top-level backup contents:"
ls -la "$BACKUP_DIR" | head -20

# Cleanup
rm -rf "$TEMP_DIR"

echo ""
echo "========================================"
print_status "OK" "Backup verification completed successfully!"
echo ""
print_status "INFO" "Summary:"
echo "  - Backup file: $BACKUP_FILE"
echo "  - Compressed size: $BACKUP_SIZE"
echo "  - Extracted size: $extracted_size"
echo ""
print_status "INFO" "Your backup appears to be complete and ready for storage or restoration."
