import logging
import aioschedule
import asyncio
from aiogram import executor, types
from config import bot, dp
from db.database import db_path
from db.function_db import SubscriptionManager
import handlers
# Настройка логирования
logging.basicConfig(level=logging.INFO)

async def schedule_jobs():
    subscription_manager = SubscriptionManager(db_path)
    aioschedule.every().day.at("01:26").do(subscription_manager.update_expired_subscriptions_and_delete_keys)

    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)

async def on_startup(_):
    asyncio.create_task(schedule_jobs())


# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)