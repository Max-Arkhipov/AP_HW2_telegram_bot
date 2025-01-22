# Логирование тренировок
import json
from pathlib import Path
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from utils.calculations import calculate_workout
from utils.helpers import load_data, save_data

# Путь к файлу для хранения данных
STORAGE_FILE = Path("data/storage.json")

# Создаем роутер
router = Router()


# Состояния для FSM
class WorkoutLogStates(StatesGroup):
    type_training = State()
    duration_training = State()


@router.message(Command("log_workout"))
async def start_workout_logging(message: Message, state: FSMContext):
    """
    Обработчик команды /log_workout.
    Начало логирования тренировки.
    """
    await message.answer("Введите тип и длительность тренировки:")
    await state.set_state(WorkoutLogStates.type_training)


@router.message(WorkoutLogStates.type_training)
async def process_product_name(message: Message, state: FSMContext):
    """
    Обработка названия продукта.
    """
    try:
        # Парсим сообщение
        workout_type, duration = message.text.split()
        duration = int(duration)

        if duration <= 0:
            raise ValueError("Длительность должна быть больше 0.")

        # Рассчитываем калории и воду
        calories, additional_water = calculate_workout(workout_type, duration)

        # Загружаем данные пользователя
        user_id = str(message.from_user.id)
        all_users = load_data(STORAGE_FILE)
        user_data = all_users.get(user_id, {})

        # Обновляем общее количество сожженых калорий
        burned_calories = user_data.get("burned_calories", 0) + calories
        user_data["burned_calories"] = burned_calories

        # Обновляем норму воды
        water_norm = user_data.get("water_norm", 0) + additional_water
        user_data["water_norm"] = water_norm

        # Сохраняем данные
        all_users[user_id] = user_data
        save_data(STORAGE_FILE, all_users)

        # Ответ пользователю
        await message.answer(
            f"🏋️‍♂️ Тренировка: {workout_type.capitalize()} ({duration} мин)\n"
            f"Сожжено: {calories:.0f} ккал\n"
            f"Дополнительно выпейте воды: {additional_water:.0f} мл\n\n"
            f"Общее количество сожженых калорий: {burned_calories:.0f} ккал\n"
            f"Обновлённая норма воды: {water_norm:.0f} мл"
        )
        await state.clear()
    except ValueError:
        await message.answer("Укажите корректную длительность тренировки (в минутах).")
    except Exception:
        await message.answer("Введите команду в формате: <тип тренировки> <время (мин)>")