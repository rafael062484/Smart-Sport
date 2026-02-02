@echo off
REM ==========================================================
REM 🔥 SmartSports AI - Run Full Server
REM ==========================================================

REM הצגת הודעה
echo Starting SmartSports AI Server...
echo.

REM מעבר לתיקיית backend
cd backend

REM הפעלת Virtual Environment
if exist ..\.venv\Scripts\activate.bat (
    call ..\.venv\Scripts\activate.bat
) else (
    echo ERROR: Virtual environment not found!
    pause
    exit /b
)

REM התקנת חבילות דרושות (אם צריך)
pip install --upgrade pip
pip install fastapi uvicorn pillow

REM הרצת השרת
echo Launching server...
uvicorn app:app --reload --host 127.0.0.1 --port 8000

pause
