import os
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional

# ---------------------------------------------------------
# הגדרות אבטחה
# שינינו את האלגוריתם ל-pbkdf2_sha256 כדי למנוע את הבאג עם bcrypt
# ---------------------------------------------------------
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# קריאת SECRET_KEY ממשתני סביבה - חובה!
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-CHANGE-IN-PRODUCTION")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# אזהרה אם משתמשים ב-default key
if SECRET_KEY == "dev-secret-key-CHANGE-IN-PRODUCTION":
    import warnings
    warnings.warn(
        "⚠️  WARNING: Using default SECRET_KEY! Set SECRET_KEY in .env for production!",
        RuntimeWarning,
        stacklevel=2
    )

def hash_password(password: str) -> str:
    """
    מקבל סיסמה רגילה ומחזיר סיסמה מוצפנת (Hash).
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    בודק האם סיסמה רגילה תואמת לסיסמה המוצפנת.
    """
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    יוצר טוקן גישה (JWT) שמשמש לזיהוי המשתמש בבקשות הבאות.

    Security: Uses timezone-aware datetime for proper token expiration.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str):
    """
    מפענח את הטוקן ומחזיר את המידע שבתוכו (כמו שם המשתמש).
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.JWTError:
        return None
