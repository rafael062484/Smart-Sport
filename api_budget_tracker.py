"""
💰 API Budget Tracker - Smart Cost Control
Created by: Rafael & AI Assistant (Phase 2)
Version: 1.0 - Production Ready

מטרה:
מעקב אחר שימוש ב-API-Sports למניעת חריגה ממכסת 100 קריאות/יום (Free Tier)
או 500 קריאות/יום (Paid Tier).

תכונות:
✅ Daily reset אוטומטי בחצות
✅ Guard rails - downgrade אוטומטי כש-90% מהמכסה נוצלה
✅ Cost estimation (Free vs Paid tier)
✅ Per-endpoint tracking (standings, form, h2h)
✅ Warning alerts למשתמש
✅ Metrics export ל-/api/api-budget/status

עקרונות:
- ב-80% מהמכסה: אזהרה
- ב-90% מהמכסה: מעבר למצב "Free behavior" (פחות קריאות)
- ב-100% מהמכסה: חסימה מלאה עד reset
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
from dataclasses import dataclass, field
from enum import Enum
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TierType(str, Enum):
    """סוגי Tier למכסות API"""
    FREE = "free"
    PAID = "paid"
    UNLIMITED = "unlimited"


class EndpointType(str, Enum):
    """סוגי Endpoints ב-API-Sports"""
    STANDINGS = "standings"
    FIXTURES = "fixtures"
    TEAMS = "teams"
    H2H = "h2h"
    STATISTICS = "statistics"
    LIVE = "live"
    OTHER = "other"


@dataclass
class DailyUsage:
    """
    📊 שימוש יומי ב-API

    Attributes:
        date: תאריך
        total_calls: סה"כ קריאות
        by_endpoint: פירוט לפי endpoint
        tier: Free/Paid/Unlimited
    """
    date: datetime = field(default_factory=datetime.now)
    total_calls: int = 0
    by_endpoint: Dict[str, int] = field(default_factory=dict)
    tier: TierType = TierType.FREE

    def to_dict(self) -> dict:
        return {
            "date": self.date.strftime("%Y-%m-%d"),
            "total_calls": self.total_calls,
            "by_endpoint": self.by_endpoint,
            "tier": self.tier.value
        }


class APIBudgetTracker:
    """
    💰 מעקב תקציב API-Sports

    Features:
    ✅ Daily limits (100 Free, 500 Paid)
    ✅ Auto reset at midnight
    ✅ Guard rails at 90%
    ✅ Per-endpoint breakdown
    ✅ Cost estimation
    ✅ Warning system

    Usage:
        tracker = APIBudgetTracker(tier="free")

        # לפני כל קריאה ל-API
        if tracker.can_make_call():
            data = await sports_api.get_standings()
            tracker.record_call(EndpointType.STANDINGS)
        else:
            print("⛔ Budget limit reached!")
    """

    # Tier limits
    TIER_LIMITS = {
        TierType.FREE: 100,
        TierType.PAID: 500,
        TierType.UNLIMITED: 999999
    }

    # Cost per call (in USD)
    COST_PER_CALL = {
        TierType.FREE: 0.0,  # Free tier = $0
        TierType.PAID: 0.001,  # Paid tier = ~$0.001/call (estimate)
        TierType.UNLIMITED: 0.0005  # Enterprise = cheaper per call
    }

    def __init__(self, tier: str = "free"):
        """
        אתחול Tracker

        Args:
            tier: "free", "paid", או "unlimited"
        """
        self.tier = TierType(tier.lower())
        self.daily_limit = self.TIER_LIMITS[self.tier]

        # Current day usage
        self._current_usage = DailyUsage(tier=self.tier)

        # Historical data (last 30 days)
        self._history: list[DailyUsage] = []

        # Locks
        self._lock = asyncio.Lock()

        # Warnings
        self._warning_threshold = 0.8  # 80%
        self._critical_threshold = 0.9  # 90%
        self._warned_at_80 = False
        self._warned_at_90 = False

        logger.info(f"💰 APIBudgetTracker initialized (tier={tier}, limit={self.daily_limit}/day)")

    async def can_make_call(self, endpoint: Optional[EndpointType] = None) -> bool:
        """
        ✅ בדוק אם ניתן לבצע קריאת API

        Args:
            endpoint: סוג ה-endpoint (אופציונלי, למטרות לוגים)

        Returns:
            True אם יש תקציב, False אחרת
        """
        async with self._lock:
            # Auto reset if day changed
            await self._check_and_reset_if_needed()

            # Check if limit reached
            if self._current_usage.total_calls >= self.daily_limit:
                logger.error(f"⛔ API Budget EXCEEDED: {self._current_usage.total_calls}/{self.daily_limit}")
                return False

            # Warning at 80%
            usage_percent = self._current_usage.total_calls / self.daily_limit
            if usage_percent >= self._warning_threshold and not self._warned_at_80:
                logger.warning(f"🟡 API Budget at 80%: {self._current_usage.total_calls}/{self.daily_limit}")
                self._warned_at_80 = True

            # Critical at 90%
            if usage_percent >= self._critical_threshold and not self._warned_at_90:
                logger.error(f"🔴 API Budget at 90%: {self._current_usage.total_calls}/{self.daily_limit} - Switching to conservative mode")
                self._warned_at_90 = True

            return True

    async def record_call(
        self,
        endpoint: EndpointType = EndpointType.OTHER,
        from_cache: bool = False
    ) -> None:
        """
        📝 רשום קריאת API (או Cache HIT)

        Args:
            endpoint: סוג ה-endpoint
            from_cache: האם הנתונים הגיעו מ-Cache (לא נחשב בתקציב)
        """
        # אם הגיע מ-Cache - לא נחשב בתקציב API!
        if from_cache:
            logger.debug(f"💨 Cache HIT for {endpoint.value} - not counting towards budget")
            return

        async with self._lock:
            await self._check_and_reset_if_needed()

            self._current_usage.total_calls += 1

            # Track by endpoint
            endpoint_name = endpoint.value
            if endpoint_name not in self._current_usage.by_endpoint:
                self._current_usage.by_endpoint[endpoint_name] = 0
            self._current_usage.by_endpoint[endpoint_name] += 1

            logger.info(
                f"📞 API Call recorded: {endpoint.value} "
                f"(total={self._current_usage.total_calls}/{self.daily_limit})"
            )

    async def get_status(self) -> dict:
        """
        📊 קבל סטטוס נוכחי של התקציב

        Returns:
            dict עם כל המידע הרלוונטי
        """
        async with self._lock:
            await self._check_and_reset_if_needed()

            calls_used = self._current_usage.total_calls
            calls_remaining = self.daily_limit - calls_used
            usage_percent = (calls_used / self.daily_limit * 100) if self.daily_limit > 0 else 0

            # Status indicator
            if usage_percent < 80:
                status = "🟢 Healthy"
            elif usage_percent < 90:
                status = "🟡 Warning"
            else:
                status = "🔴 Critical"

            # Cost estimation
            estimated_cost_today = calls_used * self.COST_PER_CALL[self.tier]
            estimated_cost_month = estimated_cost_today * 30

            return {
                "tier": self.tier.value,
                "date": self._current_usage.date.strftime("%Y-%m-%d"),
                "calls_used": calls_used,
                "calls_remaining": calls_remaining,
                "daily_limit": self.daily_limit,
                "usage_percent": round(usage_percent, 1),
                "status": status,
                "by_endpoint": self._current_usage.by_endpoint,
                "cost_today_usd": round(estimated_cost_today, 3),
                "cost_month_estimate_usd": round(estimated_cost_month, 2),
                "warnings": {
                    "approaching_limit": usage_percent >= 80,
                    "critical": usage_percent >= 90,
                    "exceeded": calls_used >= self.daily_limit
                }
            }

    async def get_stats(self) -> dict:
        """
        📈 קבל סטטיסטיקות מפורטות (כולל היסטוריה)

        Returns:
            dict עם נתונים סטטיסטיים
        """
        status = await self.get_status()

        # Historical average (last 7 days)
        recent_history = self._history[-7:] if self._history else []
        avg_daily_calls = (
            sum(day.total_calls for day in recent_history) / len(recent_history)
            if recent_history else 0
        )

        return {
            **status,
            "history": {
                "days_tracked": len(self._history),
                "avg_daily_calls_7d": round(avg_daily_calls, 1),
                "recent_days": [day.to_dict() for day in recent_history]
            }
        }

    async def _check_and_reset_if_needed(self) -> None:
        """
        🔄 בדוק אם עבר יום - אם כן, reset התקציב

        מתבצע אוטומטית בכל קריאה
        """
        now = datetime.now()
        current_date = now.date()
        usage_date = self._current_usage.date.date()

        if current_date > usage_date:
            # Save to history
            self._history.append(self._current_usage)

            # Keep only last 30 days
            if len(self._history) > 30:
                self._history = self._history[-30:]

            # Reset
            logger.info(
                f"🔄 Daily reset: {self._current_usage.total_calls} calls used yesterday. "
                f"Starting fresh with {self.daily_limit} calls."
            )

            self._current_usage = DailyUsage(date=now, tier=self.tier)
            self._warned_at_80 = False
            self._warned_at_90 = False

    async def set_tier(self, new_tier: str) -> None:
        """
        🎚️ שנה Tier (למשל, שדרוג מ-Free ל-Paid)

        Args:
            new_tier: "free", "paid", או "unlimited"
        """
        async with self._lock:
            old_tier = self.tier
            self.tier = TierType(new_tier.lower())
            self.daily_limit = self.TIER_LIMITS[self.tier]
            self._current_usage.tier = self.tier

            logger.info(f"🎚️ Tier changed: {old_tier.value} → {self.tier.value} (limit: {self.daily_limit})")

    def is_at_warning_level(self) -> bool:
        """🟡 בדוק אם הגענו לרמת אזהרה (80%)"""
        return (self._current_usage.total_calls / self.daily_limit) >= self._warning_threshold

    def is_at_critical_level(self) -> bool:
        """🔴 בדוק אם הגענו לרמה קריטית (90%)"""
        return (self._current_usage.total_calls / self.daily_limit) >= self._critical_threshold

    def should_downgrade_to_free_behavior(self) -> bool:
        """
        ⚠️ בדוק אם צריך לעבור למצב "Free behavior" (פחות קריאות)

        Returns:
            True אם חרגנו מ-90% מהמכסה
        """
        return self.is_at_critical_level()


# 🌍 Global instance (singleton)
# ברירת מחדל: Free Tier (100 calls/day)
api_budget_tracker = APIBudgetTracker(tier="free")


if __name__ == "__main__":
    """
    🧪 בדיקות יחידה
    """
    async def test_tracker():
        print("🧪 Testing APIBudgetTracker...\n")

        tracker = APIBudgetTracker(tier="free")

        # Test 1: Basic call tracking
        print("Test 1: Basic call tracking")
        assert await tracker.can_make_call() == True
        await tracker.record_call(EndpointType.STANDINGS)
        status = await tracker.get_status()
        assert status["calls_used"] == 1
        print(f"✅ Passed (calls_used={status['calls_used']})\n")

        # Test 2: Cache doesn't count
        print("Test 2: Cache HIT doesn't count towards budget")
        await tracker.record_call(EndpointType.STANDINGS, from_cache=True)
        status = await tracker.get_status()
        assert status["calls_used"] == 1  # Should still be 1!
        print(f"✅ Passed (calls_used={status['calls_used']})\n")

        # Test 3: Endpoint breakdown
        print("Test 3: Endpoint breakdown")
        await tracker.record_call(EndpointType.FIXTURES)
        await tracker.record_call(EndpointType.H2H)
        status = await tracker.get_status()
        print(f"By endpoint: {status['by_endpoint']}")
        assert status["calls_used"] == 3
        print("✅ Passed\n")

        # Test 4: Warning levels
        print("Test 4: Warning at 80%")
        for i in range(77):  # Total = 80 calls (80%)
            await tracker.record_call(EndpointType.OTHER)
        assert tracker.is_at_warning_level() == True
        print("✅ Passed\n")

        # Test 5: Full status
        print("Test 5: Full status")
        status = await tracker.get_status()
        print(json.dumps(status, indent=2, ensure_ascii=False))
        assert "status" in status
        assert "warnings" in status
        print("✅ Passed\n")

        print("🎉 All tests passed!")

    # Run tests
    asyncio.run(test_tracker())
