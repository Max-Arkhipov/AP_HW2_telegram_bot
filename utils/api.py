import requests
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

API_KEY = os.getenv("API_KEY")

def get_temp(city):
    """
    Получает текущую температуру для указанного города с использованием OpenWeather API.
    """
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Проверяем статус ответа
        data = response.json()
        return {"temp": data["main"]["temp"], "status": 200}  # Возвращаем температуру и статус
    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 404:
            return {"error": "Город не найден", "status": 404}
        if response.status_code == 401:
            return {"error": "Неверный API ключ", "status": 401}
        return {"error": str(http_err), "status": response.status_code}
    except Exception as err:
        return {"error": f"Ошибка: {err}", "status": 500}