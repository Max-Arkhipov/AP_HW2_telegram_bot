import json
from pathlib import Path
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

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


def save_data(data):
    """Сохранение данных в файл JSON."""
    STORAGE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STORAGE_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


# Определение состояний FSM
class WaterLogStates(StatesGroup):
    waiting_for_water_amount = State()


@router.message(Command("log_water"))
async def log_water_command(message: Message, state: FSMContext):
    """
    Обработчик команды /log_water.
    Запрашивает количество выпитой воды.
    """
    await message.answer("Введите количество выпитой воды в миллилитрах:")
    await state.set_state(WaterLogStates.waiting_for_water_amount)


@router.message(WaterLogStates.waiting_for_water_amount)
async def add_water(message: Message, state: FSMContext):
    """
    Обработка введённого количества воды.
    """
    user_id = str(message.from_user.id)
    all_users = load_data()

    # Если пользователь не существует, создаём запись
    if user_id not in all_users:
        all_users[user_id] = {"water_logged": 0}

    try:
        water_amount = int(message.text)
        if water_amount <= 0:
            await message.answer("Введите положительное число миллилитров.")
            return

        # Обновляем лог воды
        all_users[user_id]["water_logged"] = all_users[user_id].get("water_logged", 0) + water_amount
        save_data(all_users)

        total_water = all_users[user_id]["water_logged"]
        await message.answer(f"Вы добавили {water_amount} мл воды. Всего сегодня: {total_water} мл.")
        await state.clear()  # Сбрасываем состояние
    except ValueError:
        await message.answer("Введите число в миллилитрах.")