/**
 * 🔐 בדיקת הרשאות וניהול גישה - SMARTSPORTS PAYWALL
 * משתמש חינמי = רק דף הבית
 * מנוי משלם = גישה לכל התכנים
 */

const AUTH_CONFIG = {
    FREE_PAGES: ['/', '/index.html', '/login.html', '/subscribe.html', '/about.html', '/contact.html'],
    PREMIUM_PAGES: ['/stats.html', '/predictions.html', '/titan.html', '/live.html', '/profile.html', '/game_arena.html']
};

/**
 * בדיקה האם המשתמש מחובר ובעל מנוי פעיל
 */
function checkSubscription() {
    const user = JSON.parse(localStorage.getItem('user') || 'null');
    const currentPage = window.location.pathname;

    // אם זה דף חינמי - תמיד מותר
    if (AUTH_CONFIG.FREE_PAGES.some(page => currentPage.endsWith(page) || currentPage === '/')) {
        return true;
    }

    // אם זה דף פרמיום - בדוק מנוי
    if (AUTH_CONFIG.PREMIUM_PAGES.some(page => currentPage.endsWith(page))) {
        // אם אין משתמש או אין מנוי - חסום
        if (!user || !user.subscription || user.subscription !== 'premium') {
            showPaywall();
            return false;
        }
    }

    return true;
}

/**
 * הצגת Paywall - חסימת תוכן והצגת קריאה לפעולה
 */
function showPaywall() {
    // יצירת overlay
    const overlay = document.createElement('div');
    overlay.id = 'premium-paywall';
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(10, 14, 39, 0.98);
        backdrop-filter: blur(20px);
        z-index: 999999;
        display: flex;
        align-items: center;
        justify-content: center;
        animation: fadeIn 0.5s ease-out;
    `;

    overlay.innerHTML = `
        <style>
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
            @keyframes slideUp {
                from { transform: translateY(30px); opacity: 0; }
                to { transform: translateY(0); opacity: 1; }
            }
            @keyframes glow {
                0%, 100% { box-shadow: 0 0 40px rgba(0, 255, 157, 0.4); }
                50% { box-shadow: 0 0 60px rgba(0, 255, 157, 0.6); }
            }
        </style>
        <div style="
            max-width: 600px;
            background: linear-gradient(135deg, #1a1f3a 0%, #0f1419 100%);
            border: 2px solid rgba(0, 255, 157, 0.3);
            border-radius: 24px;
            padding: 60px 40px;
            text-align: center;
            animation: slideUp 0.6s ease-out;
            position: relative;
        ">
            <!-- אייקון נעול -->
            <div style="
                width: 100px;
                height: 100px;
                margin: 0 auto 30px;
                background: linear-gradient(135deg, #00ff9d 0%, #00b8ff 100%);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 48px;
                animation: glow 2s ease-in-out infinite;
            ">
                🔒
            </div>

            <!-- כותרת -->
            <h2 style="
                font-size: 36px;
                font-weight: 800;
                background: linear-gradient(135deg, #fff 0%, #00ff9d 50%, #00b8ff 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                margin-bottom: 20px;
                font-family: 'Assistant', sans-serif;
            ">
                תוכן פרמיום בלבד
            </h2>

            <!-- תיאור -->
            <p style="
                color: rgba(255, 255, 255, 0.8);
                font-size: 18px;
                line-height: 1.6;
                margin-bottom: 40px;
                font-family: 'Assistant', sans-serif;
            ">
                תוכן זה זמין רק למנויים פרמיום.<br>
                קבל גישה בלתי מוגבלת לכל התכונות:
            </p>

            <!-- רשימת יתרונות -->
            <div style="
                text-align: right;
                margin: 30px 0;
                padding: 0 20px;
            ">
                <div style="color: #fff; margin: 15px 0; font-size: 16px; font-family: 'Assistant', sans-serif;">
                    <span style="color: #00ff9d; margin-left: 10px;">✓</span>
                    תחזיות AI מבוססות נתונים אמיתיים
                </div>
                <div style="color: #fff; margin: 15px 0; font-size: 16px; font-family: 'Assistant', sans-serif;">
                    <span style="color: #00ff9d; margin-left: 10px;">✓</span>
                    טבלאות וסטטיסטיקות מכל הליגות הבכירות
                </div>
                <div style="color: #fff; margin: 15px 0; font-size: 16px; font-family: 'Assistant', sans-serif;">
                    <span style="color: #00ff9d; margin-left: 10px;">✓</span>
                    צ'אט עם TITAN - עוזר AI מתקדם
                </div>
                <div style="color: #fff; margin: 15px 0; font-size: 16px; font-family: 'Assistant', sans-serif;">
                    <span style="color: #00ff9d; margin-left: 10px;">✓</span>
                    עדכונים חיים ומשחקי ארנה
                </div>
                <div style="color: #fff; margin: 15px 0; font-size: 16px; font-family: 'Assistant', sans-serif;">
                    <span style="color: #00ff9d; margin-left: 10px;">✓</span>
                    ניתוח עמוק של קבוצות ושחקנים
                </div>
            </div>

            <!-- כפתורים -->
            <div style="display: flex; gap: 15px; margin-top: 40px; justify-content: center;">
                <a href="/subscribe.html" style="
                    flex: 1;
                    background: linear-gradient(135deg, #00ff9d 0%, #00b8ff 100%);
                    color: #000;
                    padding: 16px 32px;
                    border-radius: 12px;
                    font-weight: 700;
                    font-size: 18px;
                    text-decoration: none;
                    display: inline-block;
                    transition: all 0.3s ease;
                    font-family: 'Assistant', sans-serif;
                    box-shadow: 0 4px 20px rgba(0, 255, 157, 0.3);
                " onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
                    🚀 הצטרף עכשיו
                </a>
                <a href="/index.html" style="
                    flex: 1;
                    background: rgba(255, 255, 255, 0.1);
                    color: #fff;
                    padding: 16px 32px;
                    border-radius: 12px;
                    font-weight: 600;
                    font-size: 18px;
                    text-decoration: none;
                    display: inline-block;
                    transition: all 0.3s ease;
                    font-family: 'Assistant', sans-serif;
                    border: 2px solid rgba(255, 255, 255, 0.2);
                " onmouseover="this.style.background='rgba(255,255,255,0.15)'" onmouseout="this.style.background='rgba(255,255,255,0.1)'">
                    חזרה לדף הבית
                </a>
            </div>

            <!-- מחיר -->
            <div style="
                margin-top: 30px;
                color: rgba(255, 255, 255, 0.6);
                font-size: 14px;
                font-family: 'Assistant', sans-serif;
            ">
                החל מ-₪49/חודש בלבד
            </div>
        </div>
    `;

    document.body.appendChild(overlay);

    // חסימת גלילה
    document.body.style.overflow = 'hidden';
}

/**
 * בדיקה אוטומטית בטעינת הדף
 */
document.addEventListener('DOMContentLoaded', () => {
    checkSubscription();
});

/**
 * פונקציה לבדיקה ידנית (לשימוש בדפים ספציפיים)
 */
function requireSubscription() {
    return checkSubscription();
}
