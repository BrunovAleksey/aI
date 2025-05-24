from pathlib import Path
import random

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