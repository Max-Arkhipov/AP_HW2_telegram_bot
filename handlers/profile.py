import json
from pathlib import Path
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from utils.api import get_temp
from utils.calculations import calculate_water_norm, calculate_calories_norm

# Путь к файлу для хранения данных
STORAGE_FILE = Path("data/storage.json")

# Создаем роутер
router = Router()

# Определяем состояния
class ProfileState(StatesGroup):
    weight = State()
    height = State()
    age = State()
    gender = State()
    activity = State()
    city = State()

def load_data():
    """Загрузка данных из файла JSON."""
    if STORAGE_FILE.exists():
        with open(STORAGE_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    return {}

def save_data(data):
    """Сохранение данных в файл JSON."""
    STORAGE_FILE.parent.mkdir(parents=True, exist_ok=True)  # Создаем папку, если её нет
    with open(STORAGE_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

@router.message(Command("set_profile"))
async def set_profile(message: Message, state: FSMContext):
    """
    Обработчик команды /set_profile. Запускает процесс настройки профиля.
    """
    await message.answer("Введите ваш вес (в кг):")
    await state.set_state(ProfileState.weight)

@router.message(ProfileState.weight)
async def process_weight(message: Message, state: FSMContext):
    try:
        weight = float(message.text)
        if weight <= 0:
            raise ValueError
        await state.update_data(weight=weight)
        await message.answer("Введите ваш рост (в см):")
        await state.set_state(ProfileState.height)
    except ValueError:
        await message.answer("Пожалуйста, введите корректное значение веса (число больше 0).")

@router.message(ProfileState.height)
async def process_height(message: Message, state: FSMContext):
    try:
        height = float(message.text)
        if height <= 0:
            raise ValueError
        await state.update_data(height=height)
        await message.answer("Введите ваш возраст:")
        await state.set_state(ProfileState.age)
    except ValueError:
        await message.answer("Пожалуйста, введите корректное значение роста (число больше 0).")

@router.message(ProfileState.age)
async def process_age(message: Message, state: FSMContext):
    """
    Обработка возраста пользователя.
    """
    try:
        age = int(message.text)
        if age <= 0:
            raise ValueError
        await state.update_data(age=age)

        # Создаем клавиатуру для выбора пола
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Мужской"), KeyboardButton(text="Женский")],
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )

        await message.answer("Укажите ваш пол:", reply_markup=keyboard)
        await state.set_state(ProfileState.gender)
    except ValueError:
        await message.answer("Пожалуйста, введите корректное значение возраста (целое число больше 0).")


@router.message(ProfileState.gender)
async def process_gender(message: Message, state: FSMContext):
    """
    Обработка выбора пола пользователя.
    """
    gender = message.text.strip().lower()
    if gender not in ("мужской", "женский"):
        # Если ввод неверный, повторяем запрос
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Мужской"), KeyboardButton(text="Женский")],
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        await message.answer("Пожалуйста, выберите ваш пол:", reply_markup=keyboard)
        return

    # Сохраняем пол в формате male/female
    await state.update_data(gender="male" if gender == "мужской" else "female")

    # Переходим к следующему шагу
    await message.answer("Сколько минут активности у вас в день?", reply_markup=None)
    await state.set_state(ProfileState.activity)

@router.message(ProfileState.activity)
async def process_activity(message: Message, state: FSMContext):
    try:
        activity = int(message.text)
        if activity < 0 or activity > 480:
            raise ValueError
        await state.update_data(activity=activity)
        await message.answer("В каком городе вы находитесь?")
        await state.set_state(ProfileState.city)
    except ValueError:
        await message.answer("Пожалуйста, введите корректное значение активности (целое число 0 или больше).")

@router.message(ProfileState.city)
async def process_city(message: Message, state: FSMContext):
    city = message.text.strip()
    weather_response = get_temp(city)

    # Проверяем статус ответа
    if weather_response["status"] != 200:
        await message.answer(
            f"Не удалось найти информацию о городе '{city}'. "
            f"Пожалуйста, проверьте название и попробуйте снова."
        )
        return

    # Если город корректен, сохраняем его
    temperature = weather_response["temp"]
    await state.update_data(city=city)

    # Получаем данные из FSM
    data = await state.get_data()

    # Загружаем существующие данные из файла
    all_users = load_data()

    # Рассчитываем дневную норму воды
    water_norm = calculate_water_norm(
        weight=data["weight"],
        activity_minutes=data["activity"],
        temperature=temperature
    )
    await state.update_data(water_norm=water_norm)

    # Рассчитываем дневную норму калорий
    calories_norm = calculate_calories_norm(
        weight=data["weight"],
        height=data["height"],
        age=data["age"],
        gender=data["gender"],
        activity=data["activity"],
    )

    await state.update_data(calories_norm=calories_norm)

    # Записываем данные пользователя, включая норму воды
    updated_fields = {
        "weight": data["weight"],
        "height": data["height"],
        "age": data["age"],
        "gender": data["gender"],
        "activity": data["activity"],
        "city": data["city"],
        "water_norm": water_norm,
        "calories_norm": calories_norm
    }

    # Обновляем только указанные поля для пользователя
    if str(message.from_user.id) not in all_users:
        all_users[str(message.from_user.id)] = {}

    all_users[str(message.from_user.id)].update(updated_fields)

    # Сохраняем данные в файл
    save_data(all_users)

    # Завершаем FSM
    await state.clear()

    # Выводим данные профиля и дневную норму воды
    await message.answer(
        f"Ваш профиль настроен:\n"
        f"Вес: {data['weight']} кг\n"
        f"Рост: {data['height']} см\n"
        f"Возраст: {data['age']} лет\n"
        f"Активность: {data['activity']} минут в день\n"
        f"Город: {data['city']}\n"
        f"Дневная норма воды: {water_norm:.0f} мл\n"
        f"Дневная норма калорий: {calories_norm:.0f} Ккал"
    )