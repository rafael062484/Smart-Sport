// ═══════════════════════════════════════════════════════════════════
// 🚀 AI ASSISTANT POPUP - פונקציות אינטראקטיביות
// ═══════════════════════════════════════════════════════════════════

// הודעות טעינה אישיות ומצחיקות
const aiLoadingMessages = [
    'אוקיי, תן לי שנייה... 🧠',
    'קורא נתונים מהענן ☁️',
    'מדבר עם GPT-4o 🤖',
    'עוצם עיניים וחושב 🤔',
    'שואל את המומחים שלי ⚡',
    'בודק מי שיחק טוב לאחרונה 📊',
    'כמעט סיימתי... 💫',
    'בום! מוכן! 🔥'
];

// הודעות פתיחה מגוונות
const aiWelcomeMessages = [
    'רגע... אני מזהה שאתה כאן בפעם הראשונה! 🎉<br><strong>תן לי להראות לך משהו מדהים</strong> שיסביר למה משקיעים משקיעים מיליונים בנו 🚀',
    'היי שם! 👋 אני TITAN, ובאתי להפוך אותך למומחה תחזיות!<br><strong>בוא נראה איך זה עובד</strong> - זה יקח רק 10 שניות 🎯',
    'וואו, משתמש חדש! 🎊<br>אני כאן כדי <strong>להראות לך את העתיד של תחזיות ספורט</strong>. מוכן להתרשם? 🚀'
];

// הודעות מצחיקות מתחלפות
const aiFunnyMessages = [
    '🎭 כן כן, אני לא מנבא לוטו... אבל בכדורגל? 👑 אלוף עולם!',
    '💡 טיפ: תגיד "וואו" בקול רם כשתראה את התחזית. זה משפר את הדיוק! 😄',
    '🤖 אני AI, אבל אל תדאג - אני לא שולט בעולם. רק בכדורגל 😉',
    '⚽ העבודה שלי? להפוך אותך למלך התחזיות! המשכורת שלי? ביטחון שלך 💪',
    '🎯 משקיעים שאלו: "למה להשקיע בכם?" אמרתי: "תראו דמו". עכשיו הם פה! 🔥'
];

let aiLoadingInterval = null;
let aiFunnyInterval = null;

// פתיחת הפופאפ עם אפקטים
function openAiPopup() {
    // 🚀 TITAN: פותח AI Popup
    const overlay = document.getElementById('aiPopupOverlay');
    if (overlay && overlay.classList) {
        overlay.classList.add('show');
    } else {
        console.warn('AI Popup overlay element not found (aiPopupOverlay)');
        return; // אין טעם להמשיך בלי אלמנט הבסיס
    }

    // הודעת פתיחה רנדומלית
    const welcomeMsg = aiWelcomeMessages[Math.floor(Math.random() * aiWelcomeMessages.length)];
    const welcomeEl = document.getElementById('aiWelcomeMessage');
    if (welcomeEl) welcomeEl.innerHTML = welcomeMsg;

    // שינוי הודעה מצחיקה כל 5 שניות
    const funnyEl = document.getElementById('funnyMessage');
    if (funnyEl) {
        aiFunnyInterval = setInterval(() => {
            const funnyMsg = aiFunnyMessages[Math.floor(Math.random() * aiFunnyMessages.length)];
            funnyEl.innerHTML = funnyMsg;
        }, 5000);
    }

    // אפקט קונפטי עדין
    setTimeout(() => {
        if (typeof confetti === 'function') {
            confetti({
                particleCount: 40,
                spread: 55,
                origin: { y: 0.4 },
                colors: ['#8b5cf6', '#3b82f6', '#10b981', '#fbbf24']
            });
        }
    }, 300);

    // ברכה דינמית לפי שעה
    updateAiGreeting();

    // לוג
    if (typeof termLog === 'function') {
        termLog('👋 TITAN אומר שלום...', 'ai');
    }
}

// עדכון ברכה לפי שעה
function updateAiGreeting() {
    const hour = new Date().getHours();
    let greeting = 'היי! אני TITAN 👋';

    if (hour >= 5 && hour < 12) {
        greeting = 'בוקר טוב! אני TITAN ☀️';
    } else if (hour >= 12 && hour < 17) {
        greeting = 'צהריים טובים! אני TITAN 👋';
    } else if (hour >= 17 && hour < 21) {
        greeting = 'ערב טוב! אני TITAN 🌆';
    } else {
        greeting = 'לילה טוב! אני TITAN 🌙';
    }

    const greetingEl = document.getElementById('aiGreeting');
    if (greetingEl) greetingEl.textContent = greeting;
}

// סגירת הפופאפ
function closeAiPopup() {
    const overlay = document.getElementById('aiPopupOverlay');
    if (overlay && overlay.classList) {
        overlay.classList.remove('show');
    }

    const resultDiv = document.getElementById('aiPopupResult');
    if (resultDiv) resultDiv.style.display = 'none';

    const loaderDiv = document.getElementById('aiPopupLoading');
    if (loaderDiv) loaderDiv.classList.remove('active');

    if (aiLoadingInterval) {
        clearInterval(aiLoadingInterval);
        aiLoadingInterval = null;
    }

    if (aiFunnyInterval) {
        clearInterval(aiFunnyInterval);
        aiFunnyInterval = null;
    }

    if (typeof termLog === 'function') {
        termLog('להתראות! TITAN נסגר 👋', 'text');
    }
}

// הצגת טוען אינטראקטיבי
function showPopupLoading(show = true) {
    const loader = document.getElementById('aiPopupLoading');
    const loadingText = document.getElementById('aiLoadingText');

    if (!loader || !loadingText) return;

    if (show) {
        loader.classList.add('active');
        let msgIndex = 0;
        loadingText.textContent = aiLoadingMessages[msgIndex];

        // שינוי הודעת טעינה כל 1.2 שניות
        aiLoadingInterval = setInterval(() => {
            msgIndex = (msgIndex + 1) % aiLoadingMessages.length;
            loadingText.textContent = aiLoadingMessages[msgIndex];
        }, 1200);
    } else {
        loader.classList.remove('active');
        if (aiLoadingInterval) {
            clearInterval(aiLoadingInterval);
            aiLoadingInterval = null;
        }
    }
}

// ═══════════════════════════════════════════════════════════════════
// 🎯 SURPRISE PREDICTION - הפתעת תחזית
// ═══════════════════════════════════════════════════════════════════
async function surpriseMePrediction() {
    // 🎯 TITAN: הפתע אותי בתחזית
    const resultDiv = document.getElementById('aiPopupResult');
    if (!resultDiv) {
        console.error('❌ TITAN: לא מצאתי את aiPopupResult!');
        return;
    }

    // הסתר המלצות, הצג טוען
    const suggestionsEl = document.getElementById('aiSuggestions');
    if (suggestionsEl) suggestionsEl.style.display = 'none';

    // אם יש פונקציה גלובלית לתחזית (מוגדרת ב-predictions.html)
    if (typeof getAiPopupPrediction === 'function') {
        await getAiPopupPrediction();
    } else {
        // אם אין, עשה mock תחזית
        showPopupLoading(true);
        setTimeout(() => {
            showPopupLoading(false);

            const mockTeams = [
                { home: 'ריאל מדריד', away: 'ברצלונה', score: '2-1', conf: 78 },
                { home: 'מנצ\'סטר סיטי', away: 'ליברפול', score: '3-2', conf: 82 },
                { home: 'באיירן מינכן', away: 'דורטמונד', score: '2-0', conf: 75 },
                { home: 'פ.ס.ז\'', away: 'מרסיי', score: '3-1', conf: 80 },
                { home: 'יובנטוס', away: 'אינטר', score: '1-1', conf: 71 }
            ];

            const match = mockTeams[Math.floor(Math.random() * mockTeams.length)];

            resultDiv.innerHTML = `
                <div style="text-align: center; padding: 18px; background: linear-gradient(135deg, rgba(16,185,129,0.15), rgba(59,130,246,0.1)); border: 2px solid rgba(16,185,129,0.3); border-radius: 14px; animation: resultPop 0.5s ease;">
                    <div style="font-size: 28px; margin-bottom: 12px;">🎉</div>
                    <h3 style="font-size: 17px; color: #fbbf24; margin-bottom: 12px; font-weight: 900;">הפתעה! תחזית טרייה!</h3>

                    <div style="margin: 15px 0;">
                        <div style="font-size: 15px; font-weight: 800; color: #e2e8f0; margin-bottom: 8px;">
                            ${match.home} <span style="color: rgba(226, 232, 240, 0.5);">vs</span> ${match.away}
                        </div>
                        <div style="font-size: 32px; font-weight: 900; background: linear-gradient(135deg, #3b82f6, #8b5cf6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 10px 0;">
                            ${match.score}
                        </div>
                    </div>

                    <div style="display: flex; justify-content: center; gap: 15px; margin: 15px 0; font-size: 12px;">
                        <div>
                            <div style="color: rgba(226, 232, 240, 0.6);">ביטחון AI</div>
                            <div style="font-size: 20px; font-weight: 800; color: ${match.conf > 75 ? '#10b981' : '#f59e0b'};">
                                ${match.conf}%
                            </div>
                        </div>
                        <div>
                            <div style="color: rgba(226, 232, 240, 0.6);">מנוע</div>
                            <div style="font-size: 11px; font-weight: 700; color: #8b5cf6; margin-top: 4px;">
                                🤖 TITAN
                            </div>
                        </div>
                    </div>

                    <div style="margin-top: 15px; padding: 12px; background: rgba(251,191,36,0.1); border-radius: 10px; border: 1px solid rgba(251,191,36,0.2);">
                        <div style="font-size: 11px; color: #e2e8f0; line-height: 1.6;">
                            😎 <strong>וואו!</strong> זה מה שקורה כשמשלבים AI עם כדורגל!<br>
                            💪 רוצה עוד תחזית? <span onclick="surpriseMePrediction()" style="color: #fbbf24; cursor: pointer; text-decoration: underline;">לחץ כאן!</span>
                        </div>
                    </div>
                </div>
            `;
            resultDiv.style.display = 'block';

            // קונפטי!
            if (typeof confetti === 'function') {
                confetti({
                    particleCount: 100,
                    spread: 70,
                    origin: { y: 0.6 },
                    colors: ['#10b981', '#3b82f6', '#8b5cf6', '#fbbf24']
                });
            }

            if (typeof termLog === 'function') {
                termLog(`🎉 הפתעה! ${match.home} vs ${match.away} → ${match.score}`, 'success');
            }
        }, 2000);
    }
}

// ═══════════════════════════════════════════════════════════════════
// 🔥 TOP MATCHES - משחקים חמים
// ═══════════════════════════════════════════════════════════════════
function showTopMatches() {
    // 🔥 TITAN: מה חם היום
    const resultDiv = document.getElementById('aiPopupResult');
    if (!resultDiv) {
        console.error('❌ TITAN: לא מצאתי את aiPopupResult!');
        return;
    }

    // הסתר המלצות
    const suggestionsEl = document.getElementById('aiSuggestions');
    if (suggestionsEl) suggestionsEl.style.display = 'none';

    const hotMatches = [
        { home: 'ריאל מדריד', away: 'ברצלונה', league: 'LaLiga', time: '20:00', hot: 98 },
        { home: 'מנצ\'סטר סיטי', away: 'ארסנל', league: 'Premier League', time: '18:30', hot: 95 },
        { home: 'באיירן', away: 'דורטמונד', league: 'Bundesliga', time: '19:30', hot: 92 },
        { home: 'פ.ס.ז\'', away: 'מרסיי', league: 'Ligue 1', time: '21:00', hot: 88 }
    ];

    let matchesHTML = hotMatches.map((m, i) => `
        <div style="background: rgba(139,92,246,0.08); border: 1px solid rgba(139,92,246,0.2); border-radius: 10px; padding: 12px; margin-bottom: 8px; cursor: pointer; transition: all 0.3s;"
             onmouseover="this.style.background='rgba(139,92,246,0.15)'; this.style.transform='translateX(-3px)'"
             onmouseout="this.style.background='rgba(139,92,246,0.08)'; this.style.transform='translateX(0)'"
             onclick="surpriseMePrediction()">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="flex: 1;">
                    <div style="font-size: 13px; font-weight: 800; color: #e2e8f0; margin-bottom: 4px;">
                        ${m.home} <span style="color: rgba(226, 232, 240, 0.4);">vs</span> ${m.away}
                    </div>
                    <div style="font-size: 10px; color: rgba(226, 232, 240, 0.6);">
                        ${m.league} • ${m.time}
                    </div>
                </div>
                <div style="text-align: center; margin-left: 10px;">
                    <div style="font-size: 20px; margin-bottom: 2px;">🔥</div>
                    <div style="font-size: 11px; font-weight: 700; color: #fbbf24;">
                        ${m.hot}%
                    </div>
                </div>
            </div>
        </div>
    `).join('');

    resultDiv.innerHTML = `
        <div style="padding: 15px; background: linear-gradient(135deg, rgba(239,68,68,0.1), rgba(251,191,36,0.08)); border: 2px solid rgba(239,68,68,0.25); border-radius: 14px;">
            <h3 style="font-size: 17px; color: #fbbf24; margin-bottom: 12px; font-weight: 900; text-align: center;">
                🔥 המשחקים החמים של היום!
            </h3>

            <div style="margin: 12px 0;">
                ${matchesHTML}
            </div>

            <div style="margin-top: 15px; padding: 12px; background: rgba(0,0,0,0.3); border-radius: 10px; text-align: center;">
                <div style="font-size: 11px; color: #e2e8f0; line-height: 1.6;">
                    💡 <strong>טיפ:</strong> לחץ על משחק כדי לקבל תחזית מלאה!<br>
                    😉 ככה משקיעים יודעים מה חם ומה לא...
                </div>
            </div>
        </div>
    `;
    resultDiv.style.display = 'block';

    if (typeof termLog === 'function') {
        termLog('🔥 מציג משחקים חמים...', 'ai');
    }
}

// אתחול הפופאפ כשהדף נטען
document.addEventListener('DOMContentLoaded', () => {
    // הצגת AI Popup אחרי 3 שניות (אם הפונקציה קיימת)
    if (typeof openAiPopup === 'function') {
        setTimeout(() => {
            // openAiPopup(); // הוסר כדי לא להפעיל אוטומטית
        }, 3000);
    }
});
