"""
SMARTSPORTS – TITAN AI
CTO SPECIFICATION COMPLIANT PREDICTOR
VERSION: 1.0 – STANDARD MODE ONLY
"""

import os
import json
import re
from datetime import datetime
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenAI Configuration
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment")

from openai import OpenAI
client = OpenAI(api_key=OPENAI_KEY)

ENGINE_VERSION = "1.0-TITAN-STANDARD"


def get_match_prediction(home: str, away: str, league: str, date: str = None) -> Dict[str, Any]:
    """
    Generate football match prediction according to CTO specification.

    Returns structured JSON analysis in Hebrew.
    Acts as professional analyst, not bettor.
    """

    if date is None:
        date = datetime.utcnow().strftime("%Y-%m-%d")

    system_prompt = """אתה מנתח כדורגל מקצועי ברמה עולמית.

תפקידך: לספק ניתוח מקצועי, רגוע ואנליטי של משחקי כדורגל.

כללי זהב:
✔ שפה אנליטית מקצועית
✔ הסתברויות (לא הבטחות)
✔ טווחים (קרנות, כרטיסים)
✔ נימוק ברור לכל תחזית

אסור בהחלט:
✖ אימוג'ים
✖ סלנג
✖ לשון גוף ראשון ("אני חושב")
✖ קריאות לפעולה
✖ הבטחות או אחוזי זכייה

חובה להחזיר JSON תקין בלבד - ללא טקסט לפני או אחרי."""

    user_prompt = f"""נתח את המשחק הבא ותן תחזית מקצועית:

ליגה: {league}
תאריך: {date}
קבוצת בית: {home}
קבוצת חוץ: {away}

החזר JSON במבנה הבא בדיוק:

{{
  "match": {{
    "league": "{league}",
    "date": "{date}",
    "home_team": "{home}",
    "away_team": "{away}"
  }},

  "analysis": {{
    "match_overview": "פסקה אחת בלבד. ללא נקודות. הסבר את הקונטקסט של המשחק והלוגיקה.",
    "form": {{
      "home_team_form": "low | medium | high",
      "away_team_form": "low | medium | high",
      "momentum_edge": "home | away | none"
    }},
    "motivation": {{
      "home_team": "הסבר קצר",
      "away_team": "הסבר קצר"
    }},
    "pace_expectation": "low | medium | high"
  }},

  "prediction": {{
    "final_score": "X-X",
    "confidence_level": "low | medium | medium-high | high"
  }},

  "markets": {{
    "goals": {{
      "type": "Over | Under",
      "line": 2.5,
      "reason": "סיבה לוגית קצרה"
    }},
    "corners": {{
      "expected_range": "X-Y",
      "reason": "סיבה לוגית קצרה"
    }},
    "yellow_cards": {{
      "expected_range": "X-Y",
      "reason": "סיבה לוגית קצרה"
    }},
    "red_card": {{
      "probability": "low | medium | high",
      "expected": 0,
      "reason": "סיבה לוגית קצרה"
    }}
  }},

  "summary": {{
    "titan_verdict": "1–2 משפטים. ללא מידע חדש. סיכום אנליטי."
  }}
}}

דוגמה למבנה הפלט (LaLiga | 2026-01-10 | סלטה ויגו – ולנסיה):

{{
  "match": {{
    "league": "LaLiga",
    "date": "2026-01-10",
    "home_team": "סלטה ויגו",
    "away_team": "ולנסיה"
  }},

  "analysis": {{
    "match_overview": "ולנסיה מגיעה למשחק עם מוטיבציה גבוהה בעקבות מצבה בטבלה והצורך להתרחק מהקו האדום. מנגד, סלטה ויגו מגיעה במומנטום חיובי לאחר רצף של שלושה ניצחונות, עם ביטחון גבוה ויכולת התקפית משופרת. צפוי משחק שקול, עם שלבים של שליטה לשתי הקבוצות.",
    "form": {{
      "home_team_form": "high",
      "away_team_form": "medium",
      "momentum_edge": "home"
    }},
    "motivation": {{
      "home_team": "להמשיך מומנטום חיובי ולבסס מקום בטבלה",
      "away_team": "להתרחק מהקו האדום ולהשיג נקודות"
    }},
    "pace_expectation": "medium"
  }},

  "prediction": {{
    "final_score": "1-1",
    "confidence_level": "medium-high"
  }},

  "markets": {{
    "goals": {{
      "type": "Under",
      "line": 2.5,
      "reason": "שתי קבוצות טקטיות עם הגנה מסודרת"
    }},
    "corners": {{
      "expected_range": "7-9",
      "reason": "שתי קבוצות משחקות מהצד עם הגנה צפופה"
    }},
    "yellow_cards": {{
      "expected_range": "4-6",
      "reason": "משחק טעון עם חשיבות גבוהה לשתי הקבוצות"
    }},
    "red_card": {{
      "probability": "low",
      "expected": 0,
      "reason": "לא צפוי משחק אגרסיבי במיוחד"
    }}
  }},

  "summary": {{
    "titan_verdict": "שתי הקבוצות מגיעות עם רצון לנצח – האחת להמשיך מומנטום חיובי והשנייה לבסס את מקומה בליגה. המשחק צפוי להיות צמוד, טקטי וטעון, עם סיכוי גבוה לחלוקת נקודות."
  }}
}}

חשוב:
- הפלט חייב להיות JSON תקין בלבד
- ללא טקסט לפני או אחרי ה-JSON
- כל השדות חייבים להיות מלאים
- שפה: עברית מקצועית
- טון: רגוע, אנליטי, מקצועי
- ללא אימוג'ים לחלוטין
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.6,  # More conservative for consistent output
            max_tokens=2000
        )

        raw_content = response.choices[0].message.content
        data = _safe_json_parse(raw_content)

        # Validate structure
        _validate_response(data)

        # Add metadata
        data["metadata"] = {
            "engine_version": ENGINE_VERSION,
            "generated_at": datetime.utcnow().isoformat(),
            "mode": "STANDARD"
        }

        return {
            "success": True,
            "data": data
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "data": _fallback_response(home, away, league, date)
        }


def _safe_json_parse(content: str) -> Dict:
    """Parse JSON safely with automatic fixing"""
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        # Try to fix common issues
        fixed = content.strip()
        # Remove control characters
        fixed = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', fixed)
        # Extract JSON if wrapped in text
        json_match = re.search(r'\{.*\}', fixed, re.DOTALL)
        if json_match:
            fixed = json_match.group()
        try:
            return json.loads(fixed)
        except:
            raise ValueError("Failed to parse JSON response")


def _validate_response(data: Dict) -> None:
    """Validate response structure according to CTO spec"""
    required_keys = ["match", "analysis", "prediction", "markets", "summary"]
    for key in required_keys:
        if key not in data:
            raise ValueError(f"Missing required key: {key}")

    # Validate match section
    match_keys = ["league", "date", "home_team", "away_team"]
    for key in match_keys:
        if key not in data["match"]:
            raise ValueError(f"Missing match key: {key}")

    # Validate analysis section
    if "match_overview" not in data["analysis"]:
        raise ValueError("Missing match_overview in analysis")

    # Validate prediction section
    if "final_score" not in data["prediction"]:
        raise ValueError("Missing final_score in prediction")


def _fallback_response(home: str, away: str, league: str, date: str) -> Dict:
    """Fallback response if AI fails"""
    return {
        "match": {
            "league": league,
            "date": date,
            "home_team": home,
            "away_team": away
        },
        "analysis": {
            "match_overview": "ניתוח לא זמין כרגע. המערכת פועלת במצב מצומצם.",
            "form": {
                "home_team_form": "medium",
                "away_team_form": "medium",
                "momentum_edge": "none"
            },
            "motivation": {
                "home_team": "מוטיבציה סטנדרטית",
                "away_team": "מוטיבציה סטנדרטית"
            },
            "pace_expectation": "medium"
        },
        "prediction": {
            "final_score": "1-1",
            "confidence_level": "low"
        },
        "markets": {
            "goals": {
                "type": "Under",
                "line": 2.5,
                "reason": "ניתוח לא זמין"
            },
            "corners": {
                "expected_range": "6-8",
                "reason": "ניתוח לא זמין"
            },
            "yellow_cards": {
                "expected_range": "3-5",
                "reason": "ניתוח לא זמין"
            },
            "red_card": {
                "probability": "low",
                "expected": 0,
                "reason": "ניתוח לא זמין"
            }
        },
        "summary": {
            "titan_verdict": "המערכת פועלת במצב מצומצם. אנא נסה שוב מאוחר יותר."
        }
    }


def get_engine_version() -> str:
    """Return engine version"""
    return ENGINE_VERSION


def is_ai_online() -> bool:
    """Check if AI is available"""
    return OPENAI_KEY is not None and client is not None
