# 🔐 מדריך מערכת PAYWALL - SMARTSPORTS

## 📋 סקירה כללית

המערכת כעת כוללת **Paywall מלא** - משתמשים חינמיים רואים רק את דף הבית, ורק מנויים פרמיום יכולים לגשת לכל התכנים.

---

## 🎯 איך זה עובד?

### **1. דפים חופשיים (Free Pages)**
משתמשים יכולים לגשת ללא מנוי:
- ✅ `/index.html` - דף הבית
- ✅ `/login.html` - התחברות
- ✅ `/subscribe.html` - מנויים
- ✅ `/about.html` - אודות
- ✅ `/contact.html` - צור קשר

### **2. דפים פרמיום (Premium Pages)**
דורשים מנוי פעיל:
- 🔒 `/stats.html` - סטטיסטיקות וטבלאות
- 🔒 `/predictions.html` - תחזיות AI
- 🔒 `/titan.html` - צ'אט עם TITAN
- 🔒 `/live.html` - משחקים חיים
- 🔒 `/profile.html` - פרופיל משתמש
- 🔒 `/game_arena.html` - משחקים וארנה

---

## 🛠️ מערכת הקבצים

### **`auth-check.js`** - לוגיקת ה-Paywall
```javascript
// בדיקה אוטומטית בכל דף
checkSubscription() → true/false

// אם אין מנוי → מציג Paywall
showPaywall() → מסך חסימה מלא עם קריאה לפעולה
```

**המערכת בודקת:**
1. האם המשתמש מחובר? (`localStorage.getItem('user')`)
2. האם יש לו מנוי? (`user.subscription === 'premium'`)
3. אם לא → חוסם גישה ומציג overlay

---

## 🧪 בדיקה והדגמה

### **דרך 1: הוספת demo-user.js לדף הבית**

הוסף ל-`index.html` לפני `</body>`:
```html
<script src="demo-user.js"></script>
```

זה יוסיף פאנל בפינה השמאלית התחתונה עם 3 כפתורים:
- 🚫 **משתמש חינמי** - ינסה לגשת לדפים → יראה Paywall
- 💎 **משתמש פרמיום** - גישה בלתי מוגבלת
- 🚪 **איפוס** - מצב אורח

### **דרך 2: קונסול דפדפן**

פתח Console (F12) והקלד:
```javascript
// הפוך למשתמש חינמי
localStorage.setItem('user', JSON.stringify({
    username: "test",
    subscription: null
}));

// הפוך למשתמש פרמיום
localStorage.setItem('user', JSON.stringify({
    username: "premium",
    subscription: "premium"
}));

// איפוס
localStorage.removeItem('user');

// רענן את הדף
location.reload();
```

---

## 🎨 התאמה אישית

### **שינוי עיצוב ה-Paywall**
ערוך את `auth-check.js` → פונקציה `showPaywall()`:
```javascript
// שנה צבעים, טקסטים, סגנון
overlay.innerHTML = `...`
```

### **שינוי מחיר המנוי**
ערוך ב-2 מקומות:
1. **`auth-check.js`** - שורה: `"החל מ-₪49/חודש בלבד"`
2. **`index.html`** - CTA Banner: `"החל מ-₪49/חודש"`

### **הוספת דפים נוספים ל-Paywall**
ערוך `auth-check.js`:
```javascript
const AUTH_CONFIG = {
    PREMIUM_PAGES: ['/new-page.html', ...]  // הוסף כאן
};
```

---

## 👨‍💻 למפתח: גישה בלתי מוגבלת

אתה כמפתח יש לך 2 אפשרויות:

### **אפשרות 1: ללא בדיקה (מומלץ לפיתוח)**
הסר את `auth-check.js` זמנית מה-HTML:
```html
<!-- <script src="auth-check.js"></script> -->
```

### **אפשרות 2: הגדר עצמך כפרמיום**
הרץ בקונסול:
```javascript
localStorage.setItem('user', JSON.stringify({
    username: "developer",
    email: "dev@smartsports.com",
    subscription: "premium",
    subscription_expires: "2099-12-31",
    role: "admin"
}));
location.reload();
```

---

## 💰 ניהול מנויים (Backend)

### **מבנה משתמש ב-localStorage:**
```javascript
{
    "username": "string",
    "email": "string",
    "subscription": "premium" | null,
    "subscription_expires": "ISO_DATE",
    "created_at": "ISO_DATE"
}
```

### **TODO: חיבור לתשלום אמיתי**
עתיד להוסיף:
1. **Stripe / PayPal** - עיבוד תשלומים
2. **Webhook** - עדכון סטטוס מנוי
3. **Backend endpoint** - אימות מנוי מול שרת
4. **JWT Token** - במקום localStorage

---

## 📊 סטטיסטיקות שימוש

### **בדיקה כמה משתמשים יש:**
```javascript
// ב-Console
console.log(localStorage.getItem('user'));
```

### **ניטור ניסיונות גישה:**
הוסף ל-`auth-check.js`:
```javascript
if (!user || !user.subscription) {
    // שלח לוג לשרת
    fetch('/api/log-paywall-block', {
        method: 'POST',
        body: JSON.stringify({ page: window.location.pathname })
    });
}
```

---

## 🔥 טיפים חשובים

1. **בדיקה לפני השקה:**
   - נסה כל דף כמשתמש חינמי
   - ודא ש-Paywall מוצג כהלכה
   - בדוק שכפתור "הצטרף עכשיו" עובד

2. **SEO:**
   - דפים פרמיום עדיין זמינים לבוטים של Google
   - שקול להוסיף `<meta name="robots" content="noindex">` לדפים פרמיום

3. **ביצועים:**
   - `auth-check.js` קל מאוד (< 5KB)
   - בדיקה מתבצעת רק פעם אחת בטעינת דף

---

## 🎉 סיכום

✅ **מערכת Paywall פעילה ועובדת**
✅ **משתמש חינמי = דף הבית בלבד**
✅ **משתמש פרמיום = כל התכנים**
✅ **מפתח = גישה מלאה (עם ההגדרות הנכונות)**

**השרת רץ על:** `http://localhost:8000`

**לבדיקה מהירה:**
1. פתח `http://localhost:8000/index.html`
2. לחץ על "סטטיסטיקות & טבלאות"
3. תראה Paywall! 🔒

---

**נוצר ב-27/01/2026 | SMARTSPORTS PREMIUM PAYWALL SYSTEM**
