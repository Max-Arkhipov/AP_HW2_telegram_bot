# Основной файл бота

from aiohttp import web
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
dp.include_router(water.router)
dp.include_router(food.router)
dp.include_router(workout.router)
dp.include_router(progress.router)


async def main():
    print("Бот запущен!")

    # Фейковый веб-сервер для Render
    async def handle(request):
        return web.Response(text="Bot is running!")

    app = web.Application()
    app.router.add_get("/", handle)

    # Запускаем веб-сервер параллельно с polling
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 5000)
    await site.start()

    # Запускаем polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())