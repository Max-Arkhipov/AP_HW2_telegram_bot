import requests
import os
from difflib import SequenceMatcher

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


def get_food(product_name):
    """
    Получение информации о калорийности продукта с оптимизацией запроса.

    :param product_name: Название продукта для поиска.
    :return: Словарь с названием продукта и калорийностью, либо None.
    """
    base_url = "https://world.openfoodfacts.org/cgi/search.pl"
    search_terms = product_name

    params = {
        "action": "process",
        "search_terms": search_terms,
        "json": "true",
        "fields": "product_name,nutriments",  # Только нужные поля
        "page_size": 10,  # Ограничиваем выборку
        "lc": "ru",  # Ограничиваем выборку русским языком
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Проверяем статус ответа
        data = response.json()
        products = data.get('products', [])
        if not products:
            return {"error": "Продукты не найдены.", "status": 204}

        # Фильтруем продукты с отсутствующими данными о калорийности
        valid_products = [
            p for p in products
            if p.get('nutriments', {}).get('energy-kcal_100g') is not None
        ]
        if not valid_products:
            return {"error": "Нет продуктов с данными о калорийности.", "status": 204}

        # Сортируем продукты по степени совпадения с запросом
        valid_products = sorted(
            valid_products,
            key=lambda p: SequenceMatcher(None, product_name.lower(), p.get('product_name', '').lower()).ratio(),
            reverse=True
        )

        message = ""
        for idx, product in enumerate(valid_products[:5], 1):
            product_name = product.get('product_name', 'Неизвестно')
            calories = product['nutriments']['energy-kcal_100g']
            message += f"{idx}. {product_name} - {calories} ккал/100г\n"

        return {"message": message, "temp": valid_products[:5], "status": 200}  # Возвращаем список продуктов
    except requests.exceptions.HTTPError as http_err:
        return {"error": str(http_err), "status": response.status_code}
    except Exception as err:
        return {"error": f"Ошибка: {err}", "status": 500}