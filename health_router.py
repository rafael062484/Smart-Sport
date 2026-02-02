"""
🏥 Health & Monitoring Router
Created: 2026-01-09
"""

from fastapi import APIRouter
from datetime import datetime, timezone
from typing import Dict, Optional
from pydantic import BaseModel

router = APIRouter(tags=["Health & Monitoring"])

class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: str
    components: Dict[str, str]
    uptime_seconds: Optional[float] = None


@router.get("/api/health", response_model=HealthResponse)
async def health_check():
    from backend.app import app_start_time, settings, DB_LOADED, AI_ENGINE_LOADED, OPENAI_AVAILABLE, articles_cache, is_ai_online
    
    uptime = (datetime.now(timezone.utc) - app_start_time).total_seconds()
    
    return {
        "status": "healthy",
        "version": settings.app_version,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "uptime_seconds": round(uptime, 2),
        "components": {
            "database": "ok" if DB_LOADED else "unavailable",
            "ai_engine": "online" if (AI_ENGINE_LOADED and is_ai_online()) else "fallback",
            "openai": "connected" if OPENAI_AVAILABLE else "disconnected",
            "news": f"{len(articles_cache)} articles"
        }
    }


@router.get("/engine/health")
async def engine_health():
    from backend.app import AI_ENGINE_LOADED, OPENAI_AVAILABLE, is_ai_online, get_engine_version
    
    return {
        "status": "healthy" if AI_ENGINE_LOADED else "degraded",
        "ai_online": AI_ENGINE_LOADED and is_ai_online(),
        "version": get_engine_version(),
        "openai_available": OPENAI_AVAILABLE,
        "message": "TITAN AI Engine פעיל" if (AI_ENGINE_LOADED and is_ai_online()) else "מצב Fallback"
    }


@router.get("/engine/stats")
async def engine_stats():
    from backend.app import AI_ENGINE_LOADED, get_engine_stats
    
    if AI_ENGINE_LOADED:
        return {"success": True, **get_engine_stats()}
    return {"success": False, "error": "AI Engine not available"}
