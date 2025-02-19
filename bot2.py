import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

# === СОСТОЯНИЯ FSM === #
class Form(StatesGroup):
    waiting_for_code = State()  # Ожидание кодового слова
    choosing_block = State()  # Выбор блока
    choosing_course = State()  # Выбор курса
    viewing_course = State()  # Просмотр курса
# 🔐 Токен бота
API_TOKEN = "7558730596:AAGE6wMl2w0MJys_uf5qrEgy8UDCjtO62dc"

# 📌 ID группы, откуда пересылать сообщения
GROUP_ID = -1002416234517

# 🔧 Логирование
logging.basicConfig(level=logging.INFO)

# 🤖 Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# 🔑 Кодовое слово
SECRET_CODE = "123"

# 📚 Структура блоков и курсов
blocks = {
    "Подбор": {
        "Профиль должности": 32,
        "Размещение вакансий и отработка откликов": 33,
        "Обзвон кандидатов, приглашение на интервью": 34,
        "Собеседование, стажировка": 35
    },
    "Обучение": {
        "Доверительная приемка": [24, 45, 46, 47],
        "Создание инцидента по «Доверительной приёмке»": 25,
        "Переклейка ценников": 27,
        "Кассовая дисциплина": 28,
        "Порядок проведения инвентаризации": 29,
        "Процесс приготовления выпечки из замороженных ПФ и фрэнч-догов": [30, 48, 49],
        "Инструкция по снятию с охранной системы": 31
    },
    "Учет персонала": {
        "Документы при заключении договора": 38,
        "Как проверять медицинские книжки": 39,
        "Кадровый документооборот": 40
    }
}

# 🏠 Главное меню

def main_menu():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📌 Подбор")],
            [KeyboardButton(text="📚 Обучение")],
            [KeyboardButton(text="📝 Учет персонала")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard

# 🎓 Меню курсов
def course_menu(selected_block):
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=course)] for course in blocks[selected_block]] + 
                 [[KeyboardButton(text="🔙 Назад")], [KeyboardButton(text="🏠 Вернуться к блокам")]],
        resize_keyboard=True,
    )
@dp.message(F.text == "🏠 Вернуться к блокам")
async def go_to_blocks(message: types.Message, state: FSMContext):
    await state.set_state(Form.choosing_block)
    await message.answer("Выберите блок:", reply_markup=main_menu())

# 📖 Опции курса
def course_options():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📚 Курс"), KeyboardButton(text="📝 Тестирование")],
            [KeyboardButton(text="🔙 Назад")]
        ],
        resize_keyboard=True
    )
    return keyboard

# ✅ Команда /start
@dp.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    await state.set_state(Form.waiting_for_code)
    await message.answer("Привет!Введите кодовое слово🔑:")

# 🔑 Проверка кодового слова
@dp.message(Form.waiting_for_code)
async def check_code(message: types.Message, state: FSMContext):
    if message.text.strip() == SECRET_CODE:
        await state.set_state(Form.choosing_block)
        await message.answer("✅ Доступ разрешён! Выберите блок:", reply_markup=main_menu())
    else:
        await message.answer("❌ Неверное кодовое слово. Попробуйте ещё раз.")

# 📌 Выбор блока
@dp.message(Form.choosing_block)
async def choose_block(message: types.Message, state: FSMContext):
    text = message.text.strip()  # Убираем лишние пробелы
    selected_block = None  # Переменная для хранения выбранного блока

    # 🔍 Ищем, соответствует ли текст одному из блоков
    for key in blocks.keys():
        if key in text:  
            selected_block = key  
            break

    # 🔧 Логирование для отладки
    print(f"🔹 Полученный текст: {repr(text)}")  
    print(f"🔹 Доступные блоки: {list(blocks.keys())}")  
    print(f"📌 Выбранный блок: {selected_block}")  

    if selected_block:  # Если блок найден
        await state.update_data(selected_block=selected_block)  
        await state.set_state(Form.choosing_course)  
        await message.answer(f"📚 Вы выбрали '{selected_block}'. Теперь выберите курс:", reply_markup=course_menu(selected_block))
    else:
        print("❌ Ошибка! Пользователь ввёл неверное название блока.")  
        await message.answer("❌ Выберите один из предложенных блоков.")
# 📚 Выбор курса
@dp.message(Form.choosing_course)
async def choose_course(message: types.Message, state: FSMContext):
    data = await state.get_data()
    selected_block = data.get("selected_block")
    print(f"🔹 Выбранный блок: {selected_block}")
    print(f"🔹 Полученный курс: {message.text}")
    print(f"🔹 Доступные курсы: {list(blocks[selected_block].keys()) if selected_block else 'None'}")	
    if selected_block and message.text in blocks[selected_block]:
        await state.update_data(selected_course=message.text)
        await state.set_state(Form.viewing_course)  # ✅ Новый state
        await message.answer(f"📖 Курс '{message.text}'. Выберите действие:", reply_markup=course_options())
    else:
        await message.answer("❌ Выберите один из предложенных курсов.")

# 📖 Описание курса (пересылка сообщения)
@dp.message(Form.viewing_course, F.text == "📚 Курс")
async def send_description(message: types.Message, state: FSMContext):
    data = await state.get_data()
    selected_block = data.get("selected_block")
    selected_course = data.get("selected_course")

    if selected_block and selected_course:
        course_ids = blocks[selected_block][selected_course]

        if isinstance(course_ids, list):  # Если несколько ID — отправить все
            for course_id in course_ids:
                await bot.forward_message(chat_id=message.chat.id, from_chat_id=GROUP_ID, message_id=course_id)
        else:  # Если один ID — просто переслать
            await bot.forward_message(chat_id=message.chat.id, from_chat_id=GROUP_ID, message_id=course_ids)
    else:
        await message.answer("❌ Сначала выберите курс.")


@dp.message(F.text == "🔙 Назад")
async def go_back(message: types.Message, state: FSMContext):
    print(f"🔙 Получено сообщение: '{message.text}'")  

    # Получаем текущее состояние
    data = await state.get_data()
    current_state = await state.get_state()  
    print(f"🔙 Назад нажата! Текущее состояние: {current_state}, данные: {data}")  

    # Убедимся, что состояние не None
    current_state = current_state or ""

    if current_state == Form.viewing_course.state:
        print("📚 Переход обратно к выбору курса")  
        
        await state.set_state(Form.choosing_course)  # Обновляем состояние
        new_state = await state.get_state()  # Проверяем обновилось ли
        print(f"✅ Новое состояние после Назад: {new_state}")  

        selected_block = data.get("selected_block")
        if selected_block:
            print(f"📚 Возвращаемся в блок '{selected_block}'")
            await message.answer("Выберите курс:", reply_markup=course_menu(selected_block))
        else:
            print("❌ Ошибка! Не найден выбранный блок, возвращаемся в главное меню.")
            await state.set_state(Form.choosing_block)
            await message.answer("Выберите блок:", reply_markup=main_menu())

    elif current_state == Form.choosing_course.state:
        print("📌 Переход обратно к выбору блока")  
        await state.set_state(Form.choosing_block)
        new_state = await state.get_state()
        print(f"✅ Новое состояние после Назад: {new_state}")
        await message.answer("Выберите блок:", reply_markup=main_menu())

    elif current_state == Form.choosing_block.state or current_state == "":
        print("🏠 Возвращение в главное меню")  
        await state.set_state(Form.main_menu)
        new_state = await state.get_state()
        print(f"✅ Новое состояние после Назад: {new_state}")
        await message.answer("Главное меню:", reply_markup=main_menu())

    else:
        print(f"❌ Неизвестное состояние '{current_state}', сбрасываем в выбор блока.")  
        await state.set_state(Form.choosing_block)
        new_state = await state.get_state()
        print(f"✅ Новое состояние после Назад: {new_state}")
        await message.answer("Выберите блок:", reply_markup=main_menu())


# 🤷‍♂️ Обработка неизвестных сообщений
@dp.message()
async def unknown_message(message: types.Message):
    await message.answer("Извините, я не понимаю эту команду. Пожалуйста, используйте кнопки меню.")

# 🚀 Запуск бота
async def main():
    # Удаляем старые сообщения перед запуском
    await bot.delete_webhook(drop_pending_updates=True)  
    # Запускаем бота
    await dp.start_polling(bot)  

# Регистрируем обработчики
dp.message.register(start, Command("start"))  # Обработчик /start
dp.message.register(check_code, Form.waiting_for_code)  # Проверка кодового слова
dp.message.register(choose_block, Form.choosing_block, F.text.in_(blocks.keys()))  # Выбор блока
dp.message.register(go_back, F.text == "🔙 Назад")  # Кнопка "Назад"
dp.message.register(go_to_blocks, F.text == "🏠 Вернуться к блокам")  # Возвращение к блокам
dp.message.register(choose_course, Form.choosing_block, F.text.func(lambda text: any(text in courses for courses in blocks.values())))  # Выбор курса
dp.message.register(send_description, F.text == "📖 Курс")  # Описание курса
dp.message.register(unknown_message)  # Обработка неизвестных сообщений

if __name__ == "__main__":
    asyncio.run(main())  # Запуск бота



