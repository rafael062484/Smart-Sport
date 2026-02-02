FROM python:3.11-slim

WORKDIR /app

# תלויות מערכת בסיסיות
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential && rm -rf /var/lib/apt/lists/*

# העתקת תלויות
COPY requirements.txt ./
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# העתקת קבצי הפרויקט
COPY backend ./backend
COPY frontend ./frontend

WORKDIR /app/backend

# חשיפת פורט והפעלה
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]

# הערה: יש לוודא שקובץ requirements.txt כולל את כל התלויות הדרושות לפרויקט.
# כמו כן, יש להתאים את הפקודה ב-CMD בהתאם למבנה האפליקציה שלכם.
# לדוגמה, אם שם הקובץ הראשי שונה או אם יש צורך בפרמטרים נוספים.
# לדוגמה, אם אתם משתמשים ב-Django במקום FastAPI, יש לשנות את הפקודה בהתאם.
# לדוגמה:
# CMD ["gunicorn", "backend.wsgi:application", "--bind", "0.0.0.0:8000"]
# יש לוודא שהקבצים והספריות המתאימות נמצאים במקומות הנכונים בפרויקט.
# כמו כן, יש לוודא שהקבצים frontend ו-backend קיימים במבנה המתאים בפרויקט.

# ניתן להוסיף שלבים נוספים לבניית ה-frontend אם יש צורך בכך.
# לדוגמה, אם ה-frontend מבוסס על React או Vue, ניתן להוסיף שלבים לבנייתו לפני העתקתו.
# לדוגמה:
# WORKDIR /app/frontend
# RUN npm install && npm run build
# ואז להעתיק את קבצי הבנייה ל-backend אם יש צורך בכך.
# לדוגמה:
# COPY --from=frontend-build /app/frontend/build /app/backend/static
# יש להתאים את השלבים בהתאם לטכנולוגיות והצרכים של הפרויקט שלכם.
