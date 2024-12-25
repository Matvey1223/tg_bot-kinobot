import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from handlers import working
from database import main
from aiogram.enums.parse_mode import ParseMode
from config.config import TOKEN


bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
dp.include_router(working.router)


async def start_bot():
    await main()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(start_bot())

