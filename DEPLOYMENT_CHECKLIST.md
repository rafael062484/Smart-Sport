# 🚀 SmartSport Platform – Production Deployment Checklist

> **Version:** 3.0.0
> **Last Updated:** 2026-01-18
> **Status:** Pre-Production Ready

---

## 📋 Overview

This checklist covers all steps needed to deploy SmartSport from development to production environment.

**Estimated Time:** 4-6 hours (first deployment)
**Prerequisites:** VPS/Cloud server, domain name, SSH access

---

## 1️⃣ Infrastructure & Hosting

### ☐ Domain Purchase
- [ ] Register domain (recommended: Cloudflare, Namecheap, GoDaddy)
- [ ] Configure DNS to point to server IP
- [ ] Enable DNS management for easy updates
- [ ] Consider SSL/TLS certificate (Let's Encrypt - free)

**Recommended Domain:** `smartsport.io` / `smartsport.app` / `smartsport.co.il`

### ☐ VPS / Cloud Server
- [ ] **Minimum Specs:**
  - 2GB RAM
  - 1 CPU core
  - 20GB SSD storage
  - Ubuntu 22.04 LTS / Debian 12
- [ ] **Recommended Providers:**
  - DigitalOcean ($12/month)
  - Linode ($10/month)
  - AWS Lightsail ($10/month)
  - Hetzner ($5/month - EU)
- [ ] SSH access configured (root or sudo user)
- [ ] Server IP address noted

### ☐ Firewall Configuration
- [ ] Open port 22 (SSH)
- [ ] Open port 80 (HTTP)
- [ ] Open port 443 (HTTPS)
- [ ] Close all other ports
- [ ] Enable UFW (Ubuntu) or iptables:
```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

---

## 2️⃣ Backend Setup

### ☐ File Transfer
- [ ] Upload `backend/` directory to server
- [ ] Upload `.env` file (with NEW API keys)
- [ ] Upload `requirements.txt`
- [ ] Create directory structure:
```bash
mkdir -p /home/ubuntu/smartsport
cd /home/ubuntu/smartsport
```

### ☐ Environment Variables (.env)
- [ ] Verify `OPENAI_API_KEY` (new key from 2026-01-17)
- [ ] Verify `API_SPORTS_KEY` (new key from 2026-01-17)
- [ ] Verify `SECRET_KEY` (JWT secret)
- [ ] Update `DATABASE_URL` to production path:
```env
DATABASE_URL=sqlite:////home/ubuntu/smartsport/backend/smartsports.db
```
- [ ] Set `DEBUG=false`
- [ ] Set `CORS_ORIGINS` to production domain

### ☐ Python Environment
- [ ] Install Python 3.11+:
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip -y
```
- [ ] Create virtual environment:
```bash
python3.11 -m venv venv
source venv/bin/activate
```
- [ ] Install dependencies:
```bash
pip install -r requirements.txt
```

### ☐ Database Setup
- [ ] Verify database file path (absolute path)
- [ ] Initialize database:
```bash
cd backend
python -c "from db import init_db; init_db()"
```
- [ ] Check database permissions:
```bash
chmod 644 backend/smartsports.db
```

### ☐ Local Server Test
- [ ] Run server locally on server:
```bash
python backend/app.py
```
- [ ] Test health endpoint:
```bash
curl http://127.0.0.1:8000/api/health
curl http://127.0.0.1:8000/api/monitoring/health
```
- [ ] Verify Phase 2 & Phase 3 loaded correctly

---

## 3️⃣ Production Server Configuration

### ☐ Gunicorn + Uvicorn Installation
- [ ] Install production ASGI server:
```bash
pip install gunicorn uvicorn[standard]
```
- [ ] Test Gunicorn:
```bash
gunicorn backend.app:app \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --workers 3 \
  --timeout 120
```

### ☐ Nginx Reverse Proxy
- [ ] Install Nginx:
```bash
sudo apt install nginx -y
```
- [ ] Create Nginx config: `/etc/nginx/sites-available/smartsport`
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # Frontend
    location / {
        root /home/ubuntu/smartsport/frontend;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
    }

    # WebSocket support (if needed)
    location /ws {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```
- [ ] Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/smartsport /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### ☐ SSL/TLS with Let's Encrypt
- [ ] Install Certbot:
```bash
sudo apt install certbot python3-certbot-nginx -y
```
- [ ] Generate SSL certificate:
```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```
- [ ] Test auto-renewal:
```bash
sudo certbot renew --dry-run
```
- [ ] Verify HTTPS working:
```bash
curl https://yourdomain.com/api/health
```

### ☐ Systemd Service (Auto-restart)
- [ ] Create service file: `/etc/systemd/system/smartsport.service`
```ini
[Unit]
Description=SmartSport Platform - AI Sports Prediction
After=network.target

[Service]
Type=notify
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/smartsport
Environment="PATH=/home/ubuntu/smartsport/venv/bin"
ExecStart=/home/ubuntu/smartsport/venv/bin/gunicorn backend.app:app \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --workers 3 \
  --timeout 120 \
  --access-logfile /home/ubuntu/smartsport/logs/access.log \
  --error-logfile /home/ubuntu/smartsport/logs/error.log
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```
- [ ] Create logs directory:
```bash
mkdir -p /home/ubuntu/smartsport/logs
```
- [ ] Enable and start service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable smartsport
sudo systemctl start smartsport
sudo systemctl status smartsport
```

---

## 4️⃣ Frontend Deployment

### ☐ File Transfer
- [ ] Upload all files from `frontend/` to `/home/ubuntu/smartsport/frontend/`
- [ ] Verify directory structure:
```
frontend/
├── index.html (TITAN chat)
├── predictions.html
├── subscribe.html
├── profile.html
├── login.html
├── assets/
├── components/
└── manifest.json
```

### ☐ Configuration Updates
- [ ] Update API base URL in frontend JavaScript files:
```javascript
// Old (development)
const API_BASE = 'http://localhost:8000';

// New (production)
const API_BASE = 'https://yourdomain.com';
```
- [ ] Update `manifest.json` URLs
- [ ] Update service worker URLs (if any)

### ☐ PWA Configuration
- [ ] Verify `manifest.json` is accessible
- [ ] Verify service worker registered
- [ ] Test offline functionality
- [ ] Test "Add to Home Screen" on mobile

### ☐ HTTPS & Deep Linking
- [ ] Test all pages load over HTTPS
- [ ] Test direct links (e.g., `/subscribe.html`)
- [ ] Verify no mixed content warnings
- [ ] Test on mobile browsers (iOS Safari, Android Chrome)

---

## 5️⃣ Pre-Go-Live Checks

### ☐ API Endpoint Testing
- [ ] Health check:
```bash
curl https://yourdomain.com/api/health
```
- [ ] Today's matches:
```bash
curl https://yourdomain.com/api/today-matches
```
- [ ] TITAN chat:
```bash
curl -X POST https://yourdomain.com/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"מי ינצח: ריאל מדריד נגד ברצלונה?"}'
```
- [ ] Prediction with confidence:
```bash
curl -X POST https://yourdomain.com/api/predict/single \
  -H "Content-Type: application/json" \
  -d '{"home":"Manchester City","away":"Liverpool","league":"Premier League","depth":"standard"}'
```

### ☐ Authentication Flow
- [ ] Register new user:
```bash
curl -X POST https://yourdomain.com/api/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","email":"test@test.com","password":"test123"}'
```
- [ ] Login:
```bash
curl -X POST https://yourdomain.com/api/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test123"}'
```
- [ ] Get profile (with JWT):
```bash
curl https://yourdomain.com/api/profile \
  -H "Authorization: Bearer <token>"
```

### ☐ Subscription Flow (Phase 2.6)
- [ ] Test subscription endpoint:
```bash
curl -X POST https://yourdomain.com/api/subscribe \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"plan":"premium"}'
```
- [ ] Verify database update (`is_premium=1`)
- [ ] Verify profile shows Premium badge
- [ ] Test Premium-only features (if any)

### ☐ Confidence Score System (Phase 3)
- [ ] Verify prediction returns confidence score
- [ ] Test Free tier (score + level + explanation only)
- [ ] Test Premium tier (+ factors breakdown)
- [ ] Verify confidence score is deterministic

### ☐ Rate Limiting & Security
- [ ] Test rate limits (20/minute on `/api/chat`)
- [ ] Test CORS headers
- [ ] Test JWT expiration
- [ ] Test invalid API requests (should return proper errors)

### ☐ Performance Testing
- [ ] Measure page load time (< 3 seconds)
- [ ] Measure API response time (< 5 seconds)
- [ ] Test under load (10+ concurrent users)
- [ ] Check memory usage (should stay < 80% of available RAM)

---

## 6️⃣ Post-Go-Live Monitoring

### ☐ Logging Setup
- [ ] Configure log rotation: `/etc/logrotate.d/smartsport`
```
/home/ubuntu/smartsport/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    create 0640 ubuntu ubuntu
    sharedscripts
    postrotate
        systemctl reload smartsport
    endscript
}
```
- [ ] Test log rotation:
```bash
sudo logrotate -f /etc/logrotate.d/smartsport
```

### ☐ Database Backup
- [ ] Create backup directory:
```bash
mkdir -p /home/ubuntu/backups
```
- [ ] Add daily backup cron job:
```bash
crontab -e
```
Add:
```cron
0 2 * * * cp /home/ubuntu/smartsport/backend/smartsports.db /home/ubuntu/backups/smartsports_$(date +\%F).db
0 3 * * * find /home/ubuntu/backups -name "smartsports_*.db" -mtime +30 -delete
```
- [ ] Test backup manually:
```bash
cp /home/ubuntu/smartsport/backend/smartsports.db /home/ubuntu/backups/test_backup.db
ls -lh /home/ubuntu/backups/
```

### ☐ API Usage Monitoring
- [ ] Monitor OpenAI API usage (dashboard: platform.openai.com)
- [ ] Monitor API-Sports usage (dashboard: dashboard.api-football.com)
- [ ] Check Phase 2 API budget tracker:
```bash
curl https://yourdomain.com/api/api-budget/status
```
- [ ] Set up alerts for 80% usage

### ☐ System Health Monitoring
- [ ] CPU usage:
```bash
top -bn1 | grep "Cpu(s)"
```
- [ ] Memory usage:
```bash
free -h
```
- [ ] Disk space:
```bash
df -h
```
- [ ] Server uptime:
```bash
uptime
```
- [ ] Service status:
```bash
sudo systemctl status smartsport
sudo systemctl status nginx
```

### ☐ Certificate & Key Management
- [ ] Set reminder: SSL certificate renewal (every 90 days - auto with Certbot)
- [ ] Set reminder: API keys rotation (every 90 days - manual)
- [ ] Set reminder: JWT secret rotation (every 180 days)
- [ ] Document key rotation procedure in team wiki

### ☐ Analytics & Metrics (Optional)
- [ ] Set up Google Analytics / Plausible
- [ ] Track key metrics:
  - Daily active users (DAU)
  - Predictions per day
  - Subscription conversion rate
  - Confidence score distribution
  - API response times
- [ ] Set up alerts for anomalies

---

## ✅ Final Validation Checklist

Before announcing "Go-Live":

- [ ] **Backend:** All API endpoints responding correctly
- [ ] **Frontend:** All pages load over HTTPS
- [ ] **Database:** Backup system working
- [ ] **Monitoring:** Logs being written and rotated
- [ ] **Security:** SSL valid, API keys secure, rate limiting active
- [ ] **Phase 2:** Cache + API budget tracker operational
- [ ] **Phase 2.6:** Subscription flow tested end-to-end
- [ ] **Phase 3:** Confidence scores appearing in predictions
- [ ] **Performance:** Response times acceptable (< 5s for predictions)
- [ ] **Mobile:** PWA installable, works offline

---

## 🎉 Go-Live Approved!

Once all checkboxes are ✅:

**SmartSport Platform is PRODUCTION READY**

🚀 **Launch Steps:**
1. Announce to beta users
2. Monitor first 24 hours closely
3. Collect user feedback
4. Iterate based on real usage
5. Scale infrastructure as needed

---

## 📞 Emergency Contacts

**Server Issues:**
- SSH: `ssh ubuntu@your-server-ip`
- Service restart: `sudo systemctl restart smartsport`
- Nginx restart: `sudo systemctl restart nginx`
- Logs: `tail -f /home/ubuntu/smartsport/logs/error.log`

**API Issues:**
- OpenAI Status: https://status.openai.com
- API-Sports Status: https://status.api-football.com

**Database Recovery:**
```bash
# Stop service
sudo systemctl stop smartsport

# Restore from backup
cp /home/ubuntu/backups/smartsports_YYYY-MM-DD.db /home/ubuntu/smartsport/backend/smartsports.db

# Start service
sudo systemctl start smartsport
```

---

## 📚 Additional Resources

- [SmartSport STATUS.md](./STATUS.md) - Full project documentation
- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/)
- [Nginx Configuration Best Practices](https://nginx.org/en/docs/)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)
- [Systemd Service Guide](https://www.freedesktop.org/software/systemd/man/systemd.service.html)

---

**Document Version:** 1.0
**Last Updated:** 2026-01-18
**Maintained by:** Rafael (CTO) & AI Assistant
**Next Review:** Before production deployment
