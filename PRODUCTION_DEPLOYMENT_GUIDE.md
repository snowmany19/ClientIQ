# A.I.ncident Production Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying the A.I.ncident AI Incident Management Dashboard to production environments. The system consists of a FastAPI backend and Streamlit frontend with PostgreSQL database and Stripe billing integration.

**Quick Start Options:**
- 🚀 **VPS Deployment** (Traditional) - Full control, manual setup
- ☁️ **Cloud Platform Deployment** - Automated, managed services
- 🐳 **Docker Deployment** - Containerized, portable
- 🏗️ **CI/CD Pipeline** - Automated deployment

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Deployment Options](#deployment-options)
3. [VPS Deployment (Traditional)](#vps-deployment-traditional)
4. [Cloud Platform Deployment](#cloud-platform-deployment)
5. [Docker Deployment](#docker-deployment)
6. [CI/CD Pipeline Setup](#cicd-pipeline-setup)
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

## Deployment Options

### 🚀 VPS Deployment (Traditional)
**Best for**: Full control, custom configurations, cost optimization
**Time**: 2-4 hours
**Difficulty**: Intermediate

### ☁️ Cloud Platform Deployment
**Best for**: Quick setup, managed services, scalability
**Time**: 30-60 minutes
**Difficulty**: Easy

**Supported Platforms:**
- **Railway** - Recommended for quick deployment
- **Render** - Free tier available
- **Heroku** - Enterprise features
- **DigitalOcean App Platform** - Simple deployment
- **AWS Elastic Beanstalk** - Enterprise scale

### 🐳 Docker Deployment
**Best for**: Consistent environments, easy scaling, microservices
**Time**: 1-2 hours
**Difficulty**: Intermediate

### 🏗️ CI/CD Pipeline
**Best for**: Automated deployments, team development, continuous delivery
**Time**: 2-3 hours
**Difficulty**: Advanced

## VPS Deployment (Traditional)

### System Architecture

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

### Environment Setup

#### 1. Create Application User

```bash
# Create dedicated user for the application
sudo adduser aincident
sudo usermod -aG sudo aincident
sudo su - aincident
```

#### 2. Clone Repository

```bash
# Clone the repository
git clone https://github.com/yourusername/IncidentIQ_Demo.git
cd IncidentIQ_Demo

# Set proper permissions
sudo chown -R aincident:aincident /home/aincident/IncidentIQ_Demo
```

#### 3. Create Virtual Environments

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

### Database Setup

#### 1. PostgreSQL Configuration

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

#### 2. Database Migration

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

### Backend Deployment

#### 1. Environment Configuration

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

#### 2. Create Systemd Service

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

#### 3. Start Backend Service

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable aincident-backend
sudo systemctl start aincident-backend
sudo systemctl status aincident-backend
```

### Frontend Deployment

#### 1. Environment Configuration

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

#### 2. Create Systemd Service

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

#### 3. Start Frontend Service

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable aincident-frontend
sudo systemctl start aincident-frontend
sudo systemctl status aincident-frontend
```

## Cloud Platform Deployment

### Railway Deployment (Recommended)

**Time**: 15-30 minutes

#### 1. Prepare Repository

```bash
# Add Railway configuration
mkdir .railway
```

Create `.railway/railway.json`:
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

#### 2. Deploy to Railway

1. Go to [Railway.app](https://railway.app)
2. Connect your GitHub repository
3. Add environment variables:
   ```
   DATABASE_URL=postgresql://...
   SECRET_KEY=your_jwt_secret
   OPENAI_API_KEY=your_openai_key
   STRIPE_SECRET_KEY=your_stripe_key
   ENVIRONMENT=production
   ```
4. Deploy automatically

#### 3. Configure Custom Domain

1. Add custom domain in Railway dashboard
2. Configure DNS records
3. SSL certificate automatically provisioned

### Render Deployment

**Time**: 20-40 minutes

#### 1. Create Render Service

1. Go to [Render.com](https://render.com)
2. Create new Web Service
3. Connect GitHub repository
4. Configure build settings:
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`

#### 2. Add Environment Variables

```
DATABASE_URL=postgresql://...
SECRET_KEY=your_jwt_secret
OPENAI_API_KEY=your_openai_key
STRIPE_SECRET_KEY=your_stripe_key
ENVIRONMENT=production
```

#### 3. Deploy

Render will automatically deploy and provide a URL.

## Docker Deployment

### 1. Create Dockerfile

Create `Dockerfile` in the root directory:

```dockerfile
# Multi-stage build for production
FROM python:3.9-slim as backend

WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Create `Dockerfile.frontend`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY frontend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY frontend/ .
EXPOSE 8501

CMD ["streamlit", "run", "dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### 2. Create Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:13
    environment:
      POSTGRES_DB: aincident_prod
      POSTGRES_USER: aincident_user
      POSTGRES_PASSWORD: your_secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  backend:
    build:
      context: .
      dockerfile: Dockerfile
    environment:
      - DATABASE_URL=postgresql://aincident_user:your_secure_password@postgres:5432/aincident_prod
      - SECRET_KEY=your_jwt_secret
      - OPENAI_API_KEY=your_openai_key
      - STRIPE_SECRET_KEY=your_stripe_key
      - ENVIRONMENT=production
    depends_on:
      - postgres
    ports:
      - "8000:8000"
    volumes:
      - ./backend/static:/app/static

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    environment:
      - BACKEND_URL=http://backend:8000
    depends_on:
      - backend
    ports:
      - "8501:8501"

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - backend
      - frontend

volumes:
  postgres_data:
```

### 3. Deploy with Docker

```bash
# Build and start services
docker-compose up -d

# Run database migrations
docker-compose exec backend alembic upgrade head

# Initialize database
docker-compose exec backend python init_db.py
```

## CI/CD Pipeline Setup

### GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: |
        pip install -r backend/requirements.txt
        pip install -r frontend/requirements.txt
    - name: Run tests
      run: |
        cd backend && python -m pytest

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Deploy to Railway
      uses: railway/deploy@v1
      with:
        railway_token: ${{ secrets.RAILWAY_TOKEN }}
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

### 2. Application Monitoring

```bash
# Install monitoring tools
sudo apt install htop iotop nethogs

# Monitor system resources
htop
iotop
nethogs
```

### 3. Database Monitoring

```sql
-- Monitor database performance
SELECT * FROM pg_stat_activity;
SELECT * FROM pg_stat_database;
SELECT * FROM pg_stat_user_tables;
```

## Backup & Recovery

### 1. Database Backup

```bash
# Create backup script
nano /home/aincident/backup.sh
```

```bash
#!/bin/bash

# Database backup
sudo -u postgres pg_dump aincident_prod > /home/aincident/backups/db_backup_$(date +%Y%m%d_%H%M%S).sql

# File backup
tar -czf /home/aincident/backups/files_backup_$(date +%Y%m%d_%H%M%S).tar.gz /home/aincident/IncidentIQ_Demo/backend/static/

# Keep only last 7 days of backups
find /home/aincident/backups/ -name "*.sql" -mtime +7 -delete
find /home/aincident/backups/ -name "*.tar.gz" -mtime +7 -delete
```

### 2. Automated Backups

```bash
# Add to crontab
sudo crontab -e

# Add: 0 2 * * * /home/aincident/backup.sh
```

### 3. Recovery Procedures

```bash
# Restore database
sudo -u postgres psql aincident_prod < backup_file.sql

# Restore files
tar -xzf backup_file.tar.gz -C /home/aincident/IncidentIQ_Demo/backend/
```

## Security Hardening

### 1. Firewall Configuration

```bash
# Configure UFW firewall
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
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

*Last updated: July 2025*  
*Version: 2.0.0* 