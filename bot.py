import json
from pathlib import Path
from aiohttp import web
import asyncio
import logging
from aiogram import Bot, Dispatcher
import aiocron  # Асинхронная библиотека для задач

from config import BOT_TOKEN
from handlers import commands, profile, water, food, workout, progress
from utils.helpers import load_data, save_data, update_daily_goals

# Создаем экземпляр бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)

# Регистрируем обработчики
dp.include_router(commands.router)
dp.include_router(profile.router)
dp.include_router(water.router)
dp.include_router(food.router)
dp.include_router(workout.router)
dp.include_router(progress.router)

# Путь к файлу для хранения данных
STORAGE_FILE = Path("data/storage.json")


async def daily_update():
    """Запускает обновление норм для всех пользователей."""
    all_users = load_data(STORAGE_FILE)
    for user_id in all_users.keys():
        user_data = all_users.get(user_id, {})
        user_data = update_daily_goals(user_data)
        all_users[user_id] = user_data
        save_data(STORAGE_FILE, all_users)
    logging.info("Ежедневное обновление норм выполнено")


# Планируем задачу с помощью aiocron
async def scheduled_task():
    await daily_update()

# Регистрируем задачу в текущем цикле событий
async def register_cron_jobs():
    """Регистрация всех задач cron в текущем asyncio-цикле."""
    cron = aiocron.crontab("00 00 * * *", func=scheduled_task, start=False)
    cron.start()
    logging.info("Задача cron успешно зарегистрирована.")

async def main():
    print("Бот запущен!")

    # Регистрируем cron-задачи
    await register_cron_jobs()

    # Запускаем polling
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())