# bot/main.py
import asyncio
import os
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from handlers import router
from core.db_manager import init_db

BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN')

async def main():
    init_db() # Инициализируем БД тарифов и подписок при старте
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    
    print("🤖 Telegram-бот запущен и подключен к ядру WPP.")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
