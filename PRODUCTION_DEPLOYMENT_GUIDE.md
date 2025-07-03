# A.I.ncident Production Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying the A.I.ncident AI Incident Management Dashboard to production environments. The system consists of a FastAPI backend and Streamlit frontend with PostgreSQL database and Stripe billing integration.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [System Architecture](#system-architecture)
3. [Environment Setup](#environment-setup)
4. [Database Setup](#database-setup)
5. [Backend Deployment](#backend-deployment)
6. [Frontend Deployment](#frontend-deployment)
7. [SSL/TLS Configuration](#ssltls-configuration)
8. [Monitoring & Logging](#monitoring--logging)
9. [Backup & Recovery](#backup--recovery)
10. [Security Hardening](#security-hardening)
11. [Performance Optimization](#performance-optimization)
12. [Troubleshooting](#troubleshooting)

## Prerequisites

### Server Requirements

**Minimum Specifications:**
- **CPU**: 2 cores (4+ recommended)
- **RAM**: 4GB (8GB+ recommended)
- **Storage**: 50GB SSD (100GB+ recommended)
- **OS**: Ubuntu 20.04 LTS or later, CentOS 8+, or Debian 11+

**Recommended Specifications:**
- **CPU**: 4+ cores
- **RAM**: 16GB+
- **Storage**: 200GB+ SSD with RAID
- **Network**: 1Gbps+ connection

### Software Dependencies

```bash
# System packages
sudo apt update
sudo apt install -y python3.9 python3.9-venv python3.9-dev
sudo apt install -y postgresql postgresql-contrib
sudo apt install -y nginx certbot python3-certbot-nginx
sudo apt install -y git curl wget unzip
sudo apt install -y build-essential libpq-dev
sudo apt install -y supervisor

# Node.js (for PM2 if using)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

## System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Nginx (SSL)   │    │   Streamlit     │    │   PostgreSQL    │
│   (Port 443)    │◄──►│   (Port 8501)   │◄──►│   (Port 5432)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI       │    │   Redis         │    │   File Storage  │
│   (Port 8000)   │    │   (Rate Limiting)│   │   (Images/PDFs) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Environment Setup

### 1. Create Application User

```bash
# Create dedicated user for the application
sudo adduser aincident
sudo usermod -aG sudo aincident
sudo su - aincident
```

### 2. Clone Repository

```bash
# Clone the repository
git clone https://github.com/yourusername/IncidentIQ_Demo.git
cd IncidentIQ_Demo

# Set proper permissions
sudo chown -R aincident:aincident /home/aincident/IncidentIQ_Demo
```

### 3. Create Virtual Environments

```bash
# Backend virtual environment
cd backend
python3.9 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Frontend virtual environment
cd ../frontend
python3.9 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Database Setup

### 1. PostgreSQL Configuration

```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE aincident_prod;
CREATE USER aincident_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE aincident_prod TO aincident_user;
ALTER USER aincident_user CREATEDB;
\q
```

### 2. Database Migration

```bash
cd backend
source venv/bin/activate

# Set database URL
export DATABASE_URL="postgresql://aincident_user:your_secure_password@localhost/aincident_prod"

# Run migrations
alembic upgrade head

# Initialize database with seed data
python init_db.py
```

## Backend Deployment

### 1. Environment Configuration

Create `/home/aincident/IncidentIQ_Demo/backend/.env`:

```bash
# Database
DATABASE_URL=postgresql://aincident_user:your_secure_password@localhost/aincident_prod

# Security
SECRET_KEY=your_very_secure_jwt_secret_key_at_least_32_characters_long
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Environment
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
LOG_FILE=/home/aincident/IncidentIQ_Demo/backend/logs/app.log

# External Services
OPENAI_API_KEY=your_openai_api_key
STRIPE_SECRET_KEY=your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret

# CORS
FRONTEND_URL=https://yourdomain.com
CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# Email (optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
```

### 2. Create Systemd Service

Create `/etc/systemd/system/aincident-backend.service`:

```ini
[Unit]
Description=A.I.ncident Backend API
After=network.target postgresql.service
Wants=postgresql.service

[Service]
Type=exec
User=aincident
Group=aincident
WorkingDirectory=/home/aincident/IncidentIQ_Demo/backend
Environment=PATH=/home/aincident/IncidentIQ_Demo/backend/venv/bin
ExecStart=/home/aincident/IncidentIQ_Demo/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 3. Start Backend Service

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable aincident-backend
sudo systemctl start aincident-backend
sudo systemctl status aincident-backend
```

## Frontend Deployment

### 1. Environment Configuration

Create `/home/aincident/IncidentIQ_Demo/frontend/.env`:

```bash
# Backend API URL
BACKEND_URL=https://api.yourdomain.com

# Streamlit Configuration
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_SERVER_ENABLE_CORS=true
STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=true
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
```

### 2. Create Systemd Service

Create `/etc/systemd/system/aincident-frontend.service`:

```ini
[Unit]
Description=A.I.ncident Frontend
After=network.target aincident-backend.service
Wants=aincident-backend.service

[Service]
Type=exec
User=aincident
Group=aincident
WorkingDirectory=/home/aincident/IncidentIQ_Demo/frontend
Environment=PATH=/home/aincident/IncidentIQ_Demo/frontend/venv/bin
ExecStart=/home/aincident/IncidentIQ_Demo/frontend/venv/bin/streamlit run dashboard.py --server.port 8501 --server.address 0.0.0.0
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 3. Start Frontend Service

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable aincident-frontend
sudo systemctl start aincident-frontend
sudo systemctl status aincident-frontend
```

## SSL/TLS Configuration

### 1. Domain Configuration

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### 2. Nginx Configuration

Create `/etc/nginx/sites-available/aincident`:

```nginx
# Frontend (Streamlit)
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

    # Frontend proxy
    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}

# Backend API
server {
    listen 80;
    server_name api.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;

    # Security headers
    add_header X-Frame-Options "DENY" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;

    # API proxy
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static files
    location /static/ {
        alias /home/aincident/IncidentIQ_Demo/backend/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### 3. Enable Nginx Configuration

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/aincident /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Monitoring & Logging

### 1. Log Management

```bash
# Create log directories
sudo mkdir -p /var/log/aincident
sudo chown aincident:aincident /var/log/aincident

# Configure logrotate
sudo nano /etc/logrotate.d/aincident
```

Add to `/etc/logrotate.d/aincident`:

```
/var/log/aincident/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 aincident aincident
    postrotate
        systemctl reload aincident-backend
        systemctl reload aincident-frontend
    endscript
}
```

### 2. Health Monitoring

Create `/home/aincident/health_check.sh`:

```bash
#!/bin/bash

# Backend health check
if ! curl -f http://localhost:8000/ > /dev/null 2>&1; then
    echo "Backend is down!" | mail -s "A.I.ncident Backend Alert" admin@yourdomain.com
    sudo systemctl restart aincident-backend
fi

# Frontend health check
if ! curl -f http://localhost:8501/ > /dev/null 2>&1; then
    echo "Frontend is down!" | mail -s "A.I.ncident Frontend Alert" admin@yourdomain.com
    sudo systemctl restart aincident-frontend
fi

# Database health check
if ! sudo -u postgres pg_isready -d aincident_prod > /dev/null 2>&1; then
    echo "Database is down!" | mail -s "A.I.ncident Database Alert" admin@yourdomain.com
fi
```

```bash
# Make executable and add to crontab
chmod +x /home/aincident/health_check.sh
crontab -e
# Add: */5 * * * * /home/aincident/health_check.sh
```

## Backup & Recovery

### 1. Database Backup

Create `/home/aincident/backup_db.sh`:

```bash
#!/bin/bash

BACKUP_DIR="/home/aincident/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/aincident_db_$DATE.sql"

mkdir -p $BACKUP_DIR

# Create database backup
sudo -u postgres pg_dump aincident_prod > $BACKUP_FILE

# Compress backup
gzip $BACKUP_FILE

# Keep only last 30 days of backups
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete

# Upload to cloud storage (optional)
# aws s3 cp $BACKUP_FILE.gz s3://your-backup-bucket/
```

### 2. File Backup

Create `/home/aincident/backup_files.sh`:

```bash
#!/bin/bash

BACKUP_DIR="/home/aincident/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/aincident_files_$DATE.tar.gz"

# Backup static files
tar -czf $BACKUP_FILE -C /home/aincident/IncidentIQ_Demo/backend static/

# Keep only last 30 days of backups
find $BACKUP_DIR -name "files_*.tar.gz" -mtime +30 -delete
```

### 3. Automated Backups

```bash
# Make scripts executable
chmod +x /home/aincident/backup_*.sh

# Add to crontab
crontab -e
# Add:
# 0 2 * * * /home/aincident/backup_db.sh
# 0 3 * * * /home/aincident/backup_files.sh
```

## Security Hardening

### 1. Firewall Configuration

```bash
# Configure UFW firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 2. SSH Hardening

Edit `/etc/ssh/sshd_config`:

```bash
# Disable root login
PermitRootLogin no

# Use key-based authentication only
PasswordAuthentication no
PubkeyAuthentication yes

# Change default port (optional)
Port 2222

# Restrict users
AllowUsers aincident

# Restart SSH
sudo systemctl restart sshd
```

### 3. Application Security

```bash
# Set proper file permissions
sudo chown -R aincident:aincident /home/aincident/IncidentIQ_Demo
sudo chmod 600 /home/aincident/IncidentIQ_Demo/backend/.env
sudo chmod 600 /home/aincident/IncidentIQ_Demo/frontend/.env

# Secure database
sudo -u postgres psql -c "ALTER USER aincident_user PASSWORD 'new_secure_password';"
```

## Performance Optimization

### 1. Database Optimization

```sql
-- Add indexes for better performance
CREATE INDEX idx_incidents_timestamp ON incidents(timestamp);
CREATE INDEX idx_incidents_store_name ON incidents(store_name);
CREATE INDEX idx_incidents_user_id ON incidents(user_id);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
```

### 2. Application Optimization

```bash
# Configure Gunicorn for production (alternative to uvicorn)
pip install gunicorn

# Update backend service to use Gunicorn
ExecStart=/home/aincident/IncidentIQ_Demo/backend/venv/bin/gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 3. Nginx Optimization

Add to nginx configuration:

```nginx
# Enable gzip compression
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;

# Cache static files
location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

## Troubleshooting

### Common Issues

1. **Service Won't Start**
   ```bash
   # Check service status
   sudo systemctl status aincident-backend
   sudo journalctl -u aincident-backend -f
   
   # Check logs
   tail -f /home/aincident/IncidentIQ_Demo/backend/logs/app.log
   ```

2. **Database Connection Issues**
   ```bash
   # Test database connection
   sudo -u postgres psql -d aincident_prod -c "SELECT version();"
   
   # Check PostgreSQL logs
   sudo tail -f /var/log/postgresql/postgresql-*.log
   ```

3. **SSL Certificate Issues**
   ```bash
   # Check certificate status
   sudo certbot certificates
   
   # Renew certificates manually
   sudo certbot renew --dry-run
   ```

4. **Performance Issues**
   ```bash
   # Monitor system resources
   htop
   iotop
   nethogs
   
   # Check database performance
   sudo -u postgres psql -d aincident_prod -c "SELECT * FROM pg_stat_activity;"
   ```

### Emergency Procedures

1. **Complete System Restore**
   ```bash
   # Stop services
   sudo systemctl stop aincident-backend aincident-frontend
   
   # Restore database
   sudo -u postgres psql aincident_prod < backup_file.sql
   
   # Restore files
   tar -xzf backup_file.tar.gz -C /home/aincident/IncidentIQ_Demo/backend/
   
   # Restart services
   sudo systemctl start aincident-backend aincident-frontend
   ```

2. **Rollback Deployment**
   ```bash
   # Switch to previous version
   cd /home/aincident/IncidentIQ_Demo
   git checkout previous-version-tag
   
   # Restart services
   sudo systemctl restart aincident-backend aincident-frontend
   ```

## Maintenance

### Regular Maintenance Tasks

1. **Weekly**
   - Review logs for errors
   - Check disk space usage
   - Verify backup integrity

2. **Monthly**
   - Update system packages
   - Review security logs
   - Performance analysis

3. **Quarterly**
   - Security audit
   - Database optimization
   - SSL certificate renewal

### Update Procedures

```bash
# Create update script
nano /home/aincident/update.sh
```

```bash
#!/bin/bash

# Backup current version
cp -r /home/aincident/IncidentIQ_Demo /home/aincident/IncidentIQ_Demo.backup.$(date +%Y%m%d)

# Pull latest changes
cd /home/aincident/IncidentIQ_Demo
git pull origin main

# Update dependencies
cd backend && source venv/bin/activate && pip install -r requirements.txt
cd ../frontend && source venv/bin/activate && pip install -r requirements.txt

# Run migrations
cd ../backend && source venv/bin/activate && alembic upgrade head

# Restart services
sudo systemctl restart aincident-backend aincident-frontend

echo "Update completed successfully!"
```

---

*Last updated: January 2024*  
*Version: 1.0.0* 