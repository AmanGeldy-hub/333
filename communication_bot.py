import logging
import asyncio
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# Логирование
logging.basicConfig(level=logging.INFO)

# Настройки бота
TOKEN = "8163172164:AAFzBH3-_oTN4COUJUgwfpS2XaRBr83aMzE"
GROUP_CHAT_ID = -1002270098580  # ID супер-группы
WORK_START = 9
WORK_END = 18

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Переменная для хранения вопросов и их авторов
questions = {}

# Обработчик команды /start
@dp.message(Command("start"))
async def start_command_handler(message: types.Message):
    await message.answer("Привет! Я ваш помощник. Чем могу помочь? Задайте ваш вопрос, и я передам его дальше.")

# Обработчик текстовых сообщений из личного чата
@dp.message(lambda message: message.chat.type == "private")
async def handle_question(message: types.Message):
    user_id = message.from_user.id
    question_text = message.text
    current_hour = datetime.now().hour
    status = "в рабочее время" if WORK_START <= current_hour < WORK_END else "в нерабочее время."

    # Сохранение вопроса и пользователя
    question_id = f"{message.message_id}_{user_id}"
    questions[question_id] = {
        "user_id": user_id,
        "question": question_text,
    }

    # Отправка вопроса в группу
    try:
        sent_message = await bot.send_message(
            chat_id=GROUP_CHAT_ID,
            text=f"Вопрос от {message.from_user.full_name} (ID: {user_id}):\n\n{question_text}\n\nСтатус: {status}"
        )
        # Привязка ID сообщения из группы к вопросу
        questions[question_id]["group_message_id"] = sent_message.message_id
        logging.info(f"Вопрос сохранён: {questions[question_id]}")
        await message.answer("Ваш вопрос отправлен. Спасибо! Мы скоро вам ответим.")
    except Exception as e:
        logging.error(f"Ошибка при пересылке сообщения в группу: {e}")
        await message.answer("Произошла ошибка при отправке вашего вопроса. Попробуйте позже.")

# Обработчик текстовых сообщений из группы
@dp.message(lambda message: message.chat.id == GROUP_CHAT_ID and message.reply_to_message)
async def handle_group_message(message: types.Message):
    replied_message_id = message.reply_to_message.message_id
    logging.info(f"Ответ в группе. reply_to_message_id: {replied_message_id}, текст: {message.text}")

    # Ищем связанный вопрос
    for question_id, details in questions.items():
        if details.get("group_message_id") == replied_message_id:
            user_id = details["user_id"]
            logging.info(f"Найден связанный вопрос: {details}")

            # Отправка ответа пользователю
            try:
                await bot.send_message(chat_id=user_id, text=f"Ответ на ваш вопрос:\n\n{message.text}")
                logging.info(f"Ответ отправлен пользователю {user_id}")
            except Exception as e:
                logging.error(f"Ошибка при отправке ответа пользователю: {e}")

            # Удаление вопроса из памяти
            del questions[question_id]
            logging.info(f"Вопрос {question_id} удалён из памяти.")
            break
    else:
        logging.warning("Ответ из группы не связан с известным вопросом.")

# Запуск бота
async def main():
    print("Общительный бот запущен")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
