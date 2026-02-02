"""
════════════════════════════════════════════════════════════════════
🔐 SMARTSPORTS - API KEYS & CONFIGURATION MANAGEMENT
Centralized API key management with Pydantic Settings
════════════════════════════════════════════════════════════════════
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class APIKeys(BaseSettings):
    """
    🔑 Centralized API Keys Management

    All external service keys should be managed here.
    Keys are loaded from .env file automatically.
    """

    # ─────────────────────────────────────────────────────────────────────────────
    # 🤖 OpenAI Configuration
    # ─────────────────────────────────────────────────────────────────────────────
    openai_api_key: str = Field(
        default="",
        description="OpenAI API key for TITAN prediction engine"
    )
    use_openai: bool = Field(
        default=True,
        description="Enable/disable OpenAI (fallback to logic-based predictions)"
    )

    # ─────────────────────────────────────────────────────────────────────────────
    # ⚽ Sports Data API Configuration
    # ─────────────────────────────────────────────────────────────────────────────
    api_sports_key: str = Field(
        default="",
        description="API-Sports key for live match data"
    )
    use_rapidapi: bool = Field(
        default=False,
        description="Use RapidAPI (true) or direct API-Sports (false)"
    )

    # ─────────────────────────────────────────────────────────────────────────────
    # 🔐 Security Keys
    # ─────────────────────────────────────────────────────────────────────────────
    secret_key: str = Field(
        default="",
        description="JWT secret key (MUST be set in production)"
    )

    # ─────────────────────────────────────────────────────────────────────────────
    # 📊 Monitoring & Analytics (Optional)
    # ─────────────────────────────────────────────────────────────────────────────
    sentry_dsn: Optional[str] = Field(
        default=None,
        description="Sentry DSN for error tracking"
    )

    # ─────────────────────────────────────────────────────────────────────────────
    # 💾 Database
    # ─────────────────────────────────────────────────────────────────────────────
    database_url: str = Field(
        default="sqlite:///./smartsports.db",
        description="Database connection URL"
    )

    # ─────────────────────────────────────────────────────────────────────────────
    # 🌍 Environment
    # ─────────────────────────────────────────────────────────────────────────────
    environment: str = Field(
        default="development",
        description="Environment: development, staging, production"
    )
    debug: bool = Field(
        default=True,
        description="Debug mode"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"

    def is_production(self) -> bool:
        """Check if running in production"""
        return self.environment.lower() == "production"

    def has_openai(self) -> bool:
        """Check if OpenAI is configured"""
        return bool(self.openai_api_key and self.openai_api_key.startswith("sk-"))

    def has_sports_api(self) -> bool:
        """Check if Sports API is configured"""
        return bool(self.api_sports_key)

    def validate_production_keys(self) -> dict:
        """
        Validate that all critical keys are set for production

        Returns:
            dict: {"valid": bool, "missing": list}
        """
        missing = []

        if self.is_production():
            if not self.secret_key or self.secret_key == "some_very_long_random_string_here":
                missing.append("SECRET_KEY")

            if not self.has_openai():
                missing.append("OPENAI_API_KEY")

            if not self.has_sports_api():
                missing.append("API_SPORTS_KEY")

        return {
            "valid": len(missing) == 0,
            "missing": missing,
            "environment": self.environment
        }


# ═══════════════════════════════════════════════════════════════════════════════
# Global Instance
# ═══════════════════════════════════════════════════════════════════════════════

# Create a singleton instance
_api_keys_instance: Optional[APIKeys] = None


def get_api_keys() -> APIKeys:
    """
    Get API keys singleton instance

    Returns:
        APIKeys: Configured API keys instance
    """
    global _api_keys_instance
    if _api_keys_instance is None:
        _api_keys_instance = APIKeys()
    return _api_keys_instance


# ═══════════════════════════════════════════════════════════════════════════════
# Utility Functions
# ═══════════════════════════════════════════════════════════════════════════════

def get_openai_key() -> str:
    """Get OpenAI API key"""
    return get_api_keys().openai_api_key


def get_sports_api_key() -> str:
    """Get Sports API key"""
    return get_api_keys().api_sports_key


def get_secret_key() -> str:
    """Get JWT secret key"""
    return get_api_keys().secret_key


def is_production() -> bool:
    """Check if running in production"""
    return get_api_keys().is_production()


# ═══════════════════════════════════════════════════════════════════════════════
# Example Usage
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("🔐 API Keys Configuration Check")
    print("=" * 70)

    keys = get_api_keys()

    print(f"\n📊 Environment: {keys.environment}")
    print(f"🐛 Debug Mode: {keys.debug}")
    print(f"\n✅ OpenAI Configured: {keys.has_openai()}")
    print(f"✅ Sports API Configured: {keys.has_sports_api()}")

    if keys.is_production():
        print("\n🚨 PRODUCTION MODE - Validating keys...")
        validation = keys.validate_production_keys()

        if validation["valid"]:
            print("✅ All production keys are set!")
        else:
            print(f"❌ Missing keys: {', '.join(validation['missing'])}")
    else:
        print("\n💡 Development mode - some keys may be optional")

    print("\n" + "=" * 70)
