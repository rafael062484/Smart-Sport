"""
╔══════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                      ║
║     📊 CONFIDENCE SCORER - Phase 3                                                   ║
║                                                                                      ║
║     🎯 Purpose: Calculate probabilistic confidence scores for predictions            ║
║     📐 Approach: Metadata-driven, normalized factors (0-1)                           ║
║     🔬 Not marketing - real probability based on data quality                        ║
║                                                                                      ║
╚══════════════════════════════════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📚 Design Principles (CTO-Approved):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. **Separation of Concerns**
   - Confidence doesn't know how prediction was made
   - Only consumes: metadata + outputs
   - Clean interface: `from_prediction(prediction_result)`

2. **Normalization**
   - All factors ∈ [0, 1]
   - Enables weight changes without breaking formula
   - True explainability

3. **Tier-Aware ≠ Weight-Aware**
   - Same score calculation for Free/Premium
   - Different explainability depth
   - Premium gets full breakdown + confidence bands

4. **Formula (Baseline - v1.0)**
   ```
   confidence = (
       0.30 * data_completeness +
       0.25 * signal_agreement +
       0.25 * model_certainty +
       0.20 * cache_freshness
   )
   ```

5. **Classification**
   - 0.00-0.39: Low
   - 0.40-0.69: Medium
   - 0.70-1.00: High

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from dataclasses import dataclass
import logging
import re

# Setup logger
logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════════════════════════
# DATA CLASSES
# ══════════════════════════════════════════════════════════════════════════════════════

@dataclass
class ConfidenceFactor:
    """Single confidence factor with normalized value (0-1)"""
    name: str
    value: float  # Must be [0, 1]
    weight: float
    explanation: str

    def __post_init__(self):
        """Validate normalization"""
        if not 0 <= self.value <= 1:
            logger.warning(f"Factor {self.name} not normalized: {self.value}")
            self.value = max(0, min(1, self.value))


@dataclass
class ConfidenceScore:
    """Complete confidence assessment"""
    score: float  # Final weighted score [0, 1]
    level: str  # "Low", "Medium", "High"
    factors: Dict[str, ConfidenceFactor]
    explanation: str
    tier: str  # "free" or "premium"

    def to_dict(self, include_breakdown: bool = True) -> Dict[str, Any]:
        """
        Convert to dictionary

        Args:
            include_breakdown: If False, only return score + level (Free tier)
        """
        base = {
            "score": round(self.score, 3),
            "level": self.level,
            "explanation": self.explanation
        }

        if include_breakdown:
            base["factors"] = {
                name: {
                    "value": round(factor.value, 3),
                    "weight": factor.weight,
                    "explanation": factor.explanation
                }
                for name, factor in self.factors.items()
            }

        return base


# ══════════════════════════════════════════════════════════════════════════════════════
# CONFIDENCE SCORER CLASS
# ══════════════════════════════════════════════════════════════════════════════════════

class ConfidenceScorer:
    """
    Calculates confidence scores for predictions based on metadata

    Architecture:
    - Input: prediction_result (from ai_predictor.py)
    - Output: ConfidenceScore object
    - No side effects, pure function
    """

    # Weights (v1.0 - baseline, can be calibrated)
    WEIGHTS = {
        "data_completeness": 0.30,
        "signal_agreement": 0.25,
        "model_certainty": 0.25,
        "cache_freshness": 0.20
    }

    # Classification thresholds
    THRESHOLDS = {
        "low": (0.0, 0.39),
        "medium": (0.40, 0.69),
        "high": (0.70, 1.00)
    }

    def __init__(self):
        """Initialize scorer"""
        logger.info("🎯 ConfidenceScorer initialized (Phase 3)")

    # ─────────────────────────────────────────────────────────────────────────────────
    # MAIN ENTRY POINT
    # ─────────────────────────────────────────────────────────────────────────────────

    def from_prediction(
        self,
        prediction_result: Dict[str, Any],
        tier: str = "free"
    ) -> ConfidenceScore:
        """
        Calculate confidence score from prediction result

        Args:
            prediction_result: Output from ai_predictor.py with metadata
            tier: "free" or "premium" (affects explainability, not calculation)

        Returns:
            ConfidenceScore object
        """
        try:
            # Extract metadata
            metadata = prediction_result.get("metadata", {})
            prediction_text = prediction_result.get("prediction", "")

            # Calculate individual factors (all normalized to 0-1)
            factors = {
                "data_completeness": self._calculate_data_completeness(metadata),
                "cache_freshness": self._calculate_cache_freshness(metadata),
                "signal_agreement": self._calculate_signal_agreement(prediction_result),
                "model_certainty": self._calculate_model_certainty(prediction_text)
            }

            # Calculate weighted score
            score = sum(
                factor.value * factor.weight
                for factor in factors.values()
            )

            # Classify
            level = self._classify_score(score)

            # Generate explanation
            explanation = self._generate_explanation(score, level, factors, tier)

            return ConfidenceScore(
                score=score,
                level=level,
                factors=factors,
                explanation=explanation,
                tier=tier
            )

        except Exception as e:
            logger.error(f"❌ Confidence calculation error: {e}")
            return self._fallback_score(tier)

    # ─────────────────────────────────────────────────────────────────────────────────
    # FACTOR CALCULATIONS (All return ConfidenceFactor with normalized value)
    # ─────────────────────────────────────────────────────────────────────────────────

    def _calculate_data_completeness(self, metadata: Dict[str, Any]) -> ConfidenceFactor:
        """
        Calculate data completeness factor [0, 1]

        Based on Phase 2 metadata:
        - data_quality: "basic" (0.33), "standard" (0.66), "premium" (1.0)
        - api_calls_used: higher = more complete
        - data_sources: standings, form, h2h
        """
        try:
            # Get data quality from Phase 2
            data_quality = metadata.get("data_quality", "basic")
            quality_map = {
                "basic": 0.33,
                "standard": 0.66,
                "premium": 1.0
            }
            quality_score = quality_map.get(data_quality, 0.33)

            # Get completeness indicators
            completeness = metadata.get("data_completeness", {})
            sources = [
                completeness.get("standings", False),
                completeness.get("form", False),
                completeness.get("h2h", False)
            ]
            sources_ratio = sum(sources) / len(sources) if sources else 0

            # Weighted average
            value = 0.6 * quality_score + 0.4 * sources_ratio

            explanation = f"Data quality: {data_quality}, {sum(sources)}/3 sources available"

            return ConfidenceFactor(
                name="data_completeness",
                value=value,
                weight=self.WEIGHTS["data_completeness"],
                explanation=explanation
            )

        except Exception as e:
            logger.warning(f"Data completeness calculation failed: {e}")
            return ConfidenceFactor(
                name="data_completeness",
                value=0.5,
                weight=self.WEIGHTS["data_completeness"],
                explanation="Partial data available"
            )

    def _calculate_cache_freshness(self, metadata: Dict[str, Any]) -> ConfidenceFactor:
        """
        Calculate cache freshness factor [0, 1]

        Based on:
        - cache_hits: how many calls were cached
        - Time decay (if available)

        Fresh data = high confidence
        """
        try:
            cache_info = metadata.get("cache_usage", {})
            total_calls = cache_info.get("total_calls", 1)
            cache_hits = cache_info.get("cache_hits", 0)

            # More cache hits = fresher data (paradoxically, in our system)
            # Because Phase 2 cache has smart TTL
            cache_ratio = cache_hits / total_calls if total_calls > 0 else 0

            # For now, simple linear mapping
            # Can be enhanced with TTL decay later
            value = 0.7 + 0.3 * cache_ratio  # Base 0.7, bonus for cache hits

            explanation = f"{cache_hits}/{total_calls} requests served from cache"

            return ConfidenceFactor(
                name="cache_freshness",
                value=value,
                weight=self.WEIGHTS["cache_freshness"],
                explanation=explanation
            )

        except Exception as e:
            logger.warning(f"Cache freshness calculation failed: {e}")
            return ConfidenceFactor(
                name="cache_freshness",
                value=0.7,
                weight=self.WEIGHTS["cache_freshness"],
                explanation="Cache status unknown"
            )

    def _calculate_signal_agreement(self, prediction_result: Dict[str, Any]) -> ConfidenceFactor:
        """
        Calculate signal agreement factor [0, 1]

        Based on:
        - Consistency between different signals (home/away form, h2h, standings)
        - If multiple indicators point same direction = high agreement

        For now, placeholder - can be enhanced with actual signal parsing
        """
        try:
            # Check if prediction has strong indicators
            prediction_text = prediction_result.get("prediction", "").lower()

            # Count confidence indicators in prediction text
            strong_signals = [
                "ברור", "חזק", "גבוה", "סביר מאוד", "צפוי",
                "strong", "clear", "likely", "expected"
            ]
            weak_signals = [
                "אולי", "יתכן", "קשה לומר", "לא ברור", "מעורב",
                "maybe", "possible", "unclear", "mixed"
            ]

            strong_count = sum(1 for signal in strong_signals if signal in prediction_text)
            weak_count = sum(1 for signal in weak_signals if signal in prediction_text)

            # Simple heuristic
            if strong_count > weak_count:
                value = 0.7 + min(0.3, strong_count * 0.1)
            elif weak_count > strong_count:
                value = 0.4 - min(0.2, weak_count * 0.1)
            else:
                value = 0.6

            explanation = f"Signals aligned: {strong_count} strong, {weak_count} weak indicators"

            return ConfidenceFactor(
                name="signal_agreement",
                value=value,
                weight=self.WEIGHTS["signal_agreement"],
                explanation=explanation
            )

        except Exception as e:
            logger.warning(f"Signal agreement calculation failed: {e}")
            return ConfidenceFactor(
                name="signal_agreement",
                value=0.6,
                weight=self.WEIGHTS["signal_agreement"],
                explanation="Signal analysis unavailable"
            )

    def _calculate_model_certainty(self, prediction_text: str) -> ConfidenceFactor:
        """
        Calculate model certainty factor [0, 1]

        Based on:
        - Language confidence in GPT response
        - Presence of hedging language
        - Numeric predictions (if available)

        High certainty language = high confidence
        """
        try:
            text_lower = prediction_text.lower()

            # High certainty phrases
            high_certainty = [
                "בהחלט", "בטוח", "מאוד צפוי", "ללא ספק",
                "definitely", "certain", "highly likely", "confident"
            ]

            # Hedging phrases (low certainty)
            hedging = [
                "אולי", "יתכן", "לא בטוח", "קשה להעריך", "תלוי",
                "maybe", "might", "uncertain", "depends", "difficult to say"
            ]

            high_count = sum(1 for phrase in high_certainty if phrase in text_lower)
            hedge_count = sum(1 for phrase in hedging if phrase in text_lower)

            # Calculate certainty
            if high_count > hedge_count:
                value = 0.75 + min(0.25, high_count * 0.08)
            elif hedge_count > high_count:
                value = 0.45 - min(0.25, hedge_count * 0.08)
            else:
                value = 0.6

            explanation = f"Model confidence: {high_count} certain, {hedge_count} hedging phrases"

            return ConfidenceFactor(
                name="model_certainty",
                value=value,
                weight=self.WEIGHTS["model_certainty"],
                explanation=explanation
            )

        except Exception as e:
            logger.warning(f"Model certainty calculation failed: {e}")
            return ConfidenceFactor(
                name="model_certainty",
                value=0.6,
                weight=self.WEIGHTS["model_certainty"],
                explanation="Certainty analysis unavailable"
            )

    # ─────────────────────────────────────────────────────────────────────────────────
    # CLASSIFICATION & EXPLANATION
    # ─────────────────────────────────────────────────────────────────────────────────

    def _classify_score(self, score: float) -> str:
        """Classify score into Low/Medium/High"""
        if score < 0.40:
            return "Low"
        elif score < 0.70:
            return "Medium"
        else:
            return "High"

    def _generate_explanation(
        self,
        score: float,
        level: str,
        factors: Dict[str, ConfidenceFactor],
        tier: str
    ) -> str:
        """
        Generate human-readable explanation

        Free tier: Simple explanation
        Premium tier: Detailed breakdown
        """
        if tier == "premium":
            # Detailed explanation
            top_factor = max(factors.values(), key=lambda f: f.value * f.weight)
            bottom_factor = min(factors.values(), key=lambda f: f.value * f.weight)

            return (
                f"{level} confidence ({score:.2f}) based on analysis. "
                f"Strongest factor: {top_factor.name} ({top_factor.value:.2f}). "
                f"Weakest factor: {bottom_factor.name} ({bottom_factor.value:.2f})."
            )
        else:
            # Simple explanation (Free tier)
            return f"{level} confidence prediction based on available data quality and model analysis."

    def _fallback_score(self, tier: str) -> ConfidenceScore:
        """Fallback score if calculation fails"""
        return ConfidenceScore(
            score=0.5,
            level="Medium",
            factors={},
            explanation="Confidence score unavailable - using default",
            tier=tier
        )


# ══════════════════════════════════════════════════════════════════════════════════════
# MODULE INITIALIZATION
# ══════════════════════════════════════════════════════════════════════════════════════

# Global scorer instance
_scorer = ConfidenceScorer()

def calculate_confidence(
    prediction_result: Dict[str, Any],
    tier: str = "free"
) -> ConfidenceScore:
    """
    Main entry point for confidence calculation

    Args:
        prediction_result: Prediction output from ai_predictor.py
        tier: "free" or "premium"

    Returns:
        ConfidenceScore object
    """
    return _scorer.from_prediction(prediction_result, tier)


# ══════════════════════════════════════════════════════════════════════════════════════
# TESTING (if run directly)
# ══════════════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Test with mock prediction
    mock_prediction = {
        "prediction": "צפוי ניצחון חזק לקבוצת הבית עם יתרון ברור בכל הפרמטרים",
        "metadata": {
            "data_quality": "premium",
            "data_completeness": {
                "standings": True,
                "form": True,
                "h2h": True
            },
            "cache_usage": {
                "total_calls": 5,
                "cache_hits": 3
            }
        }
    }

    # Test Free tier
    confidence_free = calculate_confidence(mock_prediction, tier="free")
    print("\n🆓 Free Tier:")
    print(confidence_free.to_dict(include_breakdown=False))

    # Test Premium tier
    confidence_premium = calculate_confidence(mock_prediction, tier="premium")
    print("\n💎 Premium Tier:")
    print(confidence_premium.to_dict(include_breakdown=True))
