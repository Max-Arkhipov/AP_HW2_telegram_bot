import json
from pathlib import Path
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from utils.api import get_food
from utils.helpers import load_data, save_data

# Путь к файлу для хранения данных
STORAGE_FILE = Path("data/storage.json")

# Создаем роутер
router = Router()


# Состояния для FSM
class FoodLogStates(StatesGroup):
    waiting_for_product = State()
    waiting_for_choice = State()
    waiting_for_quantity = State()


@router.message(Command("log_food"))
async def start_food_logging(message: Message, state: FSMContext):
    """
    Обработчик команды /log_food.
    Начало логирования еды.
    """
    await message.answer("Введите название продукта:")
    await state.set_state(FoodLogStates.waiting_for_product)


@router.message(FoodLogStates.waiting_for_product)
async def process_product_name(message: Message, state: FSMContext):
    """
    Обработка названия продукта.
    """
    product_name = message.text.strip()
    food_data = get_food(product_name)

    if food_data["status"] != 200:
        await message.answer(food_data.get("error", "Ошибка при поиске продукта."))
        await state.clear()
        return

    # Сохраняем найденные продукты в состоянии
    await state.update_data(food_options=food_data["temp"])

    # Формируем список выбора
    keyboard = InlineKeyboardBuilder()
    for idx, product in enumerate(food_data["temp"], 1):
        keyboard.button(text=f"{idx}. {product['product_name']}", callback_data=str(idx))
    keyboard.adjust(1)

    await message.answer(
        f"Найденные продукты:\n{food_data['message']}\nВыберите номер продукта:",
        reply_markup=keyboard.as_markup()
    )
    await state.set_state(FoodLogStates.waiting_for_choice)


@router.callback_query(FoodLogStates.waiting_for_choice)
async def process_product_choice(callback: CallbackQuery, state: FSMContext):
    """
    Обработка выбора продукта.
    """
    choice = callback.data
    data = await state.get_data()
    food_options = data.get("food_options", [])

    if not choice.isdigit() or int(choice) < 1 or int(choice) > len(food_options):
        await callback.message.answer("Неверный выбор. Попробуйте снова.")
        return

    # Сохраняем выбранный продукт
    selected_product = food_options[int(choice) - 1]
    await state.update_data(selected_product=selected_product)

    await callback.message.answer(
        f"Вы выбрали: {selected_product['product_name']}. Введите количество в граммах:"
    )
    await state.set_state(FoodLogStates.waiting_for_quantity)


@router.message(FoodLogStates.waiting_for_quantity)
async def process_quantity(message: Message, state: FSMContext):
    """
    Обработка количества продукта.
    """
    try:
        quantity = float(message.text.strip())
        if quantity <= 0:
            raise ValueError("Количество должно быть положительным числом.")

        data = await state.get_data()
        selected_product = data.get("selected_product", {})
        calories_per_100g = selected_product['nutriments']['energy-kcal_100g']
        total_calories = (calories_per_100g / 100) * quantity

        # Сохраняем результат в общий счётчик калорий
        user_id = str(message.from_user.id)
        all_users = load_data(STORAGE_FILE)
        user_data = all_users.get(user_id, {})
        total_logged_calories = user_data.get("calories_logged", 0)
        user_data["calories_logged"] = total_logged_calories + total_calories
        all_users[user_id] = user_data
        save_data(STORAGE_FILE, all_users)

        await message.answer(
            f"Продукт: {selected_product['product_name']}\n"
            f"Количество: {quantity} г\n"
            f"Калорийность: {total_calories:.2f} ккал\n\n"
            f"Общее количество калорий за день: {user_data['calories_logged']:.0f} / {user_data['calories_norm']:.0f} ккал."
        )
        await state.clear()
    except ValueError:
        await message.answer("Введите корректное количество (число больше нуля).")