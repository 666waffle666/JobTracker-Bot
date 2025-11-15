import logging
import asyncio
from aiogram import Bot, Dispatcher
from .scheduler import start_scheduler
from app.config import Config
from .handlers import start_router, setup_router, list_router, notifications_router

bot = Bot(token=Config.BOT_TOKEN)  # Bot instance
dp = Dispatcher()  # event manager

# event handlers
dp.include_routers(start_router, setup_router, list_router, notifications_router)


async def main():
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    logging.info("Запуск бота... ✅")

    try:
        logging.info("Бот готов к работе, стартуем scheduler, polling.")
        start_scheduler(bot)
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"Ошибка во время работы бота: {e}")
    finally:
        logging.info("Бот был остановлен ⛔")


if __name__ == "__main__":
    asyncio.run(main())
