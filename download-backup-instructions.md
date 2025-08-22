# VPS Server Backup Download Instructions

## Quick Start

1. **Upload and run the backup script on your VPS:**
   ```bash
   # Upload the backup script to your server
   scp vps-backup-script.sh root@your-server-ip:/root/
   
   # SSH into your server
   ssh root@your-server-ip
   
   # Make the script executable and run it
   chmod +x /root/vps-backup-script.sh
   /root/vps-backup-script.sh
   ```

2. **Download the backup to your local machine:**
   ```bash
   # Using SCP (replace with your actual server IP)
   scp root@your-server-ip:/tmp/vps_complete_backup_*.tar.gz ./
   
   # Or using rsync for better progress and resume capability
   rsync -avz --progress root@your-server-ip:/tmp/vps_complete_backup_*.tar.gz ./
   ```

## What Gets Backed Up

### 🏠 **User Data & Applications**
- All home directories (`/home/*`)
- Root directory (`/root`)
- Your applications (`quality-app`, `vue-broker-gpt`, etc.)
- Web directories (`/var/www`, `/opt`, `/srv`)

### ⚙️ **System Configuration**
- Complete `/etc` directory (all system configs)
- Installed packages list (apt/yum/rpm)
- Systemd services and their states
- Cron jobs and scheduled tasks
- Network configuration

### 🌐 **Web Server & SSL**
- Nginx/Apache configurations
- SSL certificates (Let's Encrypt, custom certs)
- Virtual host configurations

### 🗄️ **Databases** (if present)
- Complete MySQL/MariaDB dumps
- Complete PostgreSQL dumps
- Database users and permissions

### 📋 **System Information**
- Hardware information (CPU, RAM, disk)
- Network configuration and open ports
- Running processes and services
- System logs (last 7 days)
- Firewall rules

## Advanced Options

### 1. **Selective Backup** (if you want to exclude certain directories)
Edit the script and add exclusions:
```bash
# Add to the tar command
tar -czf "$BACKUP_ARCHIVE" "$(basename "$BACKUP_DIR")" \
    --exclude='*.sock' \
    --exclude='proc/*' \
    --exclude='sys/*' \
    --exclude='dev/*' \
    --exclude='large-files/*'
```

### 2. **Incremental Backup** (for regular backups)
```bash
# Create a script for daily incremental backups
rsync -avz --delete /root/ backup-server:/backups/daily/root/
rsync -avz --delete /home/ backup-server:/backups/daily/home/
```

### 3. **Automated Backup with Cron**
Add to your crontab for weekly backups:
```bash
# Edit crontab
crontab -e

# Add this line for weekly backup every Sunday at 2 AM
0 2 * * 0 /root/vps-backup-script.sh && rsync -avz /tmp/vps_complete_backup_*.tar.gz user@backup-server:/backups/
```

## Security Considerations

### 🔐 **Before Running**
1. **Review sensitive data**: The backup includes all system files, including any stored passwords or keys
2. **Secure transfer**: Use SSH keys instead of passwords for file transfers
3. **Encrypt backup**: Consider encrypting the backup archive:
   ```bash
   # Encrypt the backup
   gpg --symmetric --cipher-algo AES256 vps_complete_backup_*.tar.gz
   ```

### 🛡️ **SSH Key Setup** (recommended)
```bash
# On your local machine, generate SSH key if you don't have one
ssh-keygen -t rsa -b 4096

# Copy public key to server
ssh-copy-id root@your-server-ip

# Now you can transfer files without password prompts
```

## Troubleshooting

### ❌ **Common Issues**

1. **Permission denied errors**: Run script as root or with sudo
2. **Disk space issues**: Check available space with `df -h` before running
3. **Large backup size**: The backup might be several GB depending on your server content

### 📊 **Monitor Backup Progress**
```bash
# Watch the backup process
tail -f /tmp/backup_*.log

# Check current backup size while it's running
watch -n 5 'du -sh /tmp/vps_backup_*'
```

### 🚀 **Speed Up Transfer**
```bash
# Use compression during transfer
rsync -avz --compress-level=9 --progress root@server:/tmp/backup.tar.gz ./

# Or use multiple parallel connections
# Install and use aria2c for faster downloads
aria2c -x 4 -s 4 "scp://root@server/tmp/backup.tar.gz"
```

## Restoration Notes

When you need to restore from this backup:

1. **Extract the archive**: `tar -xzf vps_complete_backup_*.tar.gz`
2. **Review the backup manifest**: Check `backup_manifest.txt` for contents
3. **Selective restore**: Copy only the directories/files you need
4. **System restore**: For complete system restore, you'll need a fresh server installation first

## File Structure of Backup

```
vps_backup_YYYYMMDD_HHMMSS/
├── applications/           # Web apps and services
├── crontabs/              # Scheduled tasks
├── databases/             # Database dumps
├── home_backup/           # User home directories
├── logs/                  # Recent system logs
├── root_backup/           # Root user directory
├── ssl/                   # SSL certificates
├── system_config/         # Complete /etc directory
├── system_info/           # System information files
├── webserver/             # Web server configs
├── backup_manifest.txt    # Complete file listing
└── backup_info.txt        # Backup metadata
```

This backup strategy ensures you have everything needed to restore your server or migrate to a new one!
