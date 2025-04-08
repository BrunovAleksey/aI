from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import requests
import datetime
import random
import json
import os
from pathlib import Path



def load_jokes():
    try:
        jokes_file = Path("data") / "jokes.yml"
        with open(jokes_file, 'r', encoding='utf-8') as file:
            data = file.read()

            jokes = []
            in_jokes_section = False
            for line in data.split('\n'):
                if line.strip() == "jokes:":
                    in_jokes_section = True
                    continue
                if in_jokes_section and line.strip().startswith("- "):
                    joke = line[2:].strip().strip('"')
                    jokes.append(joke)
            return jokes
    except Exception as e:
        print(f"Error loading jokes: {e}")
        return [
            "Почему программисты путают Хэллоуин и Рождество? Потому что 31 Oct = 25 Dec.",
            "— Алло, это служба поддержки? — Да. — У меня проблема, я не могу... — Войдите в систему как администратор."
        ]


class ActionGetWeather(Action):
    def name(self) -> Text:
        return "action_get_weather"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        city = tracker.get_slot("city")
        if not city:
            dispatcher.utter_message(text="Не могу определить город для проверки погоды.")
            return []


        api_key = "64240a2d35ef1acd0374d6f6f530739d"

        try:
            base_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=ru"
            complete_url = f"{base_url}appid={api_key}&q={city}&units=metric&lang=ru"
            response = requests.get(complete_url)
            weather_data = response.json()

            if weather_data["cod"] != 200:
                dispatcher.utter_message(text=f"Не могу получить данные о погоде для {city}.")
                return [SlotSet("city", None)]

            main_data = weather_data["main"]
            temperature = main_data["temp"]
            feels_like = main_data["feels_like"]
            humidity = main_data["humidity"]
            weather_desc = weather_data["weather"][0]["description"].capitalize()

            message = (
                f"Сейчас в {city}:\n"
                f"Температура: {temperature}°C (ощущается как {feels_like}°C)\n"
                f"Влажность: {humidity}%\n"
                f"Описание: {weather_desc}"
            )

            dispatcher.utter_message(text=message)
        except Exception as e:
            print(f"Error getting weather: {e}")
            dispatcher.utter_message(text="Произошла ошибка при получении данных о погоде.")

        return [SlotSet("city", None)]


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

