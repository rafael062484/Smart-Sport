/**
 * 🧪 סקריפט DEMO - להדגמת מצב משתמש ללא מנוי
 * הוסף את הסקריפט הזה ל-index.html כדי להדגים את ה-Paywall
 */

// איפוס localStorage לדמו (מחיקת מנוי אם קיים)
function setDemoMode() {
    // יצירת משתמש דמו ללא מנוי
    const demoUser = {
        username: "demo_user",
        email: "demo@smartsports.com",
        subscription: null,  // אין מנוי!
        created_at: new Date().toISOString()
    };

    localStorage.setItem('user', JSON.stringify(demoUser));
    console.log('🧪 DEMO MODE: משתמש ללא מנוי הוגדר');
    console.log('ניסיון לגשת לדפים הפרמיום יציג Paywall');
}

// יצירת משתמש פרמיום לדמו (עם מנוי)
function setPremiumMode() {
    const premiumUser = {
        username: "premium_user",
        email: "premium@smartsports.com",
        subscription: "premium",  // יש מנוי!
        subscription_expires: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(),
        created_at: new Date().toISOString()
    };

    localStorage.setItem('user', JSON.stringify(premiumUser));
    console.log('💎 PREMIUM MODE: משתמש עם מנוי הוגדר');
    console.log('גישה בלתי מוגבלת לכל הדפים');
}

// ניקוי (יציאה)
function clearUser() {
    localStorage.removeItem('user');
    console.log('🚪 משתמש הוסר - מצב אורח');
}

// הוספת כפתורים לדף הבית להדגמה
function addDemoButtons() {
    const demoPanel = document.createElement('div');
    demoPanel.style.cssText = `
        position: fixed;
        bottom: 20px;
        left: 20px;
        background: rgba(0, 0, 0, 0.9);
        border: 2px solid #00ff9d;
        border-radius: 12px;
        padding: 15px;
        z-index: 10000;
        font-family: 'Assistant', sans-serif;
        min-width: 250px;
    `;

    demoPanel.innerHTML = `
        <div style="color: #00ff9d; font-weight: 700; margin-bottom: 10px; font-size: 14px;">
            🧪 מצב הדגמה למפתח
        </div>
        <button onclick="setDemoMode(); location.reload();" style="
            background: #ff4757;
            color: #fff;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            width: 100%;
            margin-bottom: 5px;
            font-family: 'Assistant', sans-serif;
            font-weight: 600;
        ">
            🚫 משתמש חינמי
        </button>
        <button onclick="setPremiumMode(); location.reload();" style="
            background: #00ff9d;
            color: #000;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            width: 100%;
            margin-bottom: 5px;
            font-family: 'Assistant', sans-serif;
            font-weight: 600;
        ">
            💎 משתמש פרמיום
        </button>
        <button onclick="clearUser(); location.reload();" style="
            background: rgba(255, 255, 255, 0.1);
            color: #fff;
            border: 1px solid rgba(255, 255, 255, 0.3);
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            width: 100%;
            font-family: 'Assistant', sans-serif;
            font-weight: 600;
        ">
            🚪 איפוס
        </button>
        <div style="color: rgba(255,255,255,0.5); font-size: 11px; margin-top: 10px; text-align: center;">
            סטטוס: <span id="demo-status" style="color: #00ff9d; font-weight: 600;"></span>
        </div>
    `;

    document.body.appendChild(demoPanel);

    // עדכון סטטוס
    const user = JSON.parse(localStorage.getItem('user') || 'null');
    const statusEl = document.getElementById('demo-status');
    if (!user) {
        statusEl.textContent = 'אורח';
        statusEl.style.color = '#fff';
    } else if (user.subscription === 'premium') {
        statusEl.textContent = 'פרמיום';
        statusEl.style.color = '#00ff9d';
    } else {
        statusEl.textContent = 'חינמי';
        statusEl.style.color = '#ff4757';
    }
}

// הפעלה אוטומטית
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', addDemoButtons);
} else {
    addDemoButtons();
}
