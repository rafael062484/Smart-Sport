const STREAK_KEY = 'smartsport_streak';
function getStreak() {
    const saved = localStorage.getItem(STREAK_KEY);
    if (\!saved) return { current: 0, best: 0, lastCompleted: null, history: [], milestones: [] };
    try { return JSON.parse(saved); } catch (e) { return { current: 0, best: 0, lastCompleted: null, history: [], milestones: [] }; }
}
function saveStreak(d) { localStorage.setItem(STREAK_KEY, JSON.stringify(d)); }
function getTodayDate() { return new Date().toISOString().split("T")[0]; }
function getYesterdayDate() { const d = new Date(); d.setDate(d.getDate() - 1); return d.toISOString().split("T")[0]; }
function getStreakDisplayText(c, a) {
    if (c === 0) return 'התחל את הרצף היום\!';
    if (\!a) return 'הרצף נשבר - התחל מחדש\!';
    if (c === 1) return '🎉 יום ראשון - זה התחלה\!';
    return '🔥 ' + c + ' ימים רצופים';
}
function getMilestoneMessage(d) {
    const m = {3:'🎉 3 ימים רצופים\! זה רק ההתחלה\!',7:'🔥 שבוע שלם\! אתה מדהים\!',14:'💪 שבועיים\! המוטיבציה גואה\!',30:'🔥 חודש שלם\! אגדה אמיתית\!',60:'👑 חודשיים\! אף אחד לא יעצור אותך\!',90:'🎉 3 חודשים\! אתה בסטייל אדיר לחלוטין\!',100:'🎉 100 ימים\! אגדה\!'};
    return m[d] || '🎉 ' + d + ' ימים רצופים\! מעולה\!';
}
function getStreakStatus() {
    const t = getTodayDate(), y = getYesterdayDate(), s = getStreak();
    const a = s.lastCompleted === t || s.lastCompleted === y;
    return {current: s.current, best: s.best, isActive: a, lastCompleted: s.lastCompleted, completedToday: s.lastCompleted === t, displayText: getStreakDisplayText(s.current, a)};
}
function updateStreak() {
    const t = getTodayDate(), s = getStreak();
    if (s.lastCompleted === t) return {success: false, streak: s};
    let n = s.lastCompleted === getYesterdayDate() ? s.current + 1 : 1;
    const b = Math.max(s.best, n);
    const m = [3,7,14,30,60,90,100].find(x => x === n && \!s.milestones.includes(x));
    const u = {current: n, best: b, lastCompleted: t, history: [...s.history, t], milestones: m ? [...s.milestones, m] : s.milestones};
    saveStreak(u);
    return {success: true, streak: u, milestone: m, message: m ? getMilestoneMessage(m) : null};
}
function resetStreak() { const s = getStreak(); const r = {current: 0, best: s.best, lastCompleted: null, history: s.history, milestones: s.milestones}; saveStreak(r); return r; }
function handleCompletion() { localStorage.setItem("smartsport_completed_today", getTodayDate()); return updateStreak(); }
window.StreakTracker = {get: getStreak, getStatus: getStreakStatus, update: updateStreak, handleCompletion: handleCompletion, reset: resetStreak};
console.log("🎯 Streak Tracker loaded");