import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Токен бота
TOKEN = "7558730596:AAEzrvH5wqBmgSLWd2zYtjnfN2OvXufFxRQ"  # Укажи свой токен
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# ID вашей группы
GROUP_CHAT_ID = -1002416234517  # Замени на реальный ID группы

# Обработчик всех сообщений
@dp.message()
async def log_group_messages(message: types.Message):
    if message.chat.id == GROUP_CHAT_ID:
        # Логируем ID сообщения
        logger.info(f"Получено сообщение с ID: {message.message_id}, Текст: {message.text}")

# Стартовая команда
@dp.message(Command("start"))
async def start_command_handler(message: types.Message):
    await message.answer("Привет! Бот будет логировать ID сообщений, отправленных в группу.")

# Основной запуск бота
async def main():
    logger.info("Бот запущен")
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
