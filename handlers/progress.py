import json
from pathlib import Path
from aiogram import Router
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command

from utils.helpers import create_combined_progress_chart

# Путь к файлу для хранения данных
STORAGE_FILE = Path("data/storage.json")

# Создаем роутер
router = Router()

def load_data():
    """Загрузка данных из файла JSON."""
    if STORAGE_FILE.exists():
        with open(STORAGE_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    return {}

@router.message(Command("progress"))
async def show_progress(message: Message):
    """
    Обработчик команды /progress.
    Показывает прогресс пользователя.
    """
    user_id = str(message.from_user.id)

    # Загружаем данные
    all_users = load_data()

    if user_id not in all_users:
        await message.answer("Ваш профиль не найден. Сначала настройте его с помощью команды /set_profile.")
        return

    # Получаем данные пользователя
    user_data = all_users[user_id]
    water_norm = user_data.get("water_norm", 0)
    calories_norm = user_data.get("calories_norm", 0)
    water_logged = user_data.get("water_logged", 0)
    calories_logged = user_data.get("calories_logged", 0)
    burned_calories = user_data.get("burned_calories", 0)

    # Учитываем сожжённые калории
    calories_norm += burned_calories

    # Формируем сообщение о прогрессе
    progress_message = (
        f"Ваш текущий прогресс:\n"
        f"ВОДА:\n"
        f"Выпито воды: {water_logged:.0f} из {water_norm:.0f} мл\n"
        f"Баланс: {water_norm - water_logged:.0f} мл\n"
        f"КАЛОРИИ:\n"
        f"Потреблено калорий: {calories_logged:.0f} из {calories_norm:.0f} ккал\n"
        f"Сожжено калорий: {burned_calories:.0f} ккал\n"
        f"Баланс: {calories_norm - calories_logged:.0f} ккал"
    )

    # Создаём и отправляем диаграмму
    chart_path = Path(f"data/progress_{str(message.from_user.id)}.png")
    create_combined_progress_chart(water_logged, water_norm, calories_logged, calories_norm, chart_path)

    await message.answer(progress_message)
    await message.answer_photo(FSInputFile(chart_path))