"""
════════════════════════════════════════════════════════════════════
🏆 SMARTSPORTS PRO - DATABASE MODELS V2.0
מודלים מלאים למסד הנתונים עם תמיכה בתחזיות, משתמשים והגדרות
════════════════════════════════════════════════════════════════════
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    """מודל משתמש - מכיל את כל פרטי המשתמש"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # פרופיל פיננסי
    balance = Column(Float, default=0.0)
    is_premium = Column(Boolean, default=False)
    subscription_plan = Column(String(50), nullable=True)  # "free", "premium", "pro"
    subscription_start = Column(DateTime, nullable=True)  # תאריך תחילת מנוי

    # הרשאות וגישה
    role = Column(String(20), default="user")  # user, premium, owner
    is_internal = Column(Boolean, default=False)  # גישת מפתח

    # סטטיסטיקות
    total_predictions = Column(Integer, default=0)
    successful_predictions = Column(Integer, default=0)

    # קשרים לטבלאות אחרות
    settings = relationship("UserSettings", back_populates="user", uselist=False, cascade="all, delete-orphan")
    predictions = relationship("Prediction", back_populates="user", cascade="all, delete-orphan")
    saved_predictions = relationship("SavedPrediction", back_populates="user", cascade="all, delete-orphan")


class UserSettings(Base):
    """הגדרות משתמש - ערכת נושא, התראות וכו'"""
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    theme = Column(String(50), default="dark")
    notifications_enabled = Column(Boolean, default=True)
    language = Column(String(10), default="he")
    favorite_teams = Column(Text, nullable=True)  # JSON string של קבוצות מועדפות
    favorite_leagues = Column(Text, nullable=True)  # JSON string של ליגות מועדפות

    user = relationship("User", back_populates="settings")


class Prediction(Base):
    """מודל תחזית משחק - שמירת תחזיות שהמשתמש יצר"""
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # פרטי המשחק
    home_team = Column(String(255), nullable=False)
    away_team = Column(String(255), nullable=False)
    league = Column(String(100), nullable=True)

    # התחזית
    predicted_score = Column(String(20), nullable=False)  # לדוגמה: "2-1"
    confidence = Column(Integer, default=50)  # אחוז ביטחון 0-100

    # תוצאה אמיתית (יעודכן אחרי המשחק)
    actual_score = Column(String(20), nullable=True)
    is_correct = Column(Boolean, nullable=True)  # None = עדיין לא ידוע

    # מטא-דאטה
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    match_date = Column(DateTime, nullable=True)  # תאריך המשחק עצמו
    notes = Column(Text, nullable=True)  # הערות אישיות

    # קשר למשתמש
    user = relationship("User", back_populates="predictions")


class SavedPrediction(Base):
    """תחזיות שמורות מ-API חיצוני (לא תחזיות שהמשתמש יצר)"""
    __tablename__ = "saved_predictions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    match_id = Column(String(100))  # ID מה-API החיצוני
    prediction_data = Column(Text)  # JSON string עם כל הנתונים
    saved_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="saved_predictions")


class Match(Base):
    """מודל משחק - לשמירת מידע על משחקים (אופציונלי)"""
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String(100), unique=True, nullable=True)  # ID מ-API חיצוני

    home_team = Column(String(255), nullable=False)
    away_team = Column(String(255), nullable=False)
    league = Column(String(100), nullable=True)

    match_date = Column(DateTime, nullable=True)
    status = Column(String(50), default="scheduled")  # scheduled, live, finished

    home_score = Column(Integer, nullable=True)
    away_score = Column(Integer, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ActivityLog(Base):
    """לוג פעילות - מעקב אחר פעולות במערכת"""
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    action = Column(String(100), nullable=False)  # login, prediction, logout וכו'
    details = Column(Text, nullable=True)  # JSON עם פרטים נוספים
    ip_address = Column(String(50), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


