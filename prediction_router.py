"""
🧠 Prediction Router - AI-Powered Match Predictions

מטפל בכל endpoints של תחזיות AI:
- POST /api/predict        → תחזית יחידה מפורטת
- POST /api/predict/batch  → תחזיות מרובות
- POST /api/predict/compare→ השוואת קבוצות

Created: 2026-01-24
Author: Claude Code & Rafael
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import logging

# יצירת Router
router = APIRouter(tags=["AI Predictions"])

# הגדרת לוגר
logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class PredictRequest(BaseModel):
    """📊 בקשת תחזית יחידה"""
    home: str = Field(..., description="קבוצה ביתית", min_length=2)
    away: str = Field(..., description="קבוצה אורחת", min_length=2)
    league: str = Field(default="General", description="ליגה")
    depth: str = Field(default="standard", pattern="^(quick|standard|deep|expert)$")
    match_date: Optional[str] = Field(None, description="תאריך המשחק (YYYY-MM-DD)")


class BatchPredictRequest(BaseModel):
    """📊 בקשת תחזיות מרובות"""
    matches: List[Dict[str, str]] = Field(..., description="רשימת משחקים")
    depth: str = Field(default="quick", pattern="^(quick|standard|deep|expert)$")


class CompareRequest(BaseModel):
    """📊 בקשת השוואה"""
    team1: str = Field(..., description="קבוצה 1")
    team2: str = Field(..., description="קבוצה 2")
    league: str = Field(default="General", description="ליגה")


# ═══════════════════════════════════════════════════════════════════════════════
# PREDICTION ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/api/predict")
async def predict_match(request: PredictRequest):
    """
    🎯 תחזית AI מפורטת למשחק בודד

    מקבל:
    - קבוצה ביתית ואורחת
    - ליגה (אופציונלי)
    - רמת עומק (quick/standard/deep/expert)
    - תאריך משחק (אופציונלי)

    מחזיר:
    - תחזית מפורטת עם ניתוח
    - אחוזי ניצחון
    - תוצאה צפויה
    - נימוקים
    """
    try:
        from backend.app import AI_ENGINE_LOADED, get_match_prediction, logger as app_logger

        if not AI_ENGINE_LOADED:
            return {
                "success": False,
                "error": "AI Engine not available",
                "fallback_prediction": {
                    "home_team": request.home,
                    "away_team": request.away,
                    "predicted_result": "Demo Mode - AI disabled",
                    "confidence": 0,
                    "analysis": "מנוע ה-AI לא זמין כרגע. אנא נסה שוב מאוחר יותר או פנה לתמיכה."
                }
            }

        # קריאה למנוע ה-AI
        result = await get_match_prediction(
            home_team=request.home,
            away_team=request.away,
            league=request.league,
            analysis_depth=request.depth.upper(),
            match_date=request.match_date
        )

        if result and result.get("success"):
            return {
                "success": True,
                "prediction": result.get("prediction", {}),
                "timestamp": result.get("timestamp"),
                "engine_version": result.get("engine_version")
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Failed to generate prediction")
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"שגיאה ביצירת תחזית: {str(e)}")


@router.post("/api/predict/batch")
async def predict_batch(request: BatchPredictRequest):
    """
    🎯 תחזיות AI לכמה משחקים בו-זמנית

    מקבל:
    - רשימת משחקים (עד 10)
    - רמת עומק

    מחזיר:
    - רשימת תחזיות
    - סיכום
    """
    try:
        from backend.app import AI_ENGINE_LOADED, analyze_batch, logger as app_logger

        if not AI_ENGINE_LOADED:
            # Fallback למצב דמו
            demo_predictions = []
            for match in request.matches[:4]:  # מקסימום 4
                demo_predictions.append({
                    "success": False,
                    "home_team": match.get("home", "Unknown"),
                    "away_team": match.get("away", "Unknown"),
                    "error": "AI Engine not available - Demo mode"
                })

            return {
                "success": False,
                "predictions": demo_predictions,
                "total": len(demo_predictions),
                "message": "מנוע ה-AI לא זמין"
            }

        # הגבלה ל-10 משחקים
        matches_to_analyze = request.matches[:10]

        # קריאה למנוע ה-AI
        results = await analyze_batch(
            matches=matches_to_analyze,
            analysis_depth=request.depth.upper()
        )

        if results:
            return {
                "success": True,
                "predictions": results,
                "total": len(results),
                "depth": request.depth
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to generate batch predictions")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Batch prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"שגיאה בתחזיות מרובות: {str(e)}")


@router.post("/api/predict/compare")
async def compare_teams(request: CompareRequest):
    """
    ⚖️ השוואת שתי קבוצות

    מקבל:
    - שתי קבוצות
    - ליגה

    מחזיר:
    - השוואה מפורטת
    - סטטיסטיקות
    - ניתוח כוחות
    """
    try:
        from backend.app import AI_ENGINE_LOADED, get_comparison, logger as app_logger

        if not AI_ENGINE_LOADED:
            return {
                "success": False,
                "error": "AI Engine not available",
                "message": "מנוע ה-AI לא זמין כרגע"
            }

        # קריאה למנוע ה-AI
        result = await get_comparison(
            team1=request.team1,
            team2=request.team2,
            league=request.league
        )

        if result:
            return {
                "success": True,
                "comparison": result
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to generate comparison")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Comparison error: {e}")
        raise HTTPException(status_code=500, detail=f"שגיאה בהשוואה: {str(e)}")
