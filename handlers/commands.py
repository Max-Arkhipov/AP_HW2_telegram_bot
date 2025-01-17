# Обработчики команд (start, help и др.)

from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

router = Router()

@router.message(Command("start"))
async def start_command(message: Message):
    await message.answer("Привет! Я помогу вам рассчитать дневные нормы воды и калорий. Введите /help для списка команд.")

@router.message(Command("help"))
async def help_command(message: Message):
    await message.answer(
        "Доступные команды:\n"
        "/set_profile - Настройка профиля\n"
        "/log_water - Логировать воду\n"
        "/log_food - Логировать еду\n"
        "/log_workout - Логировать тренировку\n"
        "/progress - Проверить прогресс"
    )