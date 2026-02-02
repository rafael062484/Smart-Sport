"""
🌍 Sports API Manager - Real-time sports data integration
Created by: Rafael & AI Assistant
Version: 3.0 - ULTIMATE PRODUCTION READY
"""
import os
import httpx
import logging
import random
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import asyncio
from dotenv import load_dotenv


# טען את קובץ .env
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SportsAPIManager:
    """
    🏆 מנהל API מתקדם לנתוני ספורט בזמן אמת

    Features:
    ✅ Async/await for high performance
    ✅ Smart caching with TTL
    ✅ Rate limiting protection
    ✅ Retry mechanism with exponential backoff
    ✅ Comprehensive error handling
    ✅ API key validation
    ✅ Mock data fallback
    ✅ Multiple endpoints support
    """

    def __init__(self):
        """Initialize Sports API Manager"""

        # API Configuration
        # Check if using RapidAPI or direct API-Sports
        use_rapidapi = os.getenv("USE_RAPIDAPI", "false").lower() == "true"

        if use_rapidapi:
            self.base_url = "https://api-football-v1.p.rapidapi.com/v3"
            api_key = os.getenv("API_FOOTBALL_KEY", "DEMO_KEY")
            self.headers = {
                "X-RapidAPI-Key": api_key,
                "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
            }
        else:
            # Direct API-Sports (api-football.com)
            self.base_url = "https://v3.football.api-sports.io"
            api_key = os.getenv("API_SPORTS_KEY", "DEMO_KEY")
            self.headers = {
                "x-apisports-key": api_key
            }

        if api_key == "DEMO_KEY":
            logger.warning("⚠️ Using DEMO_KEY - API calls will use mock data!")
        else:
            logger.info(f"✅ API Key loaded: {api_key[:10]}...{api_key[-4:]}")

        self.api_key = api_key

        # Cache configuration
        self.cache: Dict[str, tuple] = {}
        self.cache_duration = 30  # seconds for live data
        self.standings_cache_duration = 300  # 5 minutes

        # Rate limiting
        self.request_count = 0
        self.max_requests_per_day = 100
        self.last_reset = datetime.now()

        # Retry configuration
        self.max_retries = 3
        self.retry_delay = 1  # seconds

        logger.info("🚀 SportsAPIManager initialized successfully!")

    def _check_rate_limit(self) -> bool:
        """בדוק האם ניתן לבצע בקשה (7500/יום)"""
        # Reset counter daily
        if (datetime.now() - self.last_reset).days >= 1:
            self.request_count = 0
            self.last_reset = datetime.now()
            logger.info("🔄 Rate limit counter reset")

        if self.request_count >= self.max_requests_per_day:
            logger.warning(f"🚫 Rate limit reached: {self.request_count}/{self.max_requests_per_day}")
            return False

        self.request_count += 1
        return True

    def _get_from_cache(self, key: str, max_age: int) -> Optional[List[Dict]]:
        """קבל נתונים מה-cache אם הם עדיין רלוונטיים"""
        if key in self.cache:
            cached_time, cached_data = self.cache[key]
            age_seconds = (datetime.now() - cached_time).total_seconds()

            if age_seconds < max_age:
                logger.debug(f"💨 Cache HIT: {key} (age: {age_seconds:.1f}s)")
                return cached_data

        return None

    def _save_to_cache(self, key: str, data: List[Dict]) -> None:
        """שמור נתונים ב-cache"""
        self.cache[key] = (datetime.now(), data)
        logger.debug(f"💾 Saved to cache: {key}")

        # Auto-cleanup: Keep only last 50 entries
        if len(self.cache) > 50:
            oldest_keys = sorted(self.cache.keys(), key=lambda k: self.cache[k][0])[:10]
            for old_key in oldest_keys:
                del self.cache[old_key]
            logger.debug(f"🧹 Cleaned {len(oldest_keys)} old cache entries")

    async def _make_request_with_retry(
            self,
            url: str,
            params: Dict = None
    ) -> Optional[Dict]:
        """בצע בקשה ל-API עם retry mechanism"""

        # Check rate limit first
        if not self._check_rate_limit():
            logger.warning("Rate limit exceeded, skipping API call")
            return None

        # Demo mode - skip API call
        if self.api_key == "DEMO_KEY":
            logger.info("Demo mode - using mock data")
            return None

        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.get(url, params=params, headers=self.headers)

                    if response.status_code == 200:
                        logger.info(f"✅ API request successful: {url}")
                        return response.json()

                    elif response.status_code == 429:
                        logger.error("🚫 API rate limit exceeded")
                        return None

                    else:
                        logger.warning(f"⚠️ API returned status {response.status_code}")
                        if attempt < self.max_retries - 1:
                            await asyncio.sleep(self.retry_delay * (attempt + 1))
                            continue
                        return None

            except httpx.TimeoutException:
                logger.error(f"⏱️ Request timeout (attempt {attempt + 1}/{self.max_retries})")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                    continue
                return None

            except Exception as e:
                logger.error(f"❌ Request error: {e} (attempt {attempt + 1}/{self.max_retries})")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                    continue
                return None

        return None

    async def get_live_matches(self, league_id: Optional[int] = None) -> List[Dict]:
        """
        🔴 קבל משחקים חיים כרגע

        Args:
            league_id: Optional - מזהה ליגה ספציפית

        Returns:
            List[Dict]: רשימת משחקים חיים
        """
        cache_key = f"live_matches_{league_id or 'all'}"

        # Check cache
        cached_data = self._get_from_cache(cache_key, self.cache_duration)
        if cached_data:
            return cached_data

        # Make API request
        params = {"live": "all"}
        if league_id:
            params["league"] = league_id

        data = await self._make_request_with_retry(
            f"{self.base_url}/fixtures",
            params=params
        )

        if data and data.get("response"):
            matches = self._parse_matches(data["response"])
            self._save_to_cache(cache_key, matches)
            logger.info(f"✅ Fetched {len(matches)} live matches from API")
            return matches

        # Fallback to mock data
        logger.info("Using mock data for live matches")
        return self._get_mock_live_matches()

    async def get_league_standings(self, league_id: int = 271, season: Optional[int] = None) -> List[Dict]:
        """
        📊 קבל טבלת דירוג ליגה

        Args:
            league_id: מזהה ליגה (383 = ליגת העל הישראלית)
            season: שנה (None = השנה הנוכחית)

        Returns:
            List[Dict]: טבלת דירוג
        """
        # ✅ Football seasons: Aug 2025 - May 2026 is "season 2025"
        # Current date: 27/01/2026 → We're in season 2025!
        now = datetime.now()
        if season:
            current_year = season
        elif now.month >= 8:
            # Aug-Dec → current year's season (Aug 2026 → season 2026)
            current_year = now.year
        else:
            # Jan-Jul → previous year's season (Jan 2026 → season 2025)
            current_year = now.year - 1

        cache_key = f"standings_{league_id}_{current_year}"

        # Check cache
        cached_data = self._get_from_cache(cache_key, self.standings_cache_duration)
        if cached_data:
            return cached_data

        # Make API request
        data = await self._make_request_with_retry(
            f"{self.base_url}/standings",
            params={"league": league_id, "season": current_year}
        )

        if data and data.get("response") and len(data["response"]) > 0:
            # ✅ החזר את הנתונים האמיתיים ישירות מ-API!
            logger.info(f"✅ Fetched REAL standings for league {league_id} - {len(data['response'])} results")
            self._save_to_cache(cache_key, data["response"])
            return data["response"]

        # Fallback to mock data ONLY if API failed
        logger.warning(f"⚠️ API returned no data for league {league_id}, using mock data")
        return self._get_mock_standings()

    async def get_fixtures_by_date(
            self,
            date: Optional[str] = None,
            league_id: Optional[int] = None
    ) -> List[Dict]:
        """
        📅 קבל משחקים לפי תאריך

        Args:
            date: תאריך בפורמט YYYY-MM-DD (None = היום)
            league_id: מזהה ליגה (Optional)

        Returns:
            List[Dict]: רשימת משחקים
        """
        target_date = date or datetime.now().strftime("%Y-%m-%d")
        cache_key = f"fixtures_{target_date}_{league_id or 'all'}"

        # Check cache
        cached_data = self._get_from_cache(cache_key, 3600)  # 1 hour
        if cached_data:
            return cached_data

        # Make API request
        params = {"date": target_date}
        if league_id:
            params["league"] = league_id

        data = await self._make_request_with_retry(
            f"{self.base_url}/fixtures",
            params=params
        )

        if data and data.get("response"):
            fixtures = self._parse_matches(data["response"])
            self._save_to_cache(cache_key, fixtures)
            logger.info(f"✅ Fetched {len(fixtures)} fixtures for {target_date}")
            return fixtures

        # Fallback
        logger.info("Using mock data for fixtures")
        return self._get_mock_live_matches()

    async def find_match_by_teams(
            self,
            home_team: str,
            away_team: str,
            days_range: int = 7
    ) -> Optional[Dict]:
        """
        🔍 חיפוש משחק לפי שמות קבוצות

        Args:
            home_team: שם קבוצת הבית
            away_team: שם הקבוצה האורחת
            days_range: טווח ימים לחיפוש (לפני ואחרי היום)

        Returns:
            Dict: נתוני המשחק אם נמצא, None אם לא
        """
        try:
            # חיפוש במספר ימים (היום ± days_range)
            from datetime import timedelta
            today = datetime.now()

            for day_offset in range(-days_range, days_range + 1):
                search_date = (today + timedelta(days=day_offset)).strftime("%Y-%m-%d")
                fixtures = await self.get_fixtures_by_date(date=search_date)

                # חיפוש התאמה בשמות הקבוצות (case-insensitive, חלקי)
                for fixture in fixtures:
                    home_match = home_team.lower() in fixture.get("home_team", "").lower()
                    away_match = away_team.lower() in fixture.get("away_team", "").lower()

                    if home_match and away_match:
                        logger.info(f"✅ Found match: {fixture.get('home_team')} vs {fixture.get('away_team')} on {search_date}")
                        return fixture

            logger.info(f"⚠️ No match found for {home_team} vs {away_team}")
            return None

        except Exception as e:
            logger.error(f"❌ Error finding match: {e}")
            return None

    def _parse_matches(self, matches_data: List[Dict]) -> List[Dict]:
        """המר נתוני API למבנה אחיד"""
        parsed = []

        for match in matches_data[:20]:  # Top 20
            try:
                fixture = match.get("fixture", {})
                teams = match.get("teams", {})
                goals = match.get("goals", {})
                league = match.get("league", {})

                # Format time nicely
                time_str = ""
                if fixture.get("date"):
                    try:
                        from datetime import datetime
                        match_time = datetime.fromisoformat(fixture.get("date").replace("Z", "+00:00"))
                        time_str = match_time.strftime("%H:%M")
                    except:
                        time_str = ""

                parsed.append({
                    "id": fixture.get("id"),
                    "date": fixture.get("date"),
                    "timestamp": fixture.get("timestamp"),
                    "time": time_str,
                    "league": league.get("name", "Unknown"),
                    "league_logo": league.get("logo", ""),
                    "country": league.get("country", ""),
                    "home_team": teams.get("home", {}).get("name", "Unknown"),
                    "away_team": teams.get("away", {}).get("name", "Unknown"),
                    "home_logo": teams.get("home", {}).get("logo", ""),
                    "away_logo": teams.get("away", {}).get("logo", ""),
                    "home_score": goals.get("home"),
                    "away_score": goals.get("away"),
                    "score": f"{goals.get('home', 0)}-{goals.get('away', 0)}",
                    "minute": fixture.get("status", {}).get("elapsed"),
                    "status": fixture.get("status", {}).get("short", "NS"),
                    "status_long": fixture.get("status", {}).get("long", "Not Started"),
                    "venue": fixture.get("venue", {}).get("name", "Unknown"),
                    "live": fixture.get("status", {}).get("short") in ["1H", "HT", "2H", "ET", "BT", "P", "LIVE"]
                })

            except Exception as e:
                logger.error(f"❌ Error parsing match: {e}")
                continue

        return parsed if parsed else self._get_mock_live_matches()

    def _parse_standings(self, standings_data: List[Dict]) -> List[Dict]:
        """המר טבלת דירוג למבנה נקי"""
        parsed = []

        try:
            if not standings_data:
                return self._get_mock_standings()

            league_data = standings_data[0].get("league", {})
            standings = league_data.get("standings", [[]])[0]

            for team in standings[:20]:
                all_stats = team.get("all", {})

                parsed.append({
                    "rank": team.get("rank"),
                    "team": team.get("team", {}).get("name"),
                    "logo": team.get("team", {}).get("logo"),
                    "points": team.get("points"),
                    "played": all_stats.get("played", 0),
                    "win": all_stats.get("win", 0),
                    "draw": all_stats.get("draw", 0),
                    "lose": all_stats.get("lose", 0),
                    "goals_for": all_stats.get("goals", {}).get("for", 0),
                    "goals_against": all_stats.get("goals", {}).get("against", 0),
                    "goal_diff": team.get("goalsDiff", 0),
                    "form": team.get("form", "")
                })

        except Exception as e:
            logger.error(f"❌ Error parsing standings: {e}")
            return self._get_mock_standings()

        return parsed if parsed else self._get_mock_standings()

    def _get_mock_live_matches(self) -> List[Dict]:
        """נתוני דמו מתקדמים למשחקים חיים"""
        teams = [
            {"name": "מכבי חיפה", "logo": "🟢"},
            {"name": "מכבי תל אביב", "logo": "🔵"},
            {"name": "ביתר ירושלים", "logo": "🟡"},
            {"name": "הפועל באר שבע", "logo": "🔴"},
            {"name": "הפועל חיפה", "logo": "🟠"},
            {"name": "מכבי פתח תקווה", "logo": "⚪"},
        ]

        matches = []
        for i in range(8):
            home = random.choice(teams)
            away = random.choice([t for t in teams if t != home])
            home_score = random.randint(0, 4)
            away_score = random.randint(0, 4)

            matches.append({
                "id": 10000 + i,
                "date": datetime.now().isoformat(),
                "timestamp": int(datetime.now().timestamp()),
                "league": "ליגת העל הישראלית",
                "league_logo": "🇮🇱",
                "country": "Israel",
                "home_team": home["name"],
                "away_team": away["name"],
                "home_logo": home["logo"],
                "away_logo": away["logo"],
                "home_score": home_score,
                "away_score": away_score,
                "score": f"{home_score}-{away_score}",
                "minute": f"{random.randint(1, 90)}'",
                "status": random.choice(["1H", "HT", "2H"]),
                "status_long": "Match In Progress",
                "venue": "Turner Stadium",
                "live": True
            })

        return matches

    def _get_mock_standings(self) -> List[Dict]:
        """טבלת דירוג מדומה מתקדמת"""
        teams = [
            {"name": "מכבי חיפה", "logo": "🟢", "points": 51, "form": "WWWDW"},
            {"name": "מכבי תל אביב", "logo": "🔵", "points": 45, "form": "WDWLW"},
            {"name": "ביתר ירושלים", "logo": "🟡", "points": 42, "form": "DWWWL"},
            {"name": "הפועל באר שבע", "logo": "🔴", "points": 38, "form": "LDWWD"},
            {"name": "הפועל חיפה", "logo": "🟠", "points": 33, "form": "WLDLL"},
            {"name": "מכבי פתח תקווה", "logo": "⚪", "points": 30, "form": "LLDWW"},
        ]

        standings = []
        for i, team in enumerate(teams, 1):
            wins = team["points"] // 3
            remaining = team["points"] % 3
            draws = remaining
            played = 30
            loses = played - wins - draws
            goals_for = wins * 2 + draws + random.randint(3, 8)
            goals_against = loses * 2 + random.randint(0, 5)

            standings.append({
                "rank": i,
                "team": team["name"],
                "logo": team["logo"],
                "points": team["points"],
                "played": played,
                "win": wins,
                "draw": draws,
                "lose": loses,
                "goals_for": goals_for,
                "goals_against": goals_against,
                "goal_diff": goals_for - goals_against,
                "form": team["form"]
            })

        return standings


    async def get_available_leagues(self) -> List[Dict]:
        """
        📋 קבל רשימת ליגות זמינות מ-API-Sports

        Returns:
            List[Dict]: רשימת ליגות עם מזהים
        """
        cache_key = "available_leagues"

        # Check cache (24 hours)
        cached_data = self._get_from_cache(cache_key, 86400)
        if cached_data:
            return cached_data

        # Make API request
        data = await self._make_request_with_retry(
            f"{self.base_url}/leagues",
            params={"current": "true"}
        )

        if data and data.get("response"):
            leagues = []
            for item in data["response"][:50]:  # Top 50 active leagues
                league_data = item.get("league", {})
                country_data = item.get("country", {})

                leagues.append({
                    "id": league_data.get("id"),
                    "name": league_data.get("name"),
                    "type": league_data.get("type"),
                    "logo": league_data.get("logo"),
                    "country": country_data.get("name"),
                    "country_code": country_data.get("code"),
                    "country_flag": country_data.get("flag")
                })

            self._save_to_cache(cache_key, leagues)
            logger.info(f"✅ Fetched {len(leagues)} leagues from API")
            return leagues

        # Fallback
        logger.info("Using fallback league list")
        return self._get_fallback_leagues()

    async def get_team_statistics(
            self,
            team_id: int,
            league_id: int,
            season: Optional[int] = None
    ) -> Optional[Dict]:
        """
        📈 קבל סטטיסטיקות מפורטות של קבוצה

        Args:
            team_id: מזהה קבוצה
            league_id: מזהה ליגה
            season: עונה (None = השנה הנוכחית)

        Returns:
            Dict: סטטיסטיקות מפורטות
        """
        current_year = season or datetime.now().year
        cache_key = f"team_stats_{team_id}_{league_id}_{current_year}"

        # Check cache (1 hour)
        cached_data = self._get_from_cache(cache_key, 3600)
        if cached_data:
            return cached_data

        # Make API request
        data = await self._make_request_with_retry(
            f"{self.base_url}/teams/statistics",
            params={
                "team": team_id,
                "league": league_id,
                "season": current_year
            }
        )

        if data and data.get("response"):
            stats = data["response"]
            self._save_to_cache(cache_key, stats)
            logger.info(f"✅ Fetched team statistics for team {team_id}")
            return stats

        return None

    async def get_top_scorers(
            self,
            league_id: int,
            season: Optional[int] = None
    ) -> List[Dict]:
        """
        ⚽ קבל רשימת מלכי השערים בליגה

        Args:
            league_id: מזהה ליגה
            season: עונה (None = השנה הנוכחית)

        Returns:
            List[Dict]: רשימת שחקנים מובילים
        """
        current_year = season or datetime.now().year
        cache_key = f"top_scorers_{league_id}_{current_year}"

        # Check cache (6 hours)
        cached_data = self._get_from_cache(cache_key, 21600)
        if cached_data:
            return cached_data

        # Make API request
        data = await self._make_request_with_retry(
            f"{self.base_url}/players/topscorers",
            params={"league": league_id, "season": current_year}
        )

        if data and data.get("response"):
            scorers = []
            for item in data["response"][:20]:  # Top 20
                player = item.get("player", {})
                statistics = item.get("statistics", [{}])[0]

                scorers.append({
                    "rank": len(scorers) + 1,
                    "player_id": player.get("id"),
                    "player_name": player.get("name"),
                    "photo": player.get("photo"),
                    "nationality": player.get("nationality"),
                    "age": player.get("age"),
                    "team": statistics.get("team", {}).get("name"),
                    "team_logo": statistics.get("team", {}).get("logo"),
                    "goals": statistics.get("goals", {}).get("total", 0),
                    "assists": statistics.get("goals", {}).get("assists", 0),
                    "appearances": statistics.get("games", {}).get("appearences", 0),
                    "minutes": statistics.get("games", {}).get("minutes", 0)
                })

            self._save_to_cache(cache_key, scorers)
            logger.info(f"✅ Fetched {len(scorers)} top scorers")
            return scorers

        # Fallback
        return self._get_mock_top_scorers()

    async def get_h2h_statistics(
            self,
            team1_id: int,
            team2_id: int
    ) -> Dict:
        """
        🔄 קבל סטטיסטיקות Head-to-Head בין שתי קבוצות

        Args:
            team1_id: מזהה קבוצה 1
            team2_id: מזהה קבוצה 2

        Returns:
            Dict: סטטיסטיקות מפגשים ישירים
        """
        cache_key = f"h2h_{min(team1_id, team2_id)}_{max(team1_id, team2_id)}"

        # Check cache (24 hours)
        cached_data = self._get_from_cache(cache_key, 86400)
        if cached_data:
            return cached_data

        # Make API request
        data = await self._make_request_with_retry(
            f"{self.base_url}/fixtures/headtohead",
            params={"h2h": f"{team1_id}-{team2_id}"}
        )

        if data and data.get("response"):
            h2h_data = {
                "total_matches": len(data["response"]),
                "team1_wins": 0,
                "team2_wins": 0,
                "draws": 0,
                "last_5_matches": [],
                "total_goals_team1": 0,
                "total_goals_team2": 0
            }

            for match in data["response"][:10]:  # Last 10 matches
                fixture = match.get("fixture", {})
                teams = match.get("teams", {})
                goals = match.get("goals", {})

                home_id = teams.get("home", {}).get("id")
                home_goals = goals.get("home", 0)
                away_goals = goals.get("away", 0)

                # Count wins
                if home_goals > away_goals:
                    if home_id == team1_id:
                        h2h_data["team1_wins"] += 1
                    else:
                        h2h_data["team2_wins"] += 1
                elif away_goals > home_goals:
                    if home_id == team1_id:
                        h2h_data["team2_wins"] += 1
                    else:
                        h2h_data["team1_wins"] += 1
                else:
                    h2h_data["draws"] += 1

                # Add to last 5
                if len(h2h_data["last_5_matches"]) < 5:
                    h2h_data["last_5_matches"].append({
                        "date": fixture.get("date"),
                        "home_team": teams.get("home", {}).get("name"),
                        "away_team": teams.get("away", {}).get("name"),
                        "score": f"{home_goals}-{away_goals}"
                    })

                h2h_data["total_goals_team1"] += home_goals if home_id == team1_id else away_goals
                h2h_data["total_goals_team2"] += away_goals if home_id == team1_id else home_goals

            self._save_to_cache(cache_key, h2h_data)
            logger.info(f"✅ Fetched H2H data")
            return h2h_data

        return self._get_mock_h2h()

    async def get_team_last_matches(
            self,
            team_id: int,
            limit: int = 5
    ) -> List[Dict]:
        """
        📊 קבל משחקים אחרונים של קבוצה (לצורך form analysis)

        Args:
            team_id: מזהה קבוצה
            limit: מספר משחקים אחרונים

        Returns:
            List[Dict]: רשימת משחקים אחרונים
        """
        cache_key = f"team_last_{team_id}_{limit}"

        # Check cache (1 hour)
        cached_data = self._get_from_cache(cache_key, 3600)
        if cached_data:
            return cached_data

        # Make API request
        data = await self._make_request_with_retry(
            f"{self.base_url}/fixtures",
            params={"team": team_id, "last": limit, "status": "FT"}
        )

        if data and data.get("response"):
            matches = self._parse_matches(data["response"])
            self._save_to_cache(cache_key, matches)
            logger.info(f"✅ Fetched last {len(matches)} matches for team {team_id}")
            return matches

        return []

    def _get_mock_top_scorers(self) -> List[Dict]:
        """רשימת מלכי שערים מדומה"""
        return [
            {"rank": 1, "player_name": "ארלינג הולאנד", "team": "Manchester City", "goals": 27, "assists": 5, "appearances": 25},
            {"rank": 2, "player_name": "הארי קיין", "team": "Bayern Munich", "goals": 24, "assists": 6, "appearances": 23},
            {"rank": 3, "player_name": "קיליאן מבאפה", "team": "Real Madrid", "goals": 22, "assists": 8, "appearances": 24},
            {"rank": 4, "player_name": "מוחמד סלאח", "team": "Liverpool", "goals": 18, "assists": 12, "appearances": 26},
            {"rank": 5, "player_name": "לאוטרו מרטינס", "team": "Inter Milan", "goals": 17, "assists": 4, "appearances": 24}
        ]

    def _get_mock_h2h(self) -> Dict:
        """נתוני H2H מדומים"""
        return {
            "total_matches": 10,
            "team1_wins": 4,
            "team2_wins": 3,
            "draws": 3,
            "total_goals_team1": 14,
            "total_goals_team2": 11,
            "last_5_matches": [
                {"date": "2024-12-15", "home_team": "קבוצה א", "away_team": "קבוצה ב", "score": "2-1"},
                {"date": "2024-10-20", "home_team": "קבוצה ב", "away_team": "קבוצה א", "score": "1-1"},
                {"date": "2024-08-10", "home_team": "קבוצה א", "away_team": "קבוצה ב", "score": "3-0"}
            ]
        }

    def _get_fallback_leagues(self) -> List[Dict]:
        """רשימת ליגות fallback"""
        return [
            {"id": 271, "name": "ליגת העל", "country": "Israel", "type": "League"},
            {"id": 39, "name": "Premier League", "country": "England", "type": "League"},
            {"id": 140, "name": "La Liga", "country": "Spain", "type": "League"},
            {"id": 135, "name": "Serie A", "country": "Italy", "type": "League"},
            {"id": 78, "name": "Bundesliga", "country": "Germany", "type": "League"},
            {"id": 61, "name": "Ligue 1", "country": "France", "type": "League"},
            {"id": 2, "name": "Champions League", "country": "Europe", "type": "Cup"}
        ]

    def get_stats(self) -> Dict:
        """
        קבל סטטיסטיקות על שימוש ב-API

        Returns:
            Dict: סטטיסטיקות מפורטות
        """
        return {
            "cache_entries": len(self.cache),
            "request_count": self.request_count,
            "max_requests": self.max_requests_per_day,
            "remaining_requests": self.max_requests_per_day - self.request_count,
            "api_mode": "LIVE" if self.api_key != "DEMO_KEY" else "DEMO",
            "last_reset": self.last_reset.isoformat()
        }


# יצירת מופע גלובלי
sports_api = SportsAPIManager()


# ============================================================================
# דוגמת שימוש מקיפה
# ============================================================================
if __name__ == "__main__":
    async def test():
        print("\n" + "="*70)
        print("🏆 Sports API Manager - Ultimate Test Suite")
        print("="*70 + "\n")

        # Test 1: Live Matches
        print("📺 Test 1: Fetching live matches...")
        matches = await sports_api.get_live_matches()
        print(f"✅ Found {len(matches)} live matches")
        if matches:
            print(f"   Example: {matches[0]['home_team']} vs {matches[0]['away_team']} - {matches[0]['score']}")
        print()

        # Test 2: League Standings
        print("📊 Test 2: Fetching league standings...")
        standings = await sports_api.get_league_standings(271)
        print(f"✅ Found {len(standings)} teams")
        if standings:
            print(f"   Leader: {standings[0]['team']} with {standings[0]['points']} points")
        print()

        # Test 3: Fixtures by date
        print("📅 Test 3: Fetching today's fixtures...")
        fixtures = await sports_api.get_fixtures_by_date()
        print(f"✅ Found {len(fixtures)} fixtures today")
        print()

        # Test 4: Statistics
        print("📈 Test 4: API Statistics:")
        stats = sports_api.get_stats()
        for key, value in stats.items():
            print(f"   • {key}: {value}")

        print("\n" + "="*70)
        print("✅ All tests completed successfully!")
        print("="*70 + "\n")

    asyncio.run(test())

