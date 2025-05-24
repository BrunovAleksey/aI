import sqlite3
import json
from datetime import datetime
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from typing import Any, Text, Dict, List

# Конфигурация базы данных
DB_PATH = "memory.db"
TABLE_NAME = "user_memory"


def init_db():
    """Инициализирует базу данных и таблицу для хранения пользовательских данных."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            user_id TEXT PRIMARY KEY,
            name TEXT,
            favorite_topic TEXT,
            last_seen TEXT,
            extra TEXT
        );
        """)
        conn.commit()


class DatabaseManager:
    """Вспомогательный класс для работы с базой данных."""

    @staticmethod
    def save_user_data(user_id: Text, name: Text, topic: Text, extra: Dict = None):
        """Сохраняет или обновляет данные пользователя."""
        extra = extra or {}
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                INSERT INTO {TABLE_NAME}(user_id, name, favorite_topic, last_seen, extra)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                  name=excluded.name,
                  favorite_topic=excluded.favorite_topic,
                  last_seen=excluded.last_seen,
                  extra=excluded.extra;
            """, (user_id, name, topic, datetime.utcnow().isoformat(), json.dumps(extra)))
            conn.commit()

    @staticmethod
    def load_user_data(user_id: Text) -> Dict:
        """Загружает данные пользователя по ID."""
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT name, favorite_topic, extra 
                FROM {TABLE_NAME} 
                WHERE user_id = ?
            """, (user_id,))
            row = cursor.fetchone()

        if row:
            name, topic, extra_json = row
            return {
                "name": name,
                "favorite_topic": topic,
                "extra": json.loads(extra_json) if extra_json else {}
            }
        return None


class ActionSaveUserMemory(Action):
    """Действие для сохранения информации о пользователе."""

    def name(self) -> Text:
        return "action_save_user_memory"

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        init_db()
        user_id = tracker.sender_id
        name = tracker.get_slot("name")
        topic = tracker.get_slot("favorite_topic")

        DatabaseManager.save_user_data(
            user_id=user_id,
            name=name,
            topic=topic
        )

        dispatcher.utter_message(text="Я запомнил информацию о вас.")
        return []


class ActionLoadUserMemory(Action):
    """Действие для загрузки сохраненной информации о пользователе."""

    def name(self) -> Text:
        return "action_load_user_memory"

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        init_db()
        user_id = tracker.sender_id
        user_data = DatabaseManager.load_user_data(user_id)

        events = []
        if user_data:
            name = user_data.get("name")
            dispatcher.utter_message(text=f"Снова привет{', ' + name if name else ''}!")

            # Устанавливаем слоты для дальнейшего использования
            events.extend([
                SlotSet("name", user_data.get("name")),
                SlotSet("favorite_topic", user_data.get("favorite_topic"))
            ])
        else:
            dispatcher.utter_message(text="Привет! Рад знакомству.")

        return events