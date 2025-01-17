import json
from pathlib import Path
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

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
    weight = user_data.get("weight", "не указан")
    height = user_data.get("height", "не указан")
    age = user_data.get("age", "не указан")
    activity = user_data.get("activity", "не указан")
    city = user_data.get("city", "не указан")
    water_norm = user_data.get("water_norm", "не рассчитана")
    calories_norm = user_data.get("calories_norm", "не рассчитана")

    # Формируем ответ
    progress_message = (
        f"Ваш текущий прогресс:\n"
        f"Вес: {weight} кг\n"
        f"Рост: {height} см\n"
        f"Возраст: {age} лет\n"
        f"Уровень активности: {activity} мин\n"
        f"Город: {city}\n"
        f"Дневная норма воды: {water_norm:.0f} мл\n"
        f"Дневная норма калорий: {calories_norm:.0f} Ккал"
    )

    await message.answer(progress_message)


