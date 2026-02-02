# 🚀 מדריך פריסה ל-Production - SMARTSPORTS

> **מדריך מפורט להעלאת הפלטפורמה לאוויר**
> כולל אופציות Hosting, הגדרות, ואבטחה

---

## 📋 תוכן עניינים

- [סקירה כללית](#-סקירה-כללית)
- [צ'קליסט לפני פריסה](#-צקליסט-לפני-פריסה)
- [אופציית 1: Render.com](#-אופציה-1-rendercom-מומלץ)
- [אופציית 2: Railway.app](#-אופציה-2-railwayapp)
- [אופציית 3: Vercel + Backend](#-אופציה-3-vercel--backend-נפרד)
- [הגדרת Database](#-הגדרת-database)
- [משתני סביבה](#-משתני-סביבה)
- [אבטחה ו-HTTPS](#-אבטחה-ו-https)
- [ניטור וביצועים](#-ניטור-וביצועים)
- [עדכונים ותחזוקה](#-עדכונים-ותחזוקה)

---

## 🎯 סקירה כללית

### מה נדרש?
```
✅ Backend (FastAPI) - Python 3.9+
✅ Frontend (Static Files) - HTML/CSS/JS
✅ Database - SQLite (dev) / PostgreSQL (prod)
✅ משתני סביבה - API Keys
```

### עלויות משוערות
| שירות | תוכנית | עלות חודשית |
|-------|---------|-------------|
| Render.com | Starter | $7 |
| Railway.app | Developer | $5 + שימוש |
| Vercel | Free/Pro | $0 / $20 |
| PostgreSQL | Free/Paid | $0 / $15 |
| **סה"כ** | - | **$5-42** |

---

## ✅ צ'קליסט לפני פריסה

### 1️⃣ קוד
```bash
□ כל הקוד ב-Git
□ .env לא ב-repository
□ .gitignore מעודכן
□ requirements.txt מעודכן
□ בדיקות עוברות (pytest)
```

### 2️⃣ משתני סביבה
```bash
□ OPENAI_API_KEY מוגדר
□ API_SPORTS_KEY מוגדר
□ JWT_SECRET_KEY מוגדר (חזק!)
□ DATABASE_URL מעודכן
□ ENVIRONMENT=production
```

### 3️⃣ אבטחה
```bash
□ Passwords מוצפנים
□ Rate Limiting פעיל
□ CORS מוגדר נכון
□ HTTPS מופעל
□ API Keys לא נחשפים
```

### 4️⃣ ביצועים
```bash
□ Cache פעיל
□ Budget Tracker פעיל
□ Logging מוגדר
□ Error tracking
```

---

## 🟢 אופציה 1: Render.com (מומלץ!)

### למה Render?
- ✅ הכי קל לשימוש
- ✅ Free tier זמין
- ✅ Auto-deploy מ-Git
- ✅ PostgreSQL חינם
- ✅ HTTPS אוטומטי
- ✅ תמיכה מצוינת

### צעדי פריסה:

#### **שלב 1: הכנת הפרויקט**

צור קובץ `render.yaml` בשורש הפרויקט:

```yaml
services:
  # Backend Service
  - type: web
    name: smartsports-backend
    env: python
    region: frankfurt  # או oregon לארה"ב
    plan: starter  # $7/חודש (או free)
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn backend.app:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: OPENAI_API_KEY
        sync: false
      - key: API_SPORTS_KEY
        sync: false
      - key: JWT_SECRET_KEY
        generateValue: true
      - key: DATABASE_URL
        fromDatabase:
          name: smartsports-db
          property: connectionString
      - key: ENVIRONMENT
        value: production
      - key: PYTHONUNBUFFERED
        value: "1"

  # PostgreSQL Database
databases:
  - name: smartsports-db
    databaseName: smartsports
    user: smartsports_user
    plan: free  # או starter ($7/חודש)
```

#### **שלב 2: העלאה ל-Git**

```bash
# אם עוד לא עשית:
git init
git add .
git commit -m "Initial commit - Ready for deployment"
git remote add origin https://github.com/YourUsername/smart_sport.git
git push -u origin main
```

#### **שלב 3: פריסה ב-Render**

1. **הרשמה**: [https://render.com](https://render.com)
2. **חבר GitHub**: Settings → GitHub
3. **New Web Service**:
   - Repository: `YourUsername/smart_sport`
   - Branch: `main`
   - Root Directory: `./`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn backend.app:app --host 0.0.0.0 --port $PORT`

4. **Environment Variables**:
   ```
   OPENAI_API_KEY = sk-...
   API_SPORTS_KEY = your-key
   JWT_SECRET_KEY = (generate random)
   ENVIRONMENT = production
   ```

5. **Deploy!** לחץ על "Create Web Service"

#### **שלב 4: בדיקה**

```bash
# כתובת השרת תהיה:
https://smartsports-backend.onrender.com

# בדוק:
curl https://smartsports-backend.onrender.com/api/health
```

---

## 🔵 אופציה 2: Railway.app

### למה Railway?
- ✅ פשוט מאוד
- ✅ CLI מעולה
- ✅ תמחור שקוף
- ✅ Deploy מהיר

### צעדי פריסה:

#### **שלב 1: התקנת Railway CLI**

```bash
# macOS / Linux
curl -fsSL https://railway.app/install.sh | sh

# Windows (PowerShell)
iwr https://railway.app/install.ps1 | iex
```

#### **שלב 2: התחברות**

```bash
railway login
```

#### **שלב 3: יצירת פרויקט**

```bash
# בתיקיית הפרויקט:
railway init

# בחר: "Create new project"
# שם: smartsports
```

#### **שלב 4: הוספת Database**

```bash
railway add postgresql
```

#### **שלב 5: הגדרת משתנים**

```bash
railway variables set OPENAI_API_KEY=sk-...
railway variables set API_SPORTS_KEY=your-key
railway variables set JWT_SECRET_KEY=$(openssl rand -hex 32)
railway variables set ENVIRONMENT=production
```

#### **שלב 6: יצירת קובץ `railway.toml`**

```toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "uvicorn backend.app:app --host 0.0.0.0 --port $PORT"
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10

[env]
PYTHONUNBUFFERED = "1"
```

#### **שלב 7: פריסה**

```bash
railway up
```

#### **שלב 8: קבלת URL**

```bash
railway domain
# תקבל URL כמו: smartsports-production.up.railway.app
```

---

## 🟣 אופציה 3: Vercel + Backend נפרד

### למה Vercel?
- ✅ Frontend חינם לחלוטין!
- ✅ CDN גלובלי
- ✅ HTTPS אוטומטי
- ⚠️ Backend צריך להיות נפרד

### צעדי פריסה:

#### **חלק A: Frontend ב-Vercel**

1. **התקנת Vercel CLI**:
```bash
npm install -g vercel
```

2. **יצירת `vercel.json`**:
```json
{
  "version": 2,
  "name": "smartsports-frontend",
  "builds": [
    {
      "src": "frontend/**",
      "use": "@vercel/static"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/frontend/$1"
    }
  ],
  "env": {
    "API_BASE_URL": "https://your-backend.onrender.com"
  }
}
```

3. **פריסה**:
```bash
vercel --prod
```

#### **חלק B: Backend ב-Render/Railway**

השתמש באופציה 1 או 2 למעלה עבור Backend.

#### **חלק C: חיבור ביניהם**

עדכן `API_BASE_URL` ב-`frontend/index.html`:
```javascript
const API_BASE_URL = 'https://smartsports-backend.onrender.com';
```

---

## 🗄️ הגדרת Database

### SQLite (Development)
```env
DATABASE_URL=sqlite:///./smartsports.db
```
✅ טוב ל-Dev
❌ לא מומלץ ל-Production

### PostgreSQL (Production)

#### Render:
```bash
# אוטומטי דרך render.yaml
```

#### Railway:
```bash
railway add postgresql
# DATABASE_URL יוגדר אוטומטית
```

#### Supabase (חלופה):
```bash
# הרשמה: https://supabase.com
# צור פרויקט חדש
# העתק את DATABASE_URL
```

#### הגדרה ידנית:
```env
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

### Migration
```bash
# אם יש לך migrations:
alembic upgrade head
```

---

## 🔑 משתני סביבה

### רשימה מלאה:

```env
# ═══════════════════════════════════════
# OpenAI API
# ═══════════════════════════════════════
OPENAI_API_KEY=sk-proj-...
# קבל מ: https://platform.openai.com/api-keys

# ═══════════════════════════════════════
# API-Sports
# ═══════════════════════════════════════
API_SPORTS_KEY=your-key-here
# קבל מ: https://api-sports.io
# Free tier: 100 requests/day

# ═══════════════════════════════════════
# JWT Secret
# ═══════════════════════════════════════
JWT_SECRET_KEY=your-super-secret-random-string
# צור עם: openssl rand -hex 32

# ═══════════════════════════════════════
# Database
# ═══════════════════════════════════════
DATABASE_URL=postgresql://user:pass@host:5432/db
# או: sqlite:///./smartsports.db (dev only)

# ═══════════════════════════════════════
# Environment
# ═══════════════════════════════════════
ENVIRONMENT=production
# אופציות: development, staging, production

# ═══════════════════════════════════════
# CORS (אופציונלי)
# ═══════════════════════════════════════
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# ═══════════════════════════════════════
# Logging
# ═══════════════════════════════════════
LOG_LEVEL=INFO
# אופציות: DEBUG, INFO, WARNING, ERROR

# ═══════════════════════════════════════
# Rate Limiting (אופציונלי)
# ═══════════════════════════════════════
RATE_LIMIT_PER_MINUTE=60
```

### יצירת JWT Secret מאובטח:

```bash
# Linux / macOS
openssl rand -hex 32

# Python
python -c "import secrets; print(secrets.token_hex(32))"

# Online (אם אין אופציה אחרת)
# https://randomkeygen.com/
```

---

## 🔒 אבטחה ו-HTTPS

### HTTPS
רוב שירותי הHosting מספקים HTTPS אוטומטית:
- ✅ Render - כן
- ✅ Railway - כן
- ✅ Vercel - כן

### CORS
עדכן ב-`backend/app.py`:
```python
# הוסף את ה-domain שלך
origins = [
    "http://localhost:8000",
    "https://yourdomain.com",
    "https://www.yourdomain.com"
]
```

### Secrets ב-Git
וודא ש-`.gitignore` כולל:
```gitignore
.env
.env.*
*.db
*.db-shm
*.db-wal
__pycache__/
*.pyc
.DS_Store
```

---

## 📊 ניטור וביצועים

### Logging

עדכן ל-Production logging:
```python
# backend/app.py
import logging

if ENVIRONMENT == "production":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
```

### Health Checks

השתמש ב-endpoint:
```bash
GET /api/health
```

### Monitoring Services (אופציונלי)

- **Sentry** - Error tracking (חינם ל-5K errors/month)
- **UptimeRobot** - Uptime monitoring (חינם)
- **LogRocket** - Session replay (חינם ל-1K sessions)

---

## 🔄 עדכונים ותחזוקה

### עדכון הקוד

```bash
# 1. עדכן את הקוד
git add .
git commit -m "Update: description"
git push origin main

# 2. Render/Railway יעשו auto-deploy
# או בצע deploy ידני:
railway up  # Railway
# Render עושה auto-deploy
```

### Rollback

#### Render:
1. Dashboard → Deploys
2. בחר deploy קודם
3. לחץ "Rollback to this deploy"

#### Railway:
```bash
railway rollback
```

### Backup Database

#### PostgreSQL (Render):
```bash
pg_dump $DATABASE_URL > backup.sql
```

#### הדרך המומלצת:
הגדר Automatic Backups ב-Dashboard של השירות.

---

## 🎯 טיפים למתקדמים

### Docker (אופציונלי)

צור `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### CI/CD (GitHub Actions)

צור `.github/workflows/deploy.yml`:
```yaml
name: Deploy

on:
  push:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: |
          pip install -r requirements.txt
          pytest
```

### CDN (אופציונלי)

להאצת Frontend:
- Cloudflare (חינם)
- AWS CloudFront
- Fastly

---

## 📞 תמיכה ועזרה

### בעיות נפוצות:

**1. "Module not found"**
```bash
# וודא requirements.txt מעודכן:
pip freeze > requirements.txt
```

**2. "Database connection error"**
```bash
# בדוק DATABASE_URL:
echo $DATABASE_URL
```

**3. "CORS error"**
```bash
# עדכן origins ב-app.py
```

**4. "502 Bad Gateway"**
```bash
# בדוק logs:
railway logs  # Railway
# או ב-Dashboard של Render
```

### קבלת עזרה:

- 📧 support@smartsports.com
- 💬 [Discord Community](https://discord.gg/smartsports)
- 🐛 [GitHub Issues](https://github.com/YourUsername/smart_sport/issues)

---

## ✅ סיכום

אחרי שתסיים:
- ✅ הפלטפורמה חיה באוויר
- ✅ HTTPS פעיל
- ✅ Database פעיל
- ✅ Monitoring פעיל
- ✅ Backups מוגדרים

**כתובות לבדיקה:**
```
Frontend: https://yourdomain.com
Backend:  https://yourdomain.com/api/health
API Docs: https://yourdomain.com/docs
```

---

<div align="center">

### 🎉 מזל טוב! הפלטפורמה שלך באוויר!

**Need help? Contact us at support@smartsports.com**

</div>
