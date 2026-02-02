"""

                                                                                      
               SMARTSPORTS PREDICTIONS API v9.0 - TITAN ULTIMATE                    
                                                                                      
                     למבורגיני + פרארי: API התחזיות                               
                                                                                      



 מה זה PREDICTIONS API?


זה ה**Router** שמחבר בין הפרונטאנד למנוע AI Predictor!
כל בקשת תחזית עוברת דרך הקובץ הזה.

 Endpoints זמינים:



 POST /api/predict                    תחזית יחידה פשוטה (מהיר)                  
 POST /api/predict/single             תחזית יחידה מפורטת (מומלץ!)               
 POST /api/predict/batch              תחזיות מרובות - עד 4 (כלכלי)              
 POST /api/predict/compare            השוואה בין קבוצות                          
 GET  /api/predict/options            אפשרויות וסטטוס                            
 GET  /api/engine/stats               סטטיסטיקות מנוע                            
 GET  /api/teams                      רשימת קבוצות נתמכות                       



 למבורגיני + פרארי: כללי זהב



  אזורים אסורים - אל תגע!                                                        

                                                                                     
 1⃣ הייבוא מ-ai_predictor (שורות 33-56)                                            
    → חיבור למנוע AI                                                                
    → אם תשנה: התחזיות ייפסקו!                                                   
                                                                                     
 2⃣ הגדרות Router (שורות 65-69)                                                    
    → router = APIRouter(tags=["Predictions"])                                      
    → limiter = Limiter(...)                                                        
    → שינוי = בעיות routing!                                                      
                                                                                     
 3⃣ Pydantic Models (שורות 76-170)                                                 
    → הגדרות המבנה של הבקשות                                                       
    → שינוי = validation errors!                                                  
                                                                                     



  אזורים מותרים - אפשר לשנות!                                                    

                                                                                     
 1⃣ Rate Limits (בכל endpoint)                                                     
    → @limiter.limit("30/minute")                                                    
    → אפשר להגדיל/להקטין לפי צורך                                                  
    → דוגמה: "50/minute" ליותר תנועה                                                
                                                                                     
 2⃣ הוספת Endpoints חדשים                                                          
    → אפשר להוסיף endpoints נוספים                                                 
    → שמור על המבנה הקיים!                                                          
                                                                                     
 3⃣ Background Tasks                                                                
    → אפשר להוסיף משימות ברקע                                                      
    → לוגים, שמירה, וכו'                                                           
                                                                                     



 טיפים לסטודנט סטארט-אפ


1.  ניטור תחזיות:
   - כל תחזית נרשמת בלוג
   - ניתן לעקוב אחרי דיוק
   - רואים עלויות בזמן אמת

2.  Rate Limiting:
   - מגן מפני spam
   - שומר על תקציב OpenAI
   - מאפשר שירות הוגן לכולם

3.  ביצועים:
   - Background tasks לפעולות כבדות
   - Validation מהירה בpydantic
   - Error handling מלא

4.  עלויות:
   - תחזית פשוטה: ~$0.01
   - תחזית מפורטת: ~$0.015
   - batch של 4: ~$0.03
   - צפי לחודש: users × תחזיות/יום × $0.01


© 2024-2025 SMARTSPORTS - Revolutionary AI Sports Platform

"""

import sys
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, BackgroundTasks, HTTPException, Query, Request
from fastapi.responses import ORJSONResponse
from pydantic import BaseModel, Field, model_validator
from slowapi import Limiter
from slowapi.util import get_remote_address

# תיקון נתיבים
CURRENT_DIR = Path(__file__).resolve().parent
ROOT_DIR = CURRENT_DIR.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

# ייבוא המנוע
try:
    from backend.ai_predictor import (
        get_match_prediction,
        analyze_match,
        analyze_batch,
        get_comparison,
        ai_engine,
        get_engine_stats,
        get_engine_version,
        is_ai_online,
        get_supported_sports
    )
except ImportError:
    from ai_predictor import (
        get_match_prediction,
        analyze_match,
        analyze_batch,
        get_comparison,
        ai_engine,
        get_engine_stats,
        get_engine_version,
        is_ai_online,
        get_supported_sports
    )

# ייבוא TITAN Standard Mode
try:
    from backend.ai_predictor_titan import (
        get_match_prediction as get_titan_prediction,
        get_engine_version as get_titan_version,
        is_ai_online as is_titan_online
    )
    TITAN_AVAILABLE = True
except ImportError:
    try:
        from ai_predictor_titan import (
            get_match_prediction as get_titan_prediction,
            get_engine_version as get_titan_version,
            is_ai_online as is_titan_online
        )
        TITAN_AVAILABLE = True
    except ImportError:
        TITAN_AVAILABLE = False

# ייבוא Data Manager (אופציונלי)
try:
    from data_manager import TeamDataManager
    data_manager = TeamDataManager()
except ImportError:
    data_manager = None

# יצירת ה-router - פעם אחת בלבד!
router = APIRouter(tags=["Predictions"])


# ═══════════════════════════════════════════════════════════════════════════════
# Shared Validator - DRY principle
# ═══════════════════════════════════════════════════════════════════════════════

def normalize_team_field_names(data):
    """
    Shared validator: Normalize team1/team2 to home/away
    Used across multiple Pydantic models to avoid code duplication
    """
    if isinstance(data, dict):
        if 'team1' in data and 'home' not in data:
            data['home'] = data.pop('team1')
        if 'team2' in data and 'away' not in data:
            data['away'] = data.pop('team2')
    return data

# הוספת limiter
limiter = Limiter(key_func=get_remote_address)


# 
# PYDANTIC MODELS
# 

class PredictionRequest(BaseModel):
    """בקשת תחזית בסיסית - תומך גם ב-team1/team2 וגם ב-home/away"""
    home: str = Field(..., description="קבוצה מארחת")
    away: str = Field(..., description="קבוצה אורחת")
    league: str = Field(default="ליגת העל", description="שם הליגה")
    use_live_data: bool = Field(default=True, description="שימוש בנתונים חיים")

    class Config:
        populate_by_name = True

    @model_validator(mode='before')
    @classmethod
    def normalize_team_names(cls, data):
        return normalize_team_field_names(data)


class SinglePredictionRequest(BaseModel):
    """בקשת תחזית יחידה מפורטת - תומך גם ב-team1/team2 וגם ב-home/away"""
    home: str = Field(..., description="קבוצה מארחת")
    away: str = Field(..., description="קבוצה אורחת")
    league: str = Field(default="General", description="שם הליגה")
    depth: str = Field(default="deep", description="עומק ניתוח: quick/standard/deep/expert")
    include_h2h: bool = Field(default=True, description="כלול היסטוריית מפגשים")
    include_momentum: bool = Field(default=True, description="כלול נתוני מומנטום")
    include_extended_stats: bool = Field(default=True, description="כלול סטטיסטיקות מורחבות")
    include_recommendations: bool = Field(default=True, description="כלול המלצות")
    user_id: Optional[str] = Field(default=None, description="מזהה משתמש")

    class Config:
        populate_by_name = True

    @model_validator(mode='before')
    @classmethod
    def normalize_team_names(cls, data):
        return normalize_team_field_names(data)


class MatchInput(BaseModel):
    """משחק בודד לתחזית מרובה - תומך בשני סגנונות שמות שדות"""
    home: str = Field(..., description="קבוצה מארחת")
    away: str = Field(..., description="קבוצה אורחת")
    league: str = Field(default="General", description="שם הליגה")

    class Config:
        populate_by_name = True

    @model_validator(mode='before')
    @classmethod
    def normalize_team_names(cls, data):
        return normalize_team_field_names(data)


class BatchPredictionRequest(BaseModel):
    """בקשת תחזיות מרובות - עד 4 משחקים"""
    matches: List[MatchInput] = Field(..., max_length=4, description="רשימת משחקים (עד 4)")
    depth: str = Field(default="standard", description="עומק ניתוח")
    user_id: Optional[str] = Field(default=None, description="מזהה משתמש")


class ComparisonRequest(BaseModel):
    """בקשת השוואה בין קבוצות - תומך בשני סגנונות שמות שדות"""
    home: str = Field(..., description="קבוצה ראשונה")
    away: str = Field(..., description="קבוצה שנייה")
    league: str = Field(default="General", description="שם הליגה")

    class Config:
        populate_by_name = True

    @model_validator(mode='before')
    @classmethod
    def normalize_team_names(cls, data):
        return normalize_team_field_names(data)


#
# ENDPOINTS - תחזיות
# 

@router.post("/predict", response_class=ORJSONResponse)
@limiter.limit("30/minute")
async def predict_match(request: Request, prediction_request: PredictionRequest, background_tasks: BackgroundTasks):
    """
     תחזית משחק - Endpoint ראשי

    מקבל שתי קבוצות וליגה, מחזיר תחזית מלאה
    """
    try:
        prediction_result = analyze_match(
            home=prediction_request.home,
            away=prediction_request.away,
            league=prediction_request.league
        )

        if not prediction_result or "prediction" not in prediction_result:
            raise HTTPException(status_code=500, detail="שגיאה ביצירת התחזית")


        # בניית תגובה מאוחדת שכוללת גם CTO format וגם legacy format
        response = {
            "success": True,
            "prediction": prediction_result.get("prediction", {}),
            "match": prediction_result.get("match", {}),
            "factors": prediction_result.get("factors", {}),
            "insight": prediction_result.get("insight", ""),
            "insight_en": prediction_result.get("insight_en", ""),
            "momentum": prediction_result.get("momentum", {}),
            "h2h": prediction_result.get("h2h", []),
            "extended_stats": prediction_result.get("extended_stats", {}),
            "risk_level": prediction_result.get("risk_level", "MEDIUM"),
            "recommendations": prediction_result.get("recommendations", []),
            "mvp_markets": prediction_result.get("mvp_markets", {}),
            "metadata": prediction_result.get("metadata", {}),
            "data_source": {"mode": "TITAN_AI_v7"}
        }

        # הוסף markets ו-summary אם קיימים (CTO format)
        if "markets" in prediction_result:
            response["markets"] = prediction_result["markets"]
        if "summary" in prediction_result:
            response["summary"] = prediction_result["summary"]
        if "analysis" in prediction_result:
            response["analysis"] = prediction_result["analysis"]

        return ORJSONResponse(content=response)

    except Exception as e:
        print(f" Error in prediction: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/predict/single")
async def predict_single_detailed(request: SinglePredictionRequest, background_tasks: BackgroundTasks):
    """
     תחזית יחידה מפורטת (Phase 3: with Confidence Score)

    מאפשר שליטה מלאה על הנתונים המוחזרים + Confidence Score
    """
    try:
        # 🎯 Phase 3: Use confidence-aware wrapper
        from ai_predictor import analyze_match_with_confidence

        # TODO: Get tier from user's subscription status
        tier = "free"  # Default: free tier

        prediction_result = analyze_match_with_confidence(
            home=request.home,
            away=request.away,
            league=request.league,
            depth=request.depth,
            user_id=request.user_id,
            tier=tier
        )

        response = {
            "success": True,
            "mode": "single_detailed",
            "prediction": prediction_result.get("prediction", {}),
            "match": prediction_result.get("match", {}),
            "insight": prediction_result.get("insight", ""),
            "insight_en": prediction_result.get("insight_en", ""),
            "factors": prediction_result.get("factors", {}),
            "risk_level": prediction_result.get("risk_level", "MEDIUM"),
            "value_bet": prediction_result.get("value_bet", False),
            "mvp_markets": prediction_result.get("mvp_markets", {})
        }

        # הוספת נתונים לפי בחירה
        if request.include_h2h:
            response["h2h"] = prediction_result.get("h2h", [])
        if request.include_momentum:
            response["momentum"] = prediction_result.get("momentum", {})
        if request.include_extended_stats:
            response["extended_stats"] = prediction_result.get("extended_stats", {})
        if request.include_recommendations:
            response["recommendations"] = prediction_result.get("recommendations", [])

        response["metadata"] = prediction_result.get("metadata", {})

        # 🎯 Phase 3: Add confidence score
        response["confidence"] = prediction_result.get("confidence", {})

        return response

    except Exception as e:
        print(f" Error in single prediction: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/predict/batch", response_class=ORJSONResponse)
async def predict_batch(request: BatchPredictionRequest, background_tasks: BackgroundTasks):
    """
     תחזיות מרובות - עד 4 משחקים בבת אחת

    מתאים לניתוח מספר משחקים במקביל
    """
    try:
        if len(request.matches) > 4:
            raise HTTPException(
                status_code=400,
                detail="ניתן לנתח עד 4 משחקים בבת אחת"
            )

        matches_data = [
            {
                "home": m.home,
                "away": m.away,
                "league": m.league
            }
            for m in request.matches
        ]

        result = analyze_batch(
            matches=matches_data,
            depth=request.depth,
            user_id=request.user_id
        )

        return ORJSONResponse(content=result)

    except HTTPException:
        raise
    except Exception as e:
        print(f" Error in batch prediction: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/predict/compare")
async def compare_teams(request: ComparisonRequest):
    """
     השוואה מפורטת בין שתי קבוצות

    מחזיר ניתוח השוואתי עם המלצות
    """
    try:
        result = get_comparison(
            home=request.home,
            away=request.away,
            league=request.league
        )

        return {
            "success": True,
            "mode": "comparison",
            **result
        }

    except Exception as e:
        print(f" Error in comparison: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/predict/titan")
@limiter.limit("30/minute")
async def predict_titan_standard(request: Request, prediction_request: PredictionRequest):
    """
     TITAN Standard Mode - CTO Specification Compliant

    Professional analytical prediction system.
    Returns structured JSON analysis in Hebrew.
    Acts as analyst, not bettor.

    NO emojis, NO hype, NO promises - just analysis.
    """
    if not TITAN_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="TITAN Standard Mode not available"
        )

    try:
        result = get_titan_prediction(
            home=prediction_request.home,
            away=prediction_request.away,
            league=prediction_request.league
        )

        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Unknown error")
            )

        return {
            "success": True,
            "mode": "TITAN_STANDARD",
            **result.get("data", {})
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f" Error in TITAN prediction: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# 
# ENDPOINTS - מידע ותצורה
# 

@router.get("/predict/options")
async def get_prediction_options():
    """
     אפשרויות התחזית הזמינות
    """
    endpoints = {
        "single_prediction": {
            "path": "/predict",
            "method": "POST",
            "description": "תחזית יחידה בסיסית",
            "description_en": "Basic single prediction",
            "available_to": "all"
        },
        "single_detailed": {
            "path": "/predict/single",
            "method": "POST",
            "description": "תחזית יחידה מפורטת עם כל האופציות",
            "description_en": "Detailed single prediction with all options",
            "available_to": "all"
        },
        "batch_prediction": {
            "path": "/predict/batch",
            "method": "POST",
            "description": "תחזיות מרובות - עד 4 משחקים",
            "description_en": "Multiple predictions - up to 4 matches",
            "max_matches": 4,
            "available_to": "all"
        },
        "comparison": {
            "path": "/predict/compare",
            "method": "POST",
            "description": "השוואה מפורטת בין קבוצות",
            "description_en": "Detailed comparison between teams",
            "available_to": "all"
        }
    }

    # Add TITAN Standard Mode if available
    if TITAN_AVAILABLE:
        endpoints["titan_standard"] = {
            "path": "/predict/titan",
            "method": "POST",
            "description": "מצב TITAN Standard - תחזית אנליטית מקצועית",
            "description_en": "TITAN Standard Mode - Professional analytical prediction",
            "available_to": "all",
            "features": "CTO Spec Compliant | No Emojis | Pure Analysis"
        }

    return {
        "success": True,
        "endpoints": endpoints,
        "analysis_depths": {
            "quick": "ניתוח מהיר - תוצאה בלבד",
            "standard": "ניתוח רגיל - תוצאה + תובנות",
            "deep": "ניתוח מעמיק - כל הנתונים",
            "expert": "ניתוח מומחה - כולל המלצות"
        },
        "sports_supported": get_supported_sports(),
        "ai_status": "ONLINE" if is_ai_online() else "FALLBACK",
        "engine_version": get_engine_version(),
        "titan_available": TITAN_AVAILABLE,
        "titan_version": get_titan_version() if TITAN_AVAILABLE else None
    }


@router.get("/engine/stats")
async def get_stats():
    """
     סטטיסטיקות מנוע ה-AI
    """
    return {
        "success": True,
        **get_engine_stats()
    }


@router.get("/engine/health")
async def health_check():
    """
     בדיקת תקינות המנוע
    """
    return {
        "status": "healthy",
        "ai_online": is_ai_online(),
        "version": get_engine_version(),
        "message": "TITAN AI Engine is operational" if is_ai_online() else "Running in Fallback mode"
    }


# 
# ENDPOINTS - קבוצות וליגות
# 

@router.get("/teams")
async def list_teams(
        league: Optional[str] = Query(None, description="סנן לפי ליגה"),
        sport: Optional[str] = Query(None, description="סנן לפי ספורט")
):
    """
     רשימת קבוצות זמינות
    """
    teams = []

    if data_manager:
        teams = data_manager.list_teams()

    # רשימת גיבוי
    if not teams:
        teams = [
            # כדורגל ישראלי
            "מכבי תל אביב", "מכבי חיפה", "הפועל באר שבע",
            "בית\"ר ירושלים", "מכבי נתניה", "הפועל תל אביב",
            "הפועל ירושלים", "בני סכנין", "עירוני קריית שמונה",
            "הפועל חיפה", "מכבי פתח תקווה", "בני יהודה",
            # ליגות אירופאיות
            "ריאל מדריד", "ברצלונה", "אתלטיקו מדריד",
            "מנצ'סטר סיטי", "ליברפול", "ארסנל", "צ'לסי",
            "באיירן מינכן", "בורוסיה דורטמונד",
            "פריז סן ז'רמן", "מרסיי",
            "יובנטוס", "אינטר מילאן", "מילאן",
            # NBA
            "Los Angeles Lakers", "Boston Celtics", "Golden State Warriors",
            "Miami Heat", "Brooklyn Nets", "Phoenix Suns"
        ]

    catalog = [
        {
            "name": t,
            "league": "Israel Premier League" if any(heb in t for heb in ["מכבי", "הפועל", "בית\"ר", "בני"]) else "International"
        }
        for t in sorted(teams)
    ]

    return {
        "success": True,
        "count": len(catalog),
        "teams": catalog
    }


@router.get("/leagues")
async def list_leagues():
    """
     רשימת ליגות נתמכות
    """
    leagues = [
        # כדורגל
        {"name": "ליגת העל", "sport": "Football", "country": "Israel"},
        {"name": "ליגה לאומית", "sport": "Football", "country": "Israel"},
        {"name": "Premier League", "sport": "Football", "country": "England"},
        {"name": "La Liga", "sport": "Football", "country": "Spain"},
        {"name": "Bundesliga", "sport": "Football", "country": "Germany"},
        {"name": "Serie A", "sport": "Football", "country": "Italy"},
        {"name": "Ligue 1", "sport": "Football", "country": "France"},
        {"name": "Champions League", "sport": "Football", "country": "Europe"},
        {"name": "Europa League", "sport": "Football", "country": "Europe"},
        # כדורסל
        {"name": "NBA", "sport": "Basketball", "country": "USA"},
        {"name": "Euroleague", "sport": "Basketball", "country": "Europe"},
        {"name": "BSL (Winner)", "sport": "Basketball", "country": "Israel"},
        # טניס
        {"name": "ATP Tour", "sport": "Tennis", "country": "International"},
        {"name": "WTA Tour", "sport": "Tennis", "country": "International"},
    ]

    return {
        "success": True,
        "count": len(leagues),
        "leagues": leagues
    }

# 
# ENDPOINTS - Analytics (TITAN v2.0)
# 

@router.get("/analytics/stats")
async def get_analytics_stats(days: int = 7):
    """
     Get analytics statistics

    Query params:
        days: Number of days to analyze (default: 7)

    Returns:
        Statistics about predictions, confidence, XG, etc.
    """
    from analytics_tracker import AnalyticsTracker

    try:
        tracker = AnalyticsTracker()
        stats = tracker.get_stats(last_n_days=days)

        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Failed to get analytics stats: {e}")
        return {
            "success": False,
            "error": str(e),
            "stats": {"total_predictions": 0, "message": "Failed to load analytics"}
        }


@router.get("/analytics/report")
async def get_analytics_report(days: int = 7):
    """
     Get analytics text report

    Query params:
        days: Number of days to analyze (default: 7)

    Returns:
        Formatted text report with charts and statistics
    """
    from analytics_tracker import AnalyticsTracker

    try:
        tracker = AnalyticsTracker()
        report = tracker.generate_report(last_n_days=days)

        return {
            "success": True,
            "report": report
        }
    except Exception as e:
        logger.error(f"Failed to generate analytics report: {e}")
        return {
            "success": False,
            "error": str(e),
            "report": "Failed to generate report"
        }


# 
# ENDPOINTS - משתמשים
# 

@router.get("/user/{user_id}/stats")
async def get_user_stats(user_id: str):
    """
     סטטיסטיקות משתמש
    """
    stats = ai_engine.get_user_stats(user_id)
    return {
        "success": True,
        "user_id": user_id,
        **stats
    }


