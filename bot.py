# Основной файл бота

import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from handlers import commands, profile, water, food, workout, progress

# Создаем экземпляр бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

# Регистрируем обработчики
dp.include_router(commands.router)
dp.include_router(profile.router)
# dp.include_router(water.router)
# dp.include_router(food.router)
# dp.include_router(workout.router)
dp.include_router(progress.router)

async def main():
    print("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())