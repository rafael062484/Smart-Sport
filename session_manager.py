"""
🔄 Session Manager - מערכת שמירת הקשר אוטומטית
מנהל את כל ההקשר של השיחה ושומר אותו ב-SESSION.json
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path


class SessionManager:
    def __init__(self):
        # נתיב לקובץ SESSION.json (בשורש הפרויקט)
        self.project_root = Path(__file__).parent.parent
        self.session_file = self.project_root / "SESSION.json"

        # אתחול - טען או צור חדש
        self.load_or_create()

    def load_or_create(self):
        """טען SESSION קיים או צור חדש"""
        if self.session_file.exists():
            try:
                with open(self.session_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        self.data = json.loads(content)
                    else:
                        # הקובץ ריק
                        self.data = self._create_default_session()
                        self.save()
                        print("🆕 SESSION חדש נוצר (הקובץ היה ריק)!")
                print("✅ SESSION קיים נטען בהצלחה!")
            except json.JSONDecodeError:
                # אם הקובץ קיים אבל פגום
                self.data = self._create_default_session()
                self.save()
                print("⚠️ SESSION פגום – נוצר SESSION חדש!")

            # וודא שיש את כל ה-keys החשובים
            if "project_state" not in self.data:
                self.data["project_state"] = {
                    "backend_running": False,
                    "frontend_pages": [],
                    "last_file_edited": None,
                    "last_endpoint_tested": None
                }
                self.save()
                print("🔧 project_state נוסף ל-SESSION")
        else:
            self.data = self._create_default_session()
            self.save()
            print("🆕 SESSION חדש נוצר!")

    def _create_default_session(self) -> Dict:
        """יצירת SESSION ברירת מחדל"""
        return {
            "last_updated": datetime.now().isoformat(),
            "session_id": 1,
            "current_task": {
                "title": "התחלת עבודה",
                "status": "idle",
                "started_at": datetime.now().isoformat()
            },
            "project_state": {
                "backend_running": False,
                "frontend_pages": [],
                "last_file_edited": None,
                "last_endpoint_tested": None
            },
            "conversation_history": [],
            "next_steps": [],
            "important_notes": [],
            "open_files": [],
            "blockers": [],
            "achievements_today": []
        }

    def save(self):
        """שמור SESSION לקובץ"""
        self.data["last_updated"] = datetime.now().isoformat()
        with open(self.session_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)


    def set_next_steps(self, steps: List[str]):
        """הגדר צעדים הבאים"""
        self.data["next_steps"] = steps
        self.save()

    def get_summary(self) -> Dict:
        """קבל סיכום מהיר"""
        return {
            "last_updated": self.data["last_updated"],
            "current_task": self.data["current_task"]["title"],
            "next_steps": self.data["next_steps"][:3],
            "recent_achievements": self.data["achievements_today"][-5:],
            "blockers": self.data["blockers"]
        }

    def get_full_context(self) -> str:
        """קבל הקשר מלא כטקסט"""
        context = f"""
🔄 SESSION RECOVERY - מצב נוכחי
================================

⏰ עדכון אחרון: {self.data['last_updated']}

📋 משימה נוכחית:
   {self.data['current_task']['title']} ({self.data['current_task']['status']})

🎯 צעדים הבאים:
"""
        for step in self.data['next_steps'][:5]:
            context += f"   • {step}\n"

        context += f"""
🏆 הישגים היום:
"""
        for achievement in self.data['achievements_today'][-5:]:
            context += f"   {achievement}\n"

        if self.data['blockers']:
            context += "\n⚠️ חסמים:\n"
            for blocker in self.data['blockers']:
                context += f"   {blocker}\n"

        context += f"""
📁 קבצים פתוחים:
   {', '.join(self.data['open_files']) if self.data['open_files'] else 'אין'}

💡 הערות חשובות:
"""
        for note in self.data['important_notes'][-3:]:
            context += f"   • {note}\n"

        return context


# Instance גלובלי
session_manager = SessionManager()
