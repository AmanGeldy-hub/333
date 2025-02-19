import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# === СОСТОЯНИЯ FSM === #
class Form(StatesGroup):
    waiting_for_code = State()  # Ожидание кодового слова
    choosing_block = State()  # Выбор блока
    choosing_course = State()  # Выбор курса
    viewing_course = State()  # Просмотр курса
    taking_test = State()  # Прохождение теста

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
    "📌 Подбор": {
        "Профиль должности": 32,
        "Размещение вакансий и отработка откликов": 33,
        "Обзвон кандидатов, приглашение на интервью": 34,
        "Собеседование, стажировка": 35
    },
    "📚 Обучение операционным процессам": {  # Изменено название
        "Доверительная приемка": [24, 45, 46, 47],
        "Создание инцидента по «Доверительной приёмке»": [59, 60, 61, 62, 63],
        "Переклейка ценников": [27, 79, 80, 81, 82, 83, 84],
        "Кассовая дисциплина": [28, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73],
        "Порядок проведения инвентаризации": [29, 74, 75, 76, 77, 78],
        "Процесс приготовления выпечки из замороженных ПФ и френч-догов": [30, 48, 49],
        "Инструкция по снятию с охранной системы": 31
    },
    "📝 Учет персонала": {
        "Документы при заключении договора": 38,
        "Как проверять медицинские книжки": 39,
        "Кадровый документооборот": 40
    }
}
# 📋 Тесты
TESTS = {
     "Доверительная приемка": [
        ("Что такое доверительная приемка?\n\nA. Проверка каждого элемента товара при приемке\nB. Приемка товара без предварительной проверки каждого элемента на основе доверия к поставщику\nC. Проверка качества товара на месте поставки", "B"),
        ("В течение какого времени сотрудник Daily может создать инцидент по поставке в случае обнаружения несоответствия?\n\nA. 12 часов\nB. 24 часа\nC. 48 часов", "B"),
        ("Какой из перечисленных случаев не является основанием для создания инцидента по поставке?\n\nA. Соответствие доставленного товара на 80%\nB. Брак, недопоставка\nC. Соответствие доставленного товара заказу", "C"),
        ("Как называется вкладка, в которой сотрудник видит новые задания?\n\nA. «В работе»\nB. «Новые»\nC. «Все задания»", "B"),
        ("Какое действие выполняет сотрудник после того, как выбрал задание на приёмку?\n\nA. Завершает задание\nB. Нажимает на задание и проваливается в него\nC. Переходит в раздел «Завершенные»", "B")
    ],
    "Создание инцидента по «Доверительной приёмке»": [
        ("Для чего необходимо создавать инцидент при обнаружении несоответствия с товаром?\n\nA. Чтобы отменить поставку и сделать возврат\nB. Для отслеживания графика поставок\nC. Чтобы зафиксировать проблему и принять меры для ее решения", "C"),
        ("Что позволяет своевременная регистрация инцидента?\n\nA. Ускорить доставку следующего заказа\nB. Минимизировать потери и быстро реагировать на ошибки\nC. Избежать приемки товара", "B"),
        ("Какая из ситуаций относится к причине «Недопоставка»?\n\nA. Доставлено больше товара, чем указано в заказе\nB. Фактическое количество товара меньше указанного в заказе\nC. Товар имеет физические повреждения", "B"),
        ("Какая причина инцидента соответствует следующему описанию: «Ошибка при поставке, при которой вместо заказанных товаров привезены другие продукты»?\n\nA. Недопоставка\nB. Пересорт\nC. Излишки", "B"),
        ("Что должен сделать сотрудник для выбора причины создания инцидента?\n\nA. Нажать на значок «Редактировать»\nB. Проставить галочку справа от причины и нажать «Выбрать»\nC. Ввести причину вручную", "B")
    ],
    "Порядок проведения инвентаризации": [
        ("Что такое инвентаризация?\n\nA. Процесс доставки товаров в магазин\nB. Процесс проверки и учета наличия, состояния и соответствия товарно-материальных ценностей\nC. Процесс реализации товаров покупателям", "B"),
        ("Какова основная цель инвентаризации?\n\nA. Увеличение товарных запасов\nB. Проверка состояния оборудования\nC. Сверка фактических данных с данными учета и контроль состояния запасов", "C"),
        ("Сколько раз в год проводится комплексная инвентаризация?\n\nA. Два раза в год\nB. Один раз в год\nC. Четыре раза в год", "C"),
        ("Какая инвентаризация охватывает все товарные позиции без исключений?\n\nA. Частичная\nB. Комплексная\nC. Внеплановая", "B"),
        ("Чем отличается плановая инвентаризация?\n\nA. Проводится только при обнаружении недостачи\nB. Проводится в заранее намеченные сроки по утвержденному плану-графику\nC. Проводится ежемесячно без предупреждения", "B")
    ],
    "Переклейка ценников": [
    ("Какой вариант следует выбрать, чтобы распечатать ценники на каждый товар отдельно?\n\nA) «Распечатать все ценники»\nB) «Распечатать ценники»\nC) «Распечатать выбранные ценники»", "B"),
    ("Что должен сделать сотрудник, если он повредил ранее распечатанный ценник?\n\nA) Переходить в раздел «Готовые»\nB) Создать новую задачу на печать\nC) Сообщить руководителю", "A"),
    ("Что сотрудник делает после выбора готовой задачи?\n\nA) Закрывает задачу без печати\nB) Распечатывает необходимый ему ценник\nC) Создаёт новую задачу для печати всех ценников", "C")
]
}

# 🏠 Главное меню
def main_menu():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📌 Подбор")],
            [KeyboardButton(text="📚 Обучение операционным процессам")],  # Изменено название
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

# 📝 Начало тестирования
@dp.message(Form.viewing_course, F.text == "📝 Тестирование")
async def start_test(message: types.Message, state: FSMContext):
    data = await state.get_data()
    selected_course = data.get("selected_course")  # Получаем выбранный курс
    
    if selected_course in TESTS:
        await state.update_data(course_name=selected_course, correct_answers=0, current_question=0)
        await state.set_state(Form.taking_test)
        await send_test_question(message, state)
    else:
        await message.answer("❌ Для этого курса нет теста.")

# 📌 Отправка первого вопроса
async def send_test_question(message: types.Message, state: FSMContext):
    data = await state.get_data()
    course_name = data.get("course_name")
    
    if course_name not in TESTS:
        await message.answer("❌ Ошибка: тест для этого курса не найден.")
        return
    
    questions = TESTS[course_name]
    current_question = data.get("current_question", 0)

    # Распаковываем данные из кортежа (вопрос и правильный ответ)
    question_text, correct_answer = questions[current_question]
    
    # Получаем варианты ответов (ищем строки, которые начинаются с "A.", "B.", "C.")
    options = [line for line in question_text.split("\n") if line.startswith(("A.", "B.", "C."))]

    # Создаём клавиатуру
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=option)] for option in options],
        resize_keyboard=True
    )

    # Отправляем вопрос
    await message.answer(question_text, reply_markup=keyboard)

    # Сохраняем текущий вопрос и ответ
    await state.update_data(current_question=current_question, correct_answer=correct_answer)
	

# 🎯 Обработка ответа
@dp.message(Form.taking_test)
async def handle_test_answer(message: types.Message, state: FSMContext):
    await process_answer(message, state)

# ✅ Логика обработки ответа
async def process_answer(message: types.Message, state: FSMContext):
    data = await state.get_data()
    course_name = data.get("course_name")
    
    if not course_name or course_name not in TESTS:
        await message.answer("❌ Ошибка: тест для этого курса не найден.")
        return

    questions = TESTS[course_name]
    correct_answers = data.get("correct_answers", 0)
    current_question = data.get("current_question", 0)

    selected_answer = message.text.strip()
    selected_letter = selected_answer.split(".")[0]  # Получаем только букву A, B или C

    question_text, correct_answer = questions[current_question]

    print(f"Выбранный ответ: {selected_answer} -> {selected_letter}, Правильный: {correct_answer}")

    if selected_letter == correct_answer:
        correct_answers += 1
        print("✅ Ответ верный!")

    current_question += 1
    await state.update_data(correct_answers=correct_answers, current_question=current_question)

    if current_question < len(questions):
        await send_test_question(message, state)  # Отправляем следующий вопрос
    else:
 # ✅ Тест завершен
        result_text = f"🎉 Тест завершён! \nВы набрали {correct_answers} из {len(questions)} баллов."
        keyboard = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Вернуться к курсам")]],
            resize_keyboard=True
        )
        await message.answer(result_text, reply_markup=keyboard)

# ⬇️ Сбрасываем блок и переводим в выбор блока
        await state.update_data(selected_block=None)
        await state.set_state(Form.choosing_block)


# ✅ Обработчик кнопки "Вернуться к курсам"
@dp.message(F.text.lower() == "вернуться к курсам")  
async def return_to_courses(message: types.Message, state: FSMContext):
    print("🔄 Обработчик 'Вернуться к курсам' сработал!")  # Логируем вызов обработчика
    
    # Переводим в выбор блока
    await state.update_data(selected_block=None)  
    await state.set_state(Form.choosing_block)  

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📚 Подбор"), KeyboardButton(text="🎓 Обучение")],
            [KeyboardButton(text="📋 Учет персонала")]
        ],
        resize_keyboard=True
    )
    await message.answer("🔙 Выберите обучающий блок:", reply_markup=keyboard)


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

#🔙 Назад
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
    await message.answer("Извините, я не понимаю эту команду. Пожалуйста, используйте кнопки меню либо перезагрузите используя команду /start.")

@dp.message()
async def catch_all_messages(message: types.Message):
    print(f"📩 Получен текст: '{message.text}'") 

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

# 📋 Тесты
dp.message.register(start_test, F.text == "📝 Начало тестирования")  # Начало теста
dp.message.register(handle_test_answer, Form.taking_test)  # Обработка ответа

dp.message.register(unknown_message)  # Обработка неизвестных сообщений

if __name__ == "__main__":
    asyncio.run(main())  # Запуск бота


