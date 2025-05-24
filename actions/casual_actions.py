from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import datetime
import random
from .db_utils import load_jokes

class ActionGetTime(Action):
    def name(self) -> Text:
        return "action_get_time"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        now = datetime.datetime.now()
        current_time = now.strftime("%H:%M")
        current_date = now.strftime("%d.%m.%Y")

        message = f"Сейчас {current_time}, {current_date}"
        dispatcher.utter_message(text=message)

        return []

class ActionTellJoke(Action):
    def __init__(self):
        self.jokes = load_jokes()

    def name(self) -> Text:
        return "action_tell_joke"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        if not self.jokes:
            dispatcher.utter_message(text="Извините, у меня закончились анекдоты.")
            return []

        joke = random.choice(self.jokes)
        dispatcher.utter_message(text=joke)

        return []

class ActionAnalyzeMood(Action):
    def name(self) -> Text:
        return "action_analyze_mood"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        user_message = tracker.latest_message.get("text")

        if not user_message:
            dispatcher.utter_message(text="Я не совсем понял ваше настроение.")
            return []

        mood = self.detect_mood(user_message)
        response = self.generate_mood_response(mood)

        dispatcher.utter_message(text=response)
        return []

    def detect_mood(self, text: Text) -> Text:
        text_lower = text.lower()

        positive_words = ["хорошо", "отлично", "прекрасно", "радост", "счастлив", "ура", "люблю", "классно",
                          "замечательно"]
        negative_words = ["плохо", "ужасно", "грустно", "несчаст", "тоскливо", "разочарован", "устал", "бесит"]

        positive_count = sum(word in text_lower for word in positive_words)
        negative_count = sum(word in text_lower for word in negative_words)

        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"

    def generate_mood_response(self, mood: Text) -> Text:
        responses = {
            "positive": [
                "Похоже, у вас отличное настроение! 😊",
                "Ваши слова звучат очень позитивно!",
                "Я чувствую вашу радость! Так держать!"
            ],
            "negative": [
                "Кажется, вам сейчас нелегко... 😔",
                "Похоже, у вас сложный период. Надеюсь, скоро станет лучше.",
                "Ваше настроение кажется подавленным. Если нужно поговорить - я здесь."
            ],
            "neutral": [
                "Ваше настроение кажется ровным. Все в порядке?",
                "Не могу точно определить ваше настроение. Хотите рассказать подробнее?",
                "Похоже, у вас обычный день. Надеюсь, он станет еще лучше!"
            ]
        }
        return random.choice(responses[mood])