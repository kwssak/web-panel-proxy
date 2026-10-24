# bot/main.py
import asyncio
import os
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiohttp import web
from handlers import router
from webhook_server import setup_webhook_app
from core.db_manager import init_db

BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN')
WEBHOOK_PORT = int(os.getenv('WEBHOOK_PORT', 8081))

async def main():
    init_db()
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    
    # Запуск веб-сервера для вебхуков
    webhook_app = setup_webhook_app()
    runner = web.AppRunner(webhook_app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', WEBHOOK_PORT)
    await site.start()
    print(f"🌐 Webhook сервер запущен на порту {WEBHOOK_PORT}")
    
    # Запуск бота
    print("🤖 Бот запущен!")
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен.")
