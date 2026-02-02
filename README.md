# 🏆 SMARTSPORTS - פלטפורמת AI לניתוח ספורט

> **פלטפורמה מתקדמת לתחזיות ספורט מבוססות בינה מלאכותית**
> משלבת OpenAI GPT-4o + API-Sports לניתוחים מדויקים בזמן אמת

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-orange.svg)](https://openai.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📋 תוכן עניינים

- [אודות הפרויקט](#-אודות-הפרויקט)
- [תכונות עיקריות](#-תכונות-עיקריות)
- [טכנולוגיות](#️-טכנולוגיות)
- [התקנה והרצה](#-התקנה-והרצה)
- [מבנה הפרויקט](#-מבנה-הפרויקט)
- [API Endpoints](#-api-endpoints)
- [עלויות](#-עלויות)
- [פריסה ל-Production](#-פריסה-ל-production)
- [תרומה לפרויקט](#-תרומה-לפרויקט)

---

## 🎯 אודות הפרויקט

**SMARTSPORTS** היא פלטפורמת AI מתקדמת המספקת:

- 🤖 **תחזיות AI חכמות** - ניתוח משחקים מבוסס GPT-4o
- 📊 **נתונים בזמן אמת** - אינטגרציה עם API-Sports
- 💬 **TITAN AI Chat** - בוט אנליסט ספורט אינטראקטיבי
- 📰 **חדשות ספורט** - עדכונים אוטומטיים מ-Ynet
- 🎮 **Game Arena** - אתגרי תחזיות מול AI
- 📈 **מערכת מנויים** - Free + Premium tiers

---

## ✨ תכונות עיקריות

### 🔮 מנוע תחזיות AI
- ניתוח מעמיק של משחקים עם GPT-4o
- שימוש בנתונים אמיתיים מ-API-Sports
- תחזיות יחידות ומרובות (Batch)
- ניקוד ביטחון ו-Explainable AI

### 💬 TITAN AI Chat
- בוט אנליסט חכם בעברית
- היסטוריית שיחה ו-Context awareness
- AI Routing חכם (69% חיסכון בעלויות)
- תמיכה ב-3 ספורטים: כדורגל, כדורסל, טניס

### 📰 מערכת חדשות
- משיכת RSS אוטומטית מ-Ynet ספורט
- סינון חכם לכתבות ספורט בלבד
- תמונות אמיתיות מהמקורות
- רענון אוטומטי כל 30 דקות
- **0 עלות** - ללא שימוש ב-AI לתקצירים

### 🎮 Game Arena
- אתגרי תחזיות מול AI
- מערכת ניקוד ודירוג
- תחרויות שבועיות

### 🔐 מערכת משתמשים
- רישום והתחברות מאובטחים
- JWT Authentication
- מנויים: Free / Premium
- פרופיל אישי עם היסטוריה

---

## 🛠️ טכנולוגיות

### Backend
```
🐍 Python 3.9+
⚡ FastAPI - Web Framework
🤖 OpenAI GPT-4o / GPT-4o-mini
📊 API-Sports - נתוני ספורט
🗄️ SQLAlchemy + SQLite/PostgreSQL
🔒 JWT + PBKDF2 - אבטחה
📦 Pydantic - Validation
🔄 AsyncIO - פעולות אסינכרוניות
```

### Frontend
```
🎨 HTML5 + CSS3
⚡ JavaScript (Vanilla)
🎯 Bootstrap 5
📱 Responsive Design
🖼️ API-Sports Widgets
```

### AI & Data
```
🧠 OpenAI GPT-4o (תחזיות מורכבות)
💡 OpenAI GPT-4o-mini (שאלות פשוטות)
⚽ API-Sports (משחקים, סטטיסטיקות)
📰 RSS Feeds (חדשות)
💾 Cache Manager (70-90% חיסכון)
💰 Budget Tracker (בקרת עלויות)
```

---

## 🚀 התקנה והרצה

### דרישות מקדימות
```bash
- Python 3.9+
- pip (Python package manager)
- Git
```

### 1️⃣ שכפול הפרויקט
```bash
git clone https://github.com/YourUsername/smart_sport.git
cd smart_sport
```

### 2️⃣ התקנת תלויות
```bash
pip install -r requirements.txt
```

### 3️⃣ הגדרת משתני סביבה
צור קובץ `.env` בשורש הפרויקט:

```env
# OpenAI API
OPENAI_API_KEY=sk-your-key-here

# API-Sports
API_SPORTS_KEY=your-api-sports-key

# JWT Secret
JWT_SECRET_KEY=your-random-secret-key-here

# Database (אופציונלי)
DATABASE_URL=sqlite:///./smartsports.db

# Environment
ENVIRONMENT=development
```

### 4️⃣ הרצת השרת
```bash
# אופציה 1: הרצה ישירה
python backend/app.py

# אופציה 2: עם Uvicorn
uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
```

### 5️⃣ פתיחת הדפדפן
```
🏠 דף הבית:    http://localhost:8000
📚 API Docs:    http://localhost:8000/docs
💚 Health:      http://localhost:8000/api/health
```

---

## 📁 מבנה הפרויקט

```
smart_sport/
│
├── backend/                    # Backend (FastAPI)
│   ├── app.py                 # 🔥 קובץ ראשי (3,518 שורות!)
│   ├── ai_predictor.py        # 🤖 מנוע תחזיות AI
│   ├── predictions.py         # 🔮 Router תחזיות
│   ├── sports_api.py          # ⚽ אינטגרציה עם API-Sports
│   ├── cache_manager.py       # 💾 Cache חכם
│   ├── api_budget_tracker.py  # 💰 בקרת תקציב
│   ├── game_engine.py         # 🎮 מנוע Game Arena
│   ├── models.py              # 📊 מודלים של Database
│   ├── security.py            # 🔒 אבטחה
│   │
│   └── routers/               # API Routers
│       ├── auth_router.py     # 🔐 רישום והתחברות
│       ├── game_router.py     # 🎮 Game Arena
│       ├── admin_router.py    # 👑 ניהול
│       ├── health_router.py   # 💚 Health checks
│       └── support_router.py  # 🆘 תמיכה
│
├── frontend/                   # Frontend (HTML/CSS/JS)
│   ├── index.html             # 🏠 דף הבית
│   ├── predictions.html       # 🔮 תחזיות
│   ├── news.html              # 📰 חדשות
│   ├── game_arena.html        # 🎮 אזור המשחקים
│   ├── login.html             # 🔐 התחברות
│   ├── profile.html           # 👤 פרופיל
│   └── about.html             # ℹ️ אודות
│
├── .env                        # 🔒 משתני סביבה (לא ב-Git!)
├── requirements.txt            # 📦 תלויות Python
├── README.md                   # 📖 התיעוד הזה
├── DEPLOYMENT.md              # 🚀 הוראות פריסה
└── .gitignore                 # 🚫 קבצים להתעלמות
```

---

## 🌐 API Endpoints

### 🔐 Authentication
```
POST   /api/register          - הרשמת משתמש חדש
POST   /api/login             - התחברות
GET    /api/profile           - פרופיל משתמש (JWT required)
PUT    /api/profile           - עדכון פרופיל
POST   /api/subscribe         - מנוי Premium
```

### 🔮 Predictions
```
POST   /api/predict           - תחזית יחידה
POST   /api/predict/batch     - תחזיות מרובות
POST   /api/predictions/save  - שמירת תחזית
GET    /api/predictions/history - היסטוריית תחזיות
```

### 💬 TITAN AI Chat
```
POST   /api/chat              - שליחת הודעה ל-TITAN
POST   /api/help-chat         - FAQ (ללא AI)
```

### 📊 Sports Data
```
GET    /api/today-matches     - משחקי היום
GET    /api/live-matches      - משחקים חיים
GET    /api/standings         - טבלאות ליגה
GET    /api/team-stats        - סטטיסטיקות קבוצה
```

### 📰 News
```
GET    /api/news/list         - רשימת חדשות (RSS)
POST   /api/news/refresh      - רענון ידני
```

### 🎮 Game Arena
```
POST   /api/game/submit       - שליחת תחזיות משחק
GET    /api/game/results/{id} - תוצאות משחק
```

### 💚 System
```
GET    /api/health            - בדיקת תקינות
GET    /api/status            - סטטוס מערכת
GET    /api/cache/stats       - סטטיסטיקות Cache
GET    /api/api-budget/status - סטטוס תקציב API
```

📚 **תיעוד מלא:** `http://localhost:8000/docs` (Swagger UI)

---

## 💰 עלויות

### תרחיש: 100 משתמשים פעילים ביום

| שירות | שימוש | עלות חודשית |
|-------|-------|-------------|
| **OpenAI GPT-4o** | 50 תחזיות/יום | $15-45 |
| **OpenAI GPT-4o-mini** | 100 TITAN chats | $1-3 |
| **API-Sports** | Free tier | $0 |
| **Cache saves** | -70% requests | חיסכון! |
| **RSS חדשות** | Ynet (ללא AI) | $0 |
| **Help FAQ** | ללא AI | $0 |
| **Hosting** | Render/Railway | $5-10 |

**💵 סה"כ משוער: $21-58 לחודש**

### 🎯 אופטימיזציות שביצענו:
- ✅ Cache Manager - חוסך 70-90% בקשות API
- ✅ AI Routing - חוסך 69% בעלויות AI
- ✅ RSS במקום AI - $0 לחדשות
- ✅ FAQ במקום AI - $0 לעזרה

---

## 🚀 פריסה ל-Production

ראה [DEPLOYMENT.md](DEPLOYMENT.md) להוראות מפורטות.

### אופציות Hosting מומלצות:

**1. Render.com** (מומלץ למתחילים)
- ✅ Setup פשוט
- ✅ Free tier זמין
- ✅ Auto-deploy מ-Git
- 💰 $7/חודש (Starter)

**2. Railway.app**
- ✅ Developer-friendly
- ✅ תמיכה מלאה ב-Python
- 💰 $5/חודש + שימוש

**3. Vercel + Backend נפרד**
- ✅ Frontend על Vercel (חינם!)
- ✅ Backend על Render/Railway

---

## 🧪 בדיקות

```bash
# הרצת בדיקות
pytest backend/tests/

# בדיקה עם coverage
pytest --cov=backend backend/tests/
```

---

## 📊 מדדי ביצועים

```
⚡ זמן טעינה ממוצע:     < 2 שניות
🎯 זמן תגובת API:        50-200ms
🤖 זמן תחזית AI:         3-5 שניות
💾 Hit rate של Cache:    85-90%
📰 רענון חדשות:          כל 30 דקות
```

---

## 🔒 אבטחה

- ✅ JWT Authentication
- ✅ Password Hashing (PBKDF2)
- ✅ Rate Limiting (נגד DDoS)
- ✅ CORS Middleware
- ✅ Input Validation (Pydantic)
- ✅ API Keys מוגנים (לא נחשפים לקליינט)
- ✅ HTTPS (ב-production)

---

## 🤝 תרומה לפרויקט

אנחנו מזמינים אותך לתרום!

1. Fork את הפרויקט
2. צור branch חדש (`git checkout -b feature/AmazingFeature`)
3. Commit השינויים (`git commit -m 'Add some AmazingFeature'`)
4. Push ל-branch (`git push origin feature/AmazingFeature`)
5. פתח Pull Request

---

## 📝 רישיון

פרויקט זה מוגן תחת רישיון MIT - ראה קובץ [LICENSE](LICENSE) לפרטים.

---

## 👨‍💻 מפתחים

**Rafael (osher)** - Developer & Founder
- GitHub: [@YourGitHub](https://github.com/YourGitHub)
- Email: your.email@example.com

---

## 🙏 תודות

- **OpenAI** - GPT-4o API
- **API-Sports** - נתוני ספורט
- **Ynet** - חדשות ספורט
- **FastAPI** - Web Framework מעולה
- **Claude AI** - עזרה בפיתוח

---

## 📞 צור קשר ותמיכה

- 📧 Email: support@smartsports.com
- 💬 Discord: [הצטרף לקהילה](https://discord.gg/smartsports)
- 🐛 Issues: [דווח על באג](https://github.com/YourUsername/smart_sport/issues)

---

<div align="center">

### 🌟 אם הפרויקט עזר לך, תן כוכב! ⭐

**Made with ❤️ by Rafael**

</div>
