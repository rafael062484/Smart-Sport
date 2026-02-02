"""
🗄️ Smart Cache Manager - Multi-Tier Caching System
Created by: Rafael & AI Assistant (Phase 2)
Version: 1.0 - Production Ready

מטרה:
מנהל Cache חכם שמקטין את מספר הקריאות ל-API-Sports מ-500 ל-100 ליום
על ידי שמירת נתונים עם TTL (Time To Live) משתנה לפי סוג הנתון.

עקרונות:
✅ Thread-safe / Async-safe (asyncio.Lock)
✅ TTL per key (לא global)
✅ Metadata tracking (timestamp, hits, last_access)
✅ Auto cleanup (מחיקת ערכים ישנים)
✅ Statistics (hit ratio, memory usage)

לא Redis - In-memory זה מספיק לשלב הזה.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple
from dataclasses import dataclass, field
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """
    📦 ערך בודד ב-Cache

    Attributes:
        data: הנתונים עצמם (dict, list, str, etc.)
        timestamp: מתי נשמר
        ttl: Time To Live בשניות
        hits: כמה פעמים נקרא
        last_access: גישה אחרונה
    """
    data: Any
    timestamp: datetime
    ttl: int  # seconds
    hits: int = 0
    last_access: datetime = field(default_factory=datetime.now)

    def is_expired(self) -> bool:
        """בדוק אם הערך פג תוקף"""
        age = (datetime.now() - self.timestamp).total_seconds()
        return age > self.ttl

    def age_seconds(self) -> float:
        """כמה שניות עברו מאז השמירה"""
        return (datetime.now() - self.timestamp).total_seconds()

    def to_dict(self) -> dict:
        """המרה ל-dict למטרות ניפוי באגים"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "ttl": self.ttl,
            "hits": self.hits,
            "last_access": self.last_access.isoformat(),
            "age_seconds": self.age_seconds(),
            "expired": self.is_expired()
        }


class CacheManager:
    """
    🗄️ מנהל Cache חכם עם TTL משתנה

    Features:
    ✅ Multi-tier TTL (6h, 3h, 24h, 30min)
    ✅ Thread-safe with asyncio.Lock
    ✅ Auto cleanup every 100 accesses
    ✅ Detailed statistics
    ✅ Memory-efficient (max 1000 entries)

    Usage:
        cache = CacheManager()

        # Set
        await cache.set("standings_39", data, ttl=21600)  # 6 hours

        # Get
        value = await cache.get("standings_39", ttl=21600)
        if value:
            print("Cache HIT!")
        else:
            print("Cache MISS - fetch from API")
    """

    def __init__(self, max_entries: int = 1000):
        """
        אתחול מנהל Cache

        Args:
            max_entries: מספר מקסימלי של ערכים (ברירת מחדל: 1000)
        """
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = asyncio.Lock()
        self._max_entries = max_entries

        # Statistics
        self._total_gets = 0
        self._total_sets = 0
        self._cache_hits = 0
        self._cache_misses = 0
        self._cleanup_count = 0
        self._auto_cleanup_interval = 100  # cleanup every 100 accesses

        logger.info(f"🚀 CacheManager initialized (max_entries={max_entries})")

    async def get(self, key: str, ttl: Optional[int] = None) -> Optional[Any]:
        """
        🔍 קבל ערך מה-Cache (אם קיים ולא פג תוקף)

        Args:
            key: מפתח ייחודי (לדוגמה: "standings_39_2024")
            ttl: TTL לבדיקה (אם לא סופק, לא בודק TTL)

        Returns:
            הנתונים אם קיימים ותקפים, אחרת None
        """
        async with self._lock:
            self._total_gets += 1

            # Auto cleanup every N accesses
            if self._total_gets % self._auto_cleanup_interval == 0:
                await self._cleanup_expired()

            if key not in self._cache:
                self._cache_misses += 1
                logger.debug(f"❌ Cache MISS: {key}")
                return None

            entry = self._cache[key]

            # Check if expired
            if entry.is_expired():
                self._cache_misses += 1
                logger.debug(f"⏰ Cache EXPIRED: {key} (age={entry.age_seconds():.0f}s, ttl={entry.ttl}s)")
                del self._cache[key]
                return None

            # Cache HIT!
            self._cache_hits += 1
            entry.hits += 1
            entry.last_access = datetime.now()

            logger.info(f"✅ Cache HIT: {key} (age={entry.age_seconds():.0f}s, hits={entry.hits})")
            return entry.data

    async def set(self, key: str, data: Any, ttl: int) -> None:
        """
        💾 שמור ערך ב-Cache

        Args:
            key: מפתח ייחודי
            data: נתונים לשמירה
            ttl: Time To Live בשניות
        """
        async with self._lock:
            self._total_sets += 1

            # Check memory limit
            if len(self._cache) >= self._max_entries:
                await self._cleanup_oldest()

            entry = CacheEntry(
                data=data,
                timestamp=datetime.now(),
                ttl=ttl
            )

            self._cache[key] = entry
            logger.info(f"💾 Cache SET: {key} (ttl={ttl}s, size={len(self._cache)})")

    async def delete(self, key: str) -> bool:
        """
        🗑️ מחק ערך ספציפי

        Returns:
            True אם נמחק, False אם לא קיים
        """
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                logger.info(f"🗑️ Cache DELETE: {key}")
                return True
            return False

    async def clear(self) -> int:
        """
        🧹 נקה את כל ה-Cache

        Returns:
            מספר הערכים שנמחקו
        """
        async with self._lock:
            count = len(self._cache)
            self._cache.clear()
            logger.info(f"🧹 Cache CLEARED: {count} entries removed")
            return count

    async def _cleanup_expired(self) -> int:
        """
        🧼 ניקוי אוטומטי של ערכים שפג תוקפם

        Returns:
            מספר הערכים שנמחקו
        """
        expired_keys = [
            key for key, entry in self._cache.items()
            if entry.is_expired()
        ]

        for key in expired_keys:
            del self._cache[key]

        if expired_keys:
            self._cleanup_count += 1
            logger.info(f"🧼 Auto cleanup #{self._cleanup_count}: {len(expired_keys)} expired entries removed")

        return len(expired_keys)

    async def _cleanup_oldest(self, count: int = 100) -> int:
        """
        🗑️ מחק את הערכים הכי ישנים (LRU - Least Recently Used)

        Args:
            count: כמה ערכים למחוק

        Returns:
            מספר הערכים שנמחקו
        """
        if not self._cache:
            return 0

        # Sort by last_access
        sorted_entries = sorted(
            self._cache.items(),
            key=lambda x: x[1].last_access
        )

        # Delete oldest
        deleted = 0
        for key, _ in sorted_entries[:count]:
            del self._cache[key]
            deleted += 1

        logger.warning(f"🗑️ Memory cleanup: {deleted} oldest entries removed (was {len(self._cache) + deleted})")
        return deleted

    def get_stats(self) -> dict:
        """
        📊 קבל סטטיסטיקות מפורטות

        Returns:
            dict עם כל הנתונים הסטטיסטיים
        """
        total_requests = self._cache_hits + self._cache_misses
        hit_ratio = (self._cache_hits / total_requests * 100) if total_requests > 0 else 0

        # Calculate memory usage (rough estimate)
        memory_mb = sum(
            len(json.dumps(entry.data)) if isinstance(entry.data, (dict, list)) else 100
            for entry in self._cache.values()
        ) / (1024 * 1024)

        return {
            "cache_size": len(self._cache),
            "max_entries": self._max_entries,
            "memory_usage_mb": round(memory_mb, 2),
            "total_gets": self._total_gets,
            "total_sets": self._total_sets,
            "cache_hits": self._cache_hits,
            "cache_misses": self._cache_misses,
            "hit_ratio": f"{hit_ratio:.1f}%",
            "cleanup_count": self._cleanup_count,
            "status": "🟢 Healthy" if hit_ratio > 60 else "🟡 Low efficiency"
        }

    def get_all_keys(self) -> list:
        """
        🔑 קבל רשימת כל המפתחות ב-Cache

        Returns:
            list של מפתחות
        """
        return list(self._cache.keys())

    def get_entry_metadata(self, key: str) -> Optional[dict]:
        """
        🔍 קבל metadata של ערך ספציפי

        Args:
            key: מפתח לבדיקה

        Returns:
            dict עם metadata או None אם לא קיים
        """
        if key not in self._cache:
            return None

        entry = self._cache[key]
        return {
            "key": key,
            **entry.to_dict()
        }


# 🌍 Global instance (singleton pattern)
# שימוש: from cache_manager import cache_manager
cache_manager = CacheManager(max_entries=1000)


# 🎯 Helper: TTL Constants (לשימוש קל)
class CacheTTL:
    """קבועים לזמני TTL נפוצים"""
    LIVE_MATCH = 30  # 30 seconds
    MATCH_DETAILS = 1800  # 30 minutes
    LAST_5_MATCHES = 10800  # 3 hours
    STANDINGS = 21600  # 6 hours
    H2H = 86400  # 24 hours
    STATIC = 604800  # 7 days


if __name__ == "__main__":
    """
    🧪 בדיקות יחידה
    """
    async def test_cache():
        print("🧪 Testing CacheManager...\n")

        cache = CacheManager(max_entries=5)

        # Test 1: Set and Get
        print("Test 1: Set and Get")
        await cache.set("test_key", {"value": 123}, ttl=5)
        result = await cache.get("test_key")
        assert result == {"value": 123}, "Failed: data mismatch"
        print("✅ Passed\n")

        # Test 2: Expiration
        print("Test 2: Expiration")
        await cache.set("expire_key", {"value": 456}, ttl=1)
        await asyncio.sleep(2)
        result = await cache.get("expire_key")
        assert result is None, "Failed: should be expired"
        print("✅ Passed\n")

        # Test 3: Cache HIT
        print("Test 3: Cache HIT")
        await cache.set("hit_key", {"value": 789}, ttl=10)
        result1 = await cache.get("hit_key")
        result2 = await cache.get("hit_key")
        assert result1 == result2, "Failed: inconsistent data"
        stats = cache.get_stats()
        assert stats["cache_hits"] >= 2, "Failed: hits not recorded"
        print(f"✅ Passed (hits={stats['cache_hits']})\n")

        # Test 4: Statistics
        print("Test 4: Statistics")
        stats = cache.get_stats()
        print(json.dumps(stats, indent=2, ensure_ascii=False))
        assert "hit_ratio" in stats, "Failed: missing hit_ratio"
        print("✅ Passed\n")

        print("🎉 All tests passed!")

    # Run tests
    asyncio.run(test_cache())
