"""
════════════════════════════════════════════════════════════════════
💾 SMARTSPORTS - Database Configuration (Production-Ready)
Enhanced with connection pooling, WAL mode, and error handling
════════════════════════════════════════════════════════════════════
"""

import os
from pathlib import Path
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from models import Base
from dotenv import load_dotenv

# Load .env file from project root (parent of backend/)
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Load database URL from environment
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./smartsports.db"
)

# Determine if using SQLite
is_sqlite = SQLALCHEMY_DATABASE_URL.startswith("sqlite")

# ═══════════════════════════════════════════════════════════════════════════════
# Engine Configuration (optimized for production)
# ═══════════════════════════════════════════════════════════════════════════════

if is_sqlite:
    # SQLite configuration with WAL mode and connection pooling
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={
            "check_same_thread": False,
            "timeout": 15  # 15 seconds timeout for busy database
        },
        pool_pre_ping=True,  # Test connections before using
        echo=False  # Set to True for SQL query logging in development
    )

    # Enable WAL (Write-Ahead Logging) mode for better concurrency
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")  # Faster writes
        cursor.execute("PRAGMA cache_size=-64000")  # 64MB cache
        cursor.execute("PRAGMA temp_store=MEMORY")  # Use memory for temp tables
        cursor.close()

else:
    # PostgreSQL/MySQL configuration
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        pool_size=10,  # Connection pool size
        max_overflow=20,  # Max connections above pool_size
        pool_pre_ping=True,  # Test connections
        pool_recycle=3600,  # Recycle connections after 1 hour
        echo=False
    )

# ═══════════════════════════════════════════════════════════════════════════════
# Session Configuration
# ═══════════════════════════════════════════════════════════════════════════════

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# ═══════════════════════════════════════════════════════════════════════════════
# Database Initialization
# ═══════════════════════════════════════════════════════════════════════════════

def init_db():
    """
    Initialize database - create all tables

    Safe to call multiple times (won't recreate existing tables)
    """
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        raise


def get_db_info():
    """
    Get database connection information

    Returns:
        dict: Database type, URL (sanitized), and status
    """
    db_type = "PostgreSQL" if "postgresql" in SQLALCHEMY_DATABASE_URL else \
              "MySQL" if "mysql" in SQLALCHEMY_DATABASE_URL else \
              "SQLite"

    # Sanitize URL (hide password)
    safe_url = SQLALCHEMY_DATABASE_URL
    if "@" in safe_url:
        parts = safe_url.split("@")
        credentials = parts[0].split("//")[1]
        if ":" in credentials:
            user = credentials.split(":")[0]
            safe_url = safe_url.replace(credentials, f"{user}:****")

    return {
        "type": db_type,
        "url": safe_url,
        "is_sqlite": is_sqlite,
        "pool_size": getattr(engine.pool, 'size', lambda: 'N/A')()
    }

