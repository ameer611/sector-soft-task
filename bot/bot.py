import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import TELEGRAM_BOT_TOKEN
from bot.handlers import register_handlers

def start_bot():
    bot = Bot(
    token=TELEGRAM_BOT_TOKEN,
    default=DefaultBotProperties(parse_mode="HTML")
)
    dp = Dispatcher(storage=MemoryStorage())
    register_handlers(dp)
    asyncio.run(dp.start_polling(bot))