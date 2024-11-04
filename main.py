import asyncio
import config as cfg
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from handlers import rt

logging.basicConfig(level=logging.INFO)

bot = Bot(token=cfg.TOKEN)
stroge = MemoryStorage()
dp = Dispatcher(storage=stroge)

dp.include_router(rt)
async def main():
    await dp.start_polling(bot, skip_updates=True)

if __name__ == '__main__':
    asyncio.run(main())
