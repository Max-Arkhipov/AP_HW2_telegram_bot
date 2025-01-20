from aiogram import Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command

router = Router()

# Создание клавиатуры
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="/set_profile"), KeyboardButton(text="/log_water")],
        [KeyboardButton(text="/log_food"), KeyboardButton(text="/log_workout")],
        [KeyboardButton(text="/progress"), KeyboardButton(text="/help")]
    ],
    resize_keyboard=True  # Клавиатура адаптируется под экран устройства
)

@router.message(Command("start"))
async def start_command(message: Message):
    """
    Обработчик команды /start.
    """
    await message.answer(
        "Привет! Я помогу вам рассчитать дневные нормы воды и калорий. "
        "Введите /help для списка команд.",
        reply_markup=keyboard
    )

@router.message(Command("help"))
async def help_command(message: Message):
    """
    Обработчик команды /help.
    """
    await message.answer(
        "Доступные команды:\n"
        "/set_profile - Настройка профиля\n"
        "/log_water - Логировать воду\n"
        "/log_food - Логировать еду\n"
        "/log_workout - Логировать тренировку\n"
        "/progress - Проверить прогресс",
        reply_markup=keyboard
    )