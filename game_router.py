"""
🎮 Game Engine Router

אחראי על endpoints של משחק התחזיות מול AI.

Endpoints:
---------
- POST /game/submit           → שליחת תחזיות משחק
- GET  /game/results/{id}     → קבלת תוצאות משחק

Created: 2026-01-09
Author: Claude Code
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from datetime import datetime
import secrets

# יצירת Router
router = APIRouter(tags=["Game"])

# אחסון sessions במטמון (בפרודקשן - להעביר ל-Redis/DB)
game_sessions: Dict[str, Dict] = {}


# ═══════════════════════════════════════════════════════════════════════════════
# GAME ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/game/submit")
async def submit_game_predictions(data: Dict[str, Any]):
    """
    🎮 שליחת תחזיות משחק
    
    תהליך:
    -------
    1. קבלת רשימת משחקים ותחזיות משתמש
    2. יצירת תחזיות AI (או fallback לrandom)
    3. שמירת session
    4. החזרת session_id ותחזיות AI
    
    Input:
    ------
    - matches: רשימת משחקים
    - predictions: תחזיות המשתמש {match_id: "home"/"draw"/"away"}
    
    Returns:
    --------
    Dict with session_id and ai_predictions
    """
    from backend.app import logger
    
    matches = data.get("matches", [])
    user_predictions = data.get("predictions", {})
    
    if not matches or not user_predictions:
        raise HTTPException(status_code=400, detail="Missing matches or predictions")
    
    # Generate AI predictions
    try:
        from backend.game_engine import ai_generate_predictions
        ai_predictions_list = await ai_generate_predictions(matches)
        ai_predictions = {match["id"]: pred for match, pred in zip(matches, ai_predictions_list)}
    except Exception as e:
        logger.warning(f"AI prediction failed: {e}, using random predictions")
        import random
        ai_predictions = {match["id"]: random.choice(["home", "draw", "away"]) for match in matches}
    
    # Generate session ID
    session_id = secrets.token_urlsafe(16)
    
    # Store session
    game_sessions[session_id] = {
        "matches": matches,
        "user_predictions": user_predictions,
        "ai_predictions": ai_predictions,
        "created_at": datetime.now().isoformat()
    }
    
    return {
        "success": True,
        "session_id": session_id,
        "ai_predictions": ai_predictions
    }


@router.get("/game/results/{session_id}")
async def get_game_results(session_id: str):
    """
    🏆 קבלת תוצאות משחק
    
    תהליך:
    -------
    1. מציאת session
    2. יצירת/קבלת תוצאות אמיתיות
    3. חישוב ניקוד משתמש vs AI
    4. בניית תגובה מפורטת
    
    Returns:
    --------
    Dict with user_score, ai_score, and detailed predictions
    """
    if session_id not in game_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = game_sessions[session_id]
    matches = session["matches"]
    user_preds = session["user_predictions"]
    ai_preds = session["ai_predictions"]
    
    # Generate random results (במציאות - תוצאות אמיתיות מ-API)
    import random
    results = {match["id"]: random.choice(["home", "draw", "away"]) for match in matches}
    
    # Calculate scores
    user_score = sum(1 for match_id, pred in user_preds.items() if pred == results.get(match_id))
    ai_score = sum(1 for match_id, pred in ai_preds.items() if pred == results.get(match_id))
    
    # Build response
    predictions = []
    for match in matches:
        match_id = match["id"]
        predictions.append({
            "match": match,
            "user_pick": user_preds.get(match_id),
            "ai_pick": ai_preds.get(match_id),
            "result": results.get(match_id),
            "user_correct": user_preds.get(match_id) == results.get(match_id),
            "ai_correct": ai_preds.get(match_id) == results.get(match_id)
        })
    
    return {
        "success": True,
        "user_score": user_score,
        "ai_score": ai_score,
        "predictions": predictions
    }
