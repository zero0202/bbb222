import asyncio

from aiogram import executor

from config import admin_id
from database import create_db
import load_all


async def on_shutdown(dp):
    await load_all.bot.close()


async def on_startup(dp):
    # Подождем пока запустится база данных...
    await asyncio.sleep(5)
    await create_db()
    await load_all.bot.send_message(admin_id, "Я запущен!")


if __name__ == '__main__':
    from admin_panel import dp
    from handlers import dp

    executor.start_polling(dp, on_shutdown=on_shutdown, on_startup=on_startup)