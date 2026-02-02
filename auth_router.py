"""
🔐 Authentication Router

אחראי על endpoints של אימות משתמשים - התחברות והרשמה.

Endpoints:
---------
- POST /api/register    → הרשמת משתמש חדש  
- POST /api/login       → התחברות משתמש קיים

Created: 2026-01-09
Author: Claude Code
"""

from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from pydantic import BaseModel, EmailStr, Field

# יצירת Router
router = APIRouter(tags=["Authentication"])


# ═══════════════════════════════════════════════════════════════════════════════
# MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class UserRegisterRequest(BaseModel):
    """📝 בקשת הרשמה"""
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)


class UserLoginRequest(BaseModel):
    """🔐 בקשת התחברות"""
    email: EmailStr
    password: str


# ═══════════════════════════════════════════════════════════════════════════════
# AUTH ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@router.post("/api/register")
async def register_user(
        request: Request,
        user_data: UserRegisterRequest = None
):
    """📝 הרשמת משתמש חדש"""
    from backend.app import (
        get_db, hash_password, create_access_token,
        User, UserSettings, logger
    )
    
    # קבלת DB session
    db = next(get_db())
    
    try:
        # Parse body אם צריך
        if user_data is None:
            try:
                body = await request.json()
                user_data = UserRegisterRequest(**body)
            except Exception as e:
                logger.error(f"❌ Register parse error: {e}")
                raise HTTPException(status_code=422, detail="נתוני הרשמה לא תקינים")
        
        # בדיקת אימייל קיים
        existing = db.query(User).filter(User.email == user_data.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="כתובת האימייל כבר רשומה")
        
        # יצירת משתמש
        new_user = User(
            username=user_data.email,
            email=user_data.email,
            password_hash=hash_password(user_data.password),
            full_name=user_data.name,
            created_at=datetime.now(timezone.utc)
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # יצירת הגדרות
        user_settings = UserSettings(
            user_id=new_user.id,
            theme="dark",
            notifications_enabled=True,
            language="he"
        )
        db.add(user_settings)
        db.commit()
        
        # יצירת token
        token = create_access_token({"sub": new_user.email, "user_id": new_user.id})
        
        logger.info(f"✅ New user registered: {new_user.email}")
        
        return {
            "success": True,
            "message": "נרשמת בהצלחה!",
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": new_user.id,
                "name": new_user.full_name,
                "email": new_user.email,
                "is_premium": new_user.is_premium,
                "subscription": new_user.subscription_plan or "free",
                "subscription_expiry": new_user.subscription_start.isoformat() if new_user.subscription_start else None
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Register error: {e}")
        raise HTTPException(status_code=500, detail="שגיאה ביצירת המשתמש")
    finally:
        db.close()


@router.post("/api/login")
async def login_user(
        request: Request,
        login_data: UserLoginRequest = None
):
    """🔐 התחברות משתמש"""
    from backend.app import (
        get_db, verify_password, create_access_token, log_activity,
        User, logger
    )
    
    # קבלת DB session
    db = next(get_db())
    
    try:
        # Parse body אם צריך
        if login_data is None:
            try:
                body = await request.json()
                login_data = UserLoginRequest(**body)
            except Exception as e:
                logger.error(f"❌ Login parse error: {e}")
                raise HTTPException(status_code=422, detail="נתוני התחברות לא תקינים")
        
        user = db.query(User).filter(User.email == login_data.email).first()

        if not user or not verify_password(login_data.password, user.password_hash):
            raise HTTPException(status_code=401, detail="אימייל או סיסמה שגויים")
        
        log_activity(
            db, "login", user.id,
            ip_address=request.client.host if request.client else None
        )
        
        token = create_access_token({"sub": user.email, "user_id": user.id})
        
        logger.info(f"✅ User logged in: {login_data.email}")
        
        return {
            "success": True,
            "message": "התחברת בהצלחה!",
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "name": user.full_name or user.username,
                "email": user.email,
                "is_premium": user.is_premium,
                "subscription": user.subscription_plan or "free",
                "subscription_expiry": user.subscription_start.isoformat() if user.subscription_start else None
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Login error: {e}")
        raise HTTPException(status_code=500, detail="שגיאה בהתחברות")
    finally:
        db.close()
