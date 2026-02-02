"""
🆘 Support & PWA Router

אחראי על endpoints של תמיכה, עזרה, ו-PWA (Progressive Web App).

Endpoints:
---------
- POST /api/contact             → טופס יצירת קשר
- POST /api/help-chat           → Help & Education (AI-powered)
- GET  /api/predictions/latest  → תחזיות אחרונות (PWA)
- GET  /api/live/scores         → תוצאות חיות (PWA)

Created: 2026-01-10
Author: Claude Code
"""

from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, timezone
from typing import Optional

# יצירת Router
router = APIRouter(tags=["Support & PWA"])


# ═══════════════════════════════════════════════════════════════════════════════
# MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class ContactRequest(BaseModel):
    """📧 טופס יצירת קשר"""
    name: str
    email: EmailStr
    message: str


class HelpChatRequest(BaseModel):
    """🆘 בקשת עזרה"""
    message: str
    page: Optional[str] = None


class HelpChatResponse(BaseModel):
    """תשובת Help Chat"""
    answer: str


# ═══════════════════════════════════════════════════════════════════════════════
# SUPPORT ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/api/contact")
async def submit_contact(request: Request, contact: ContactRequest):
    """
    📧 טופס יצירת קשר - שליחת הודעה לתמיכה
    
    מקבל פרטי יצירת קשר ומעביר לערוץ התמיכה.
    במימוש מלא - שליחה למייל או שמירה ב-DB.
    
    Returns:
    --------
    Dict with status and message
    """
    from backend.app import logger
    
    try:
        # לוג ההודעה
        logger.info(f"📧 Contact form submission from {contact.email}")
        logger.info(f"   Name: {contact.name}")
        logger.info(f"   Message: {contact.message[:100]}...")
        
        # TODO: שליחה למייל או שמירה ב-DB
        # כרגע רק לוג - אפשר להוסיף אינטגרציה עם SendGrid/Mailgun
        
        return {
            "status": "ok",
            "message": "תודה! ההודעה התקבלה ונחזור אליך בהקדם"
        }
    except Exception as e:
        from backend.app import logger
        logger.error(f"❌ Contact form error: {e}")
        raise HTTPException(status_code=500, detail="שגיאה בשליחת ההודעה")


@router.post("/api/help-chat", response_model=HelpChatResponse)
async def help_chat(req: HelpChatRequest):
    """
    🆘 Help & Education endpoint powered by AI (TITAN-style educational mode)
    
    מספק תשובות חינוכיות ומסבירות על ספורט, AI, וניתוח משחקים.
    
    Features:
    ---------
    - AI-powered responses (OpenAI)
    - Educational tone
    - Context-aware (page parameter)
    - Fallback לתשובות מוכנות אם AI לא זמין
    
    Returns:
    --------
    HelpChatResponse with educational answer
    """
    from backend.app import OPENAI_AVAILABLE, openai_client, settings, logger
    
    system_context = f"""
    אתה TITAN AI של SMARTSPORTS.
    תפקידך להסביר, ללמד ולהנגיש ספורט ו-AI בצורה חינוכית.
    
    חוקים:
    - לא הימורים ולא המלצות הימור ישירות
    - לא כסף / לא להבטיח רווחים
    - תמיד להסביר את החשיבה, לא רק לתת תשובה
    - שפה פשוטה וברורה בעברית
    - להתייחס להקשר: דף מקור = {req.page or "general"}
    """
    
    # אם אין OpenAI – תשובת fallback חינוכית
    if not OPENAI_AVAILABLE or not openai_client:
        base_answer = (
            "מערכת ה-AI המלאה לא מחוברת כרגע, אבל אני עדיין יכול להסביר באופן כללי:\n\n"
            f"{req.message}\n\n"
            "כדי לנתח משחק/סטטיסטיקה בצורה חכמה, מתמקדים בכמה עקרונות:\n"
            "1. נתונים היסטוריים – תוצאות אחרונות, פורמה, בית/חוץ.\n"
            "2. נתונים מספריים – שערים/נקודות, xG, אחוזי החזקה בכדור.\n"
            "3. הקשר – חשיבות המשחק, עייפות, פציעות, עומס משחקים.\n"
            "4. לא לחפש ודאות של 100%, אלא הסתברות והבנה.\n\n"
            "אם תרצה, נסח את השאלה מחדש ואסביר שלב‑אחר‑שלב איך לנתח אותה."
        )
        return {"answer": base_answer}
    
    # שימוש ב-OpenAI למצב חינוכי
    try:
        response = openai_client.chat.completions.create(
            model=settings.openai_model_mini or "gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_context},
                {"role": "user", "content": req.message},
            ],
            max_tokens=700,
            temperature=0.6,
        )
        
        answer_text = (response.choices[0].message.content or "").strip()
        if not answer_text:
            answer_text = "לא הצלחתי לייצר תשובה כרגע. נסה לנסח שוב את השאלה."
        
        return {"answer": answer_text}
    
    except Exception as e:
        logger.error(f"Help chat error: {e}", exc_info=True)
        fallback = (
            "אירעה שגיאה בזמן הפעלת מנוע ה-AI.\n"
            "מומלץ לנסות שוב בעוד מספר דקות. בינתיים תוכל לחשוב כך:\n"
            "• מה הנתונים שיש לי על המשחק / המצב?\n"
            "• מה הגורמים הכי משמעותיים שמשפיעים על התוצאה?\n"
            "• איך הייתי מסביר את זה לחבר בצורה פשוטה?\n"
        )
        return {"answer": fallback}


@router.get("/api/predictions/latest")
async def get_latest_predictions(limit: int = 10):
    """
    📊 תחזיות אחרונות - לשימוש ב-PWA/Service Worker
    
    מחזיר רשימת תחזיות אחרונות עבור Progressive Web App.
    שימושי עבור notifications, offline mode, ו-background sync.
    
    Returns:
    --------
    Dict with success, predictions list, and timestamp
    """
    from backend.app import logger
    
    try:
        # TODO: שליפה מ-DB של תחזיות אחרונות
        # כרגע מחזיר mock data
        return {
            "success": True,
            "predictions": [],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Latest predictions error: {e}")
        return {"success": False, "predictions": []}


@router.get("/api/live/scores")
async def get_live_scores():
    """
    ⚡ תוצאות חיות - לשימוש ב-PWA/Service Worker
    
    מחזיר תוצאות משחקים חיות עבור Progressive Web App.
    שימושי עבור live updates, notifications, ו-background sync.
    
    Returns:
    --------
    Dict with success, scores list, and timestamp
    """
    from backend.app import logger
    
    try:
        # TODO: אינטגרציה עם Sports API לתוצאות חיות
        # כרגע מחזיר mock data
        return {
            "success": True,
            "scores": [],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Live scores error: {e}")
        return {"success": False, "scores": []}
