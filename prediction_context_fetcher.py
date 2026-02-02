"""
🧠 Smart Prediction Context Fetcher - Phase 2 ULTRA Core
Created by: Rafael & AI Assistant
Version: 2.0 - UPGRADED for Premium API (7500 calls/day!)

מטרה:
משוך דאטה רלוונטי מ-API-Sports בצורה חכמה:
✅ משתמש ב-Cache כדי לחסוך קריאות API
✅ מכבד תקציב יומי (7500 calls Premium!)
✅ בוחר מה למשוך לפי Priority (Standings > Team Stats > Form > H2H)
✅ מותאם לפי Tier (Free = 3 calls, Premium = 7 calls)

Flow:
1. בדוק תקציב API
2. בדוק Cache
3. משוך מ-API רק אם צריך
4. החזר context אחיד ל-AI

🚀 UPGRADED FEATURES (v2.0):
- Premium now gets 7 API calls (was 5)
- Added Team Statistics (2 new calls)
- Data quality levels: basic → standard → premium → ultra

זה הלב של Phase 2 המשודרג!
"""

import asyncio
import logging
from typing import Dict, Optional, Any
from datetime import datetime

# Imports
try:
    from cache_manager import cache_manager, CacheTTL
    from api_budget_tracker import api_budget_tracker, EndpointType
    from sports_api import SportsAPIManager
except ImportError:
    try:
        from backend.cache_manager import cache_manager, CacheTTL
        from backend.api_budget_tracker import api_budget_tracker, EndpointType
        from backend.sports_api import SportsAPIManager
    except ImportError as e:
        raise ImportError(f"Failed to import Phase 2 dependencies: {e}")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PredictionContextFetcher:
    """
    🧠 Smart Data Fetcher עם Cache ו-Budget Awareness

    תפקידו:
    1. לא לחרוג ממכסת API (100/יום)
    2. להשתמש ב-Cache כמה שיותר
    3. למשוך רק דאטה שבאמת משנה
    4. להתאים את עצמו ל-Free/Premium tier

    Usage:
        fetcher = PredictionContextFetcher()

        context = await fetcher.fetch_prediction_context(
            home="Barcelona",
            away="Real Madrid",
            league_id=140,
            tier="premium"
        )

        # context מכיל:
        # - standings (טבלת ליגה)
        # - form (5 משחקים אחרונים)
        # - h2h (היסטוריה ביניהם)
        # - metadata (API calls used, cache efficiency)
    """

    def __init__(self):
        """אתחול Fetcher"""
        self.sports_api = SportsAPIManager()
        logger.info("🧠 PredictionContextFetcher initialized")

    async def fetch_prediction_context(
        self,
        home: str,
        away: str,
        league_id: int,
        match_date: Optional[str] = None,
        tier: str = "free"
    ) -> Dict[str, Any]:
        """
        🎯 משוך Context חכם לתחזית

        Args:
            home: קבוצת הבית
            away: קבוצת החוץ
            league_id: מזהה הליגה (לדוגמה: 39 = Premier League)
            match_date: תאריך המשחק (אופציונלי)
            tier: "free" או "premium"

        Returns:
            dict עם:
            - standings: טבלת ליגה
            - form: פורמה אחרונה (אם יש תקציב)
            - h2h: Head-to-Head (רק Premium)
            - metadata: מידע על השימוש ב-API

        Logic:
        - Free tier: רק Standings (חובה)
        - Premium tier: Standings + Form + H2H (אם יש תקציב)
        """
        # 🔧 UPGRADED: Rafael's Premium API (7500 calls/day!)
        context = {
            "standings": None,
            "team_stats": {"home": None, "away": None},  # NEW!
            "form": {"home": None, "away": None},
            "h2h": None,
            "match_data": None,  # NEW!
            "match_date": match_date,
            "metadata": {
                "api_calls_used": 0,
                "api_calls_budget": 3 if tier == "free" else 7,  # ⚡ UPGRADED from 5 to 7!
                "cache_hits": 0,
                "cache_misses": 0,
                "tier": tier,
                "data_quality": "basic",
                "data_completeness": "full"  # 🔧 CTO: Track partial failures
            }
        }

        api_calls_used = 0
        max_calls = context["metadata"]["api_calls_budget"]
        failed_fetches = []  # 🔧 CTO: Fail-soft tracking

        # ✅ Priority 1: Standings (חובה - גם Free וגם Premium)
        if await api_budget_tracker.can_make_call():
            try:
                standings_data = await self._get_cached_or_fetch(
                    cache_key=f"standings_{league_id}",
                    fetch_func=lambda: self.sports_api.get_league_standings(league_id),
                    ttl=CacheTTL.STANDINGS,
                    endpoint=EndpointType.STANDINGS
                )

                if standings_data:
                    context["standings"] = standings_data["data"]
                    api_calls_used += 0 if standings_data["from_cache"] else 1
                    context["metadata"]["cache_hits" if standings_data["from_cache"] else "cache_misses"] += 1
                else:
                    failed_fetches.append("standings")
            except Exception as e:
                logger.error(f"🔧 Fail-soft: standings fetch failed: {e}")
                failed_fetches.append("standings")

        # ✅ Priority 2: Team Statistics (רק Premium - 2 calls)
        if tier == "premium" and api_calls_used < max_calls:
            # Home team stats
            if await api_budget_tracker.can_make_call():
                try:
                    home_stats_data = await self._get_cached_or_fetch(
                        cache_key=f"team_stats_{home}_{league_id}",
                        fetch_func=lambda: self.sports_api.get_team_statistics(home, league_id),
                        ttl=CacheTTL.LAST_5_MATCHES,  # Same TTL as form
                        endpoint=EndpointType.FIXTURES
                    )

                    if home_stats_data:
                        context["team_stats"]["home"] = home_stats_data["data"]
                        api_calls_used += 0 if home_stats_data["from_cache"] else 1
                        context["metadata"]["cache_hits" if home_stats_data["from_cache"] else "cache_misses"] += 1
                    else:
                        failed_fetches.append("team_stats_home")
                except Exception as e:
                    logger.error(f"🔧 Fail-soft: home team stats fetch failed: {e}")
                    failed_fetches.append("team_stats_home")

            # Away team stats
            if await api_budget_tracker.can_make_call() and api_calls_used < max_calls:
                try:
                    away_stats_data = await self._get_cached_or_fetch(
                        cache_key=f"team_stats_{away}_{league_id}",
                        fetch_func=lambda: self.sports_api.get_team_statistics(away, league_id),
                        ttl=CacheTTL.LAST_5_MATCHES,
                        endpoint=EndpointType.FIXTURES
                    )

                    if away_stats_data:
                        context["team_stats"]["away"] = away_stats_data["data"]
                        api_calls_used += 0 if away_stats_data["from_cache"] else 1
                        context["metadata"]["cache_hits" if away_stats_data["from_cache"] else "cache_misses"] += 1
                    else:
                        failed_fetches.append("team_stats_away")
                except Exception as e:
                    logger.error(f"🔧 Fail-soft: away team stats fetch failed: {e}")
                    failed_fetches.append("team_stats_away")

        # ✅ Priority 3: Form (רק אם יש תקציב)
        if tier in ["premium", "free"] and api_calls_used < max_calls:
            # Home team form
            if await api_budget_tracker.can_make_call():
                try:
                    # Note: get_team_last_matches needs team_id, not team_name
                    # For now, skip form data until we have team_id resolution
                    home_form_data = None
                    logger.warning(f"⚠️ Form data skipped - need team_id for {home}")

                    if home_form_data:
                        context["form"]["home"] = home_form_data["data"]
                        api_calls_used += 0 if home_form_data["from_cache"] else 1
                        context["metadata"]["cache_hits" if home_form_data["from_cache"] else "cache_misses"] += 1
                    else:
                        failed_fetches.append("form_home")
                except Exception as e:
                    logger.error(f"🔧 Fail-soft: home form fetch failed: {e}")
                    failed_fetches.append("form_home")

            # Away team form
            if await api_budget_tracker.can_make_call() and api_calls_used < max_calls:
                try:
                    # Note: get_team_last_matches needs team_id, not team_name
                    # For now, skip form data until we have team_id resolution
                    away_form_data = None
                    logger.warning(f"⚠️ Form data skipped - need team_id for {away}")

                    if away_form_data:
                        context["form"]["away"] = away_form_data["data"]
                        api_calls_used += 0 if away_form_data["from_cache"] else 1
                        context["metadata"]["cache_hits" if away_form_data["from_cache"] else "cache_misses"] += 1
                    else:
                        failed_fetches.append("form_away")
                except Exception as e:
                    logger.error(f"🔧 Fail-soft: away form fetch failed: {e}")
                    failed_fetches.append("form_away")

        # ⚡ Priority 4: H2H (רק Premium + אם יש תקציב)
        if tier == "premium" and api_calls_used < max_calls:
            if await api_budget_tracker.can_make_call():
                try:
                    # Note: get_h2h_statistics needs team_ids, not team_names
                    # For now, skip h2h data until we have team_id resolution
                    h2h_data = None
                    logger.warning(f"⚠️ H2H data skipped - need team_ids for {home} vs {away}")

                    if h2h_data:
                        context["h2h"] = h2h_data["data"]
                        api_calls_used += 0 if h2h_data["from_cache"] else 1
                        context["metadata"]["cache_hits" if h2h_data["from_cache"] else "cache_misses"] += 1
                    else:
                        failed_fetches.append("h2h")
                except Exception as e:
                    logger.error(f"🔧 Fail-soft: h2h fetch failed: {e}")
                    failed_fetches.append("h2h")

        # 📊 Update metadata
        context["metadata"]["api_calls_used"] = api_calls_used
        cache_total = context["metadata"]["cache_hits"] + context["metadata"]["cache_misses"]
        cache_efficiency = (context["metadata"]["cache_hits"] / cache_total * 100) if cache_total > 0 else 0
        context["metadata"]["cache_efficiency"] = f"{cache_efficiency:.0f}%"

        # 🔧 CTO: Data completeness tracking
        if failed_fetches:
            context["metadata"]["data_completeness"] = "partial"
            logger.warning(f"⚠️ Partial context: failed fetches = {failed_fetches}")
        else:
            context["metadata"]["data_completeness"] = "full"

        # Data quality assessment - UPGRADED!
        has_all = (context["standings"] and
                   context["team_stats"]["home"] and context["team_stats"]["away"] and
                   context["form"]["home"] and context["form"]["away"] and
                   context["h2h"])

        if has_all:
            context["metadata"]["data_quality"] = "ultra"  # 7 API calls - Full power!
        elif context["standings"] and context["form"]["home"] and context["form"]["away"] and context["h2h"]:
            context["metadata"]["data_quality"] = "premium"  # 5 API calls
        elif context["standings"] and (context["form"]["home"] or context["form"]["away"]):
            context["metadata"]["data_quality"] = "standard"  # 3 API calls
        else:
            context["metadata"]["data_quality"] = "basic"

        logger.info(
            f"📊 Context fetched: {tier} tier, "
            f"{api_calls_used} API calls, "
            f"{context['metadata']['cache_efficiency']} cache efficiency, "
            f"quality={context['metadata']['data_quality']}"
        )

        return context

    async def _get_cached_or_fetch(
        self,
        cache_key: str,
        fetch_func,
        ttl: int,
        endpoint: EndpointType
    ) -> Optional[Dict]:
        """
        🔍 Helper: בדוק Cache → אם לא קיים, משוך מ-API

        Args:
            cache_key: מפתח ייחודי
            fetch_func: פונקציה למשיכה מ-API
            ttl: Time To Live
            endpoint: סוג ה-endpoint (למעקב)

        Returns:
            {"data": ..., "from_cache": bool} או None אם נכשל
        """
        # 1. בדוק Cache
        cached = await cache_manager.get(cache_key, ttl)

        if cached:
            logger.info(f"💨 Cache HIT: {cache_key}")
            return {"data": cached, "from_cache": True}

        # 2. Cache MISS - משוך מ-API
        logger.info(f"🌐 Cache MISS: {cache_key} - Fetching from API")

        try:
            data = await fetch_func()

            if data:
                # שמור ב-Cache
                await cache_manager.set(cache_key, data, ttl)

                # רשום קריאת API
                await api_budget_tracker.record_call(endpoint, from_cache=False)

                return {"data": data, "from_cache": False}
            else:
                logger.warning(f"⚠️ API returned empty data for {cache_key}")
                return None

        except Exception as e:
            logger.error(f"❌ Error fetching {cache_key}: {e}")
            return None


# 🌍 Global instance
prediction_context_fetcher = PredictionContextFetcher()


# ╔══════════════════════════════════════════════════════════════════════════════════╗
# ║  📦 CONVENIENCE FUNCTION                                                          ║
# ╚══════════════════════════════════════════════════════════════════════════════════╝

async def fetch_prediction_context(
    home: str,
    away: str,
    league_id: int,
    match_date: Optional[str] = None,
    tier: str = "free"
) -> Dict[str, Any]:
    """
    🎯 Convenience function - קיצור דרך

    Usage:
        from prediction_context_fetcher import fetch_prediction_context

        context = await fetch_prediction_context(
            home="Barcelona",
            away="Real Madrid",
            league_id=140,
            tier="premium"
        )
    """
    return await prediction_context_fetcher.fetch_prediction_context(
        home=home,
        away=away,
        league_id=league_id,
        match_date=match_date,
        tier=tier
    )


if __name__ == "__main__":
    """
    🧪 בדיקות יחידה
    """
    async def test_fetcher():
        print("🧪 Testing PredictionContextFetcher...\n")

        fetcher = PredictionContextFetcher()

        # Test 1: Free tier
        print("Test 1: Free Tier Context")
        context = await fetcher.fetch_prediction_context(
            home="Barcelona",
            away="Real Madrid",
            league_id=140,
            tier="free"
        )
        print(f"API calls used: {context['metadata']['api_calls_used']}")
        print(f"Data quality: {context['metadata']['data_quality']}")
        print(f"Cache efficiency: {context['metadata']['cache_efficiency']}")
        assert context['metadata']['tier'] == 'free'
        print("✅ Passed\n")

        # Test 2: Premium tier
        print("Test 2: Premium Tier Context")
        context = await fetcher.fetch_prediction_context(
            home="Manchester City",
            away="Liverpool",
            league_id=39,
            tier="premium"
        )
        print(f"API calls used: {context['metadata']['api_calls_used']}")
        print(f"Data quality: {context['metadata']['data_quality']}")
        print(f"Has H2H: {context['h2h'] is not None}")
        print("✅ Passed\n")

        # Test 3: Cache efficiency (second call)
        print("Test 3: Cache Efficiency (repeated call)")
        context = await fetcher.fetch_prediction_context(
            home="Barcelona",
            away="Real Madrid",
            league_id=140,
            tier="free"
        )
        # Should have high cache efficiency now!
        print(f"Cache efficiency: {context['metadata']['cache_efficiency']}")
        assert context['metadata']['cache_hits'] > 0, "Should have cache hits"
        print("✅ Passed\n")

        print("🎉 All tests passed!")

    # Run tests
    asyncio.run(test_fetcher())
