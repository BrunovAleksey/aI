from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import requests

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

        api_key = "xx"

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