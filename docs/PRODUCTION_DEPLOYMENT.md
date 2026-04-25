# 🚀 Production Deployment Guide

**For deploying to production servers.**

---

## Environment Setup

### 1. Create Production Environment File

```bash
cp .env.production.example .env.production
```

Edit `.env.production`:
```
ENVIRONMENT=production
DEBUG=False
HOST=0.0.0.0
PORT=8000

# Database (PostgreSQL required for production)
DATABASE_URL=postgresql://user:password@db-host:5432/fabricators_prod

# LLM Settings (from testing results)
PROD_LLM_PROVIDER=unsloth
PROD_MODEL_NAME=meta-llama/Llama-2-7b-hf
PROD_MAX_TOKENS=512
PROD_TEMPERATURE=0.7

# CORS (restrict to your domain)
CORS_ORIGINS=https://yourdomain.com,https://api.yourdomain.com

# API Keys
UNSLOTH_API_KEY=your_key_here

# Logging
LOG_LEVEL=info
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Verify Configuration

```bash
export ENVIRONMENT=production
python -c "from config import get_settings; s = get_settings(); print(f'✓ Config loaded: {s.ENVIRONMENT} - {s.MODEL_NAME}')"
```

---

## Running Locally

### Development Machine

```bash
export ENVIRONMENT=production
python app.py
```

Check: http://localhost:8000/health

### With Uvicorn (Single Worker)

```bash
export ENVIRONMENT=production
uvicorn app:app --host 0.0.0.0 --port 8000
```

---

## Production Deployment

### Option 1: Gunicorn + Uvicorn (Recommended)

```bash
# Install gunicorn
pip install gunicorn

# Run with 4 workers (adjust based on CPU cores)
export ENVIRONMENT=production
gunicorn app:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --log-level info
```

### Option 2: Docker

**Dockerfile:**
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Set production environment
ENV ENVIRONMENT=production

EXPOSE 8000

CMD ["gunicorn", "app:app", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000"]
```

**Build & Run:**
```bash
docker build -t fabricators-ai:latest .

docker run -d \
  --name fabricators-ai \
  -p 8000:8000 \
  --env-file .env.production \
  fabricators-ai:latest
```

### Option 3: Systemd Service

**Create `/etc/systemd/system/fabricators-ai.service`:**

```ini
[Unit]
Description=Fabricators AI Service
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/home/www-data/fabricators_ai
EnvironmentFile=/home/www-data/fabricators_ai/.env.production
ExecStart=/usr/bin/gunicorn app:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --log-level info

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable & Start:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable fabricators-ai
sudo systemctl start fabricators-ai
```

**Monitor:**
```bash
sudo systemctl status fabricators-ai
sudo journalctl -u fabricators-ai -f
```

---

## Reverse Proxy Setup

### Nginx Configuration

**`/etc/nginx/sites-available/fabricators-ai`:**

```nginx
upstream fabricators_ai {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name api.yourdomain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    # SSL certificates (use Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;

    # Proxy settings
    location / {
        proxy_pass http://fabricators_ai;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Rate limiting
    limit_req zone=api burst=100 nodelay;
}
```

**Enable:**
```bash
sudo ln -s /etc/nginx/sites-available/fabricators-ai /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## Monitoring & Logging

### Application Logs

```bash
# View recent logs
tail -f /var/log/fabricators-ai.log

# Check for errors
grep ERROR /var/log/fabricators-ai.log

# Tail with systemd
sudo journalctl -u fabricators-ai -f -n 100
```

### Health Checks

```bash
# Health endpoint
curl https://api.yourdomain.com/health

# Expected response:
# {"status":"healthy","version":"1.0.0"}
```

### Performance Monitoring

```bash
# CPU & Memory
top -p $(pgrep -f "gunicorn app:app")

# Port monitoring
netstat -tlnp | grep 8000

# Connections
lsof -i :8000
```

---

## Database Setup

### PostgreSQL

```bash
# Create database
createdb fabricators_prod -U postgres

# Run migrations (if using Alembic)
alembic upgrade head

# Verify connection
psql -d fabricators_prod -c "SELECT version();"
```

### Backup Strategy

```bash
# Daily backup
0 2 * * * pg_dump fabricators_prod | gzip > /backups/db_$(date +\%Y\%m\%d).sql.gz

# Retention (keep 30 days)
find /backups -name "db_*.sql.gz" -mtime +30 -delete
```

---

## SSL/TLS Certificates

### Using Let's Encrypt

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot certonly --nginx -d api.yourdomain.com

# Auto-renewal (runs twice daily)
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer

# Verify renewal
sudo certbot renew --dry-run
```

---

## Security Checklist

- [ ] `.env.production` is not in git (add to `.gitignore`)
- [ ] Database password is strong
- [ ] SSL/TLS certificates installed
- [ ] Firewall configured (only allow ports 80, 443)
- [ ] API key is secure (use environment variables)
- [ ] CORS origins restricted to your domain
- [ ] Logs are monitored for errors
- [ ] Database backups are automated
- [ ] Rate limiting is enabled
- [ ] Security headers are set (Nginx config above)

---

## Deployment Checklist

Before deploying to production:

- [ ] Tested in staging environment first
- [ ] All environment variables in `.env.production`
- [ ] Database is running and accessible
- [ ] SSL certificate installed
- [ ] Nginx/reverse proxy configured
- [ ] Systemd service created and enabled
- [ ] Health endpoint responding
- [ ] Logs being collected
- [ ] Backups configured
- [ ] Monitoring alerts set up
- [ ] Team notified of deployment

---

## Troubleshooting

### App won't start

```bash
# Check environment
echo $ENVIRONMENT
cat .env.production | head

# Test config loading
python -c "from config import get_settings; print(get_settings())"

# Check database connection
python -c "from config import get_settings; import sqlalchemy; engine = sqlalchemy.create_engine(get_settings().DATABASE_URL); print(engine.execute('SELECT 1'))"
```

### Port already in use

```bash
# Find process using port 8000
lsof -i :8000

# Kill if needed
kill -9 <PID>
```

### High memory usage

```bash
# Reduce worker count
gunicorn app:app --workers 2

# Or use async workers
gunicorn app:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --worker-connections 100
```

### Database connection errors

```bash
# Test connection
psql -h db-host -U username -d fabricators_prod -c "SELECT 1"

# Check pool settings in config
```

---

## Scaling

### Multiple Servers (Load Balancing)

1. Deploy app to multiple servers
2. Use Nginx as load balancer
3. Shared database (PostgreSQL)
4. Cache with Redis (optional)

### Caching

Add Redis for faster responses:

```python
# In config/production.py
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
```

---

## Rollback Procedure

```bash
# If new deploy breaks:
git checkout <previous-commit-hash>
systemctl restart fabricators-ai

# Or with Docker:
docker stop fabricators-ai
docker run -d --name fabricators-ai <previous-image-id>
```

---

## Support

For issues:
1. Check logs: `journalctl -u fabricators-ai -f`
2. Test health: `curl /health`
3. Check environment: `cat .env.production`
4. Review deployment guide above

---

**Ready to deploy?** Run the deployment checklist above! 🚀
