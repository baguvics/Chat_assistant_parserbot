import logging
import sqlite3
import os
import asyncio
import dbinit, db_functions
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import Message



from datetime import datetime
from kbs import inline_kb_full

from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

load_dotenv()
API_TOKEN = os.environ.get('TELEGRAM_TOKEN')
DB_PATH = os.environ.get('DB_PATH')
ADMIN = os.environ.get('ADMINS')


logging.basicConfig(level=logging.INFO)

storage = MemoryStorage()
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)

class States(StatesGroup):
    main_menu = State()
    events = State()
    suggestions = State()
    news = State()
    faq = State()
    list_of_events = State()
    sign_up_for_event = State()
    contact = State()
    handle_event_button = State()
    handle_event_signup = State()
    delete_event = State()
    edit_event = State()
    add_event = State()
    edit_name = State()
    edit_description = State()
    edit_date = State()
    waiting_for_phone = State()
    waiting_for_name = State()
    waiting_for_suggestion = State()


@dp.message_handler(commands=['start'])
async def handle_meets(message: types.Message, state: FSMContext):
    # Проверяем, есть ли пользователь в БД
    query = 'SELECT * FROM Person WHERE telegramId = ?'
    existing_person = db_functions.execute_query(query, (message.from_user.id,), fetch_all=True)

    if not existing_person:
        # Если пользователя нет в БД, запускаем процесс регистрации
        await States.waiting_for_name.set()

        # Отправляем запрос на ввод имени
        await message.answer("Добро пожаловать! Для начала, давайте узнаем ваши ФИО.")
    else:
        # Если пользователь уже есть в БД, отправляем соответствующее сообщение
        await States.main_menu.set()
        await message.answer("Привет! Выберите действие:", reply_markup=main_menu())
        await States.contact.set()

    # Хендлер, который ждет ввода имени


@dp.message_handler(state=States.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    # Сохраняем введенное имя в состояние FSM
    await state.update_data(name=message.text)

    # Отправляем запрос на ввод номера телефона
    await message.answer(f"Спасибо, {message.text}! Теперь укажите ваш номер телефона.")

    # Переключаем состояние на ожидание ввода номера телефона
    await States.waiting_for_phone.set()


# Хендлер, который ждет ввода номера телефона
@dp.message_handler(state=States.waiting_for_phone)
async def process_phone(message: types.Message, state: FSMContext):
    # Сохраняем введенный номер телефона в состояние FSM
    await state.update_data(phone=message.text)

    # Извлекаем данные из состояния
    user_data = await state.get_data()

    # Ваши данные для записи в БД
    user_id = message.from_user.id
    name = user_data.get('name')
    phone = user_data.get('phone')

    # Добавляем пользователя в БД
    db_functions.add_person_to_db(user_id, name, phone)

    # Завершаем процесс регистрации
    await state.finish()

    # Отправляем сообщение с благодарностью
    await States.main_menu.set()
    await message.answer("Спасибо за регистрацию! ", reply_markup=main_menu())
    await States.contact.set()


# @dp.message_handler(commands=['start'])
# async def cmd_start(message: types.Message):
#     # Устанавливаем начальное состояние
#
#     await States.main_menu.set()
#     await message.answer("Привет! Выберите действие:", reply_markup=main_menu())
#     await States.contact.set()

@dp.message_handler(content_types=types.ContentType.CONTACT, state=States.contact)
async def contacts(msg: types.Message, state: FSMContext):
    print(msg)
    await msg.answer(f"Твой номер успешно получен: {msg.contact.phone_number}", reply_markup=types.ReplyKeyboardRemove())
    await state.finish()


@dp.callback_query_handler(lambda c: c.data == 'main_menu', state='*')
async def process_main_menu(callback_query: types.CallbackQuery, state: FSMContext):
    await States.main_menu.set()
    await callback_query.answer()
    await callback_query.message.edit_text("1Главное", reply_markup=main_menu())


@dp.callback_query_handler(lambda c: c.data == 'events', state='*')
async def process_events_menu(callback_query: types.CallbackQuery, state: FSMContext):
    await States.events.set()
    await callback_query.answer()
    await callback_query.message.edit_text("2Мероприятия", reply_markup=events(str(callback_query.from_user.id)))

@dp.callback_query_handler(lambda c: c.data == 'list_of_events', state='*')
async def process_list_of_events_menu(callback_query: types.CallbackQuery, state: FSMContext):
    await States.list_of_events.set()
    await callback_query.answer()
    list_of_events = db_functions.get_all_events()
    await callback_query.message.edit_text(list_of_events, reply_markup=news())

@dp.callback_query_handler(lambda c: c.data == 'sign_up_for_event', state='*')
async def process_sign_up_for_event_menu(callback_query: types.CallbackQuery, state: FSMContext):
    await States.sign_up_for_event.set()
    await callback_query.answer()
    list_of_events = db_functions.get_all_events()
    await callback_query.message.edit_text(list_of_events, reply_markup=sign_up_for_event(list_of_events))


@dp.callback_query_handler(lambda query: query.data.startswith("event_button:"), state='*')
async def handle_event_button(callback_query: types.CallbackQuery, state: FSMContext):
    await States.handle_event_button.set()
    event_id = int(callback_query.data.split(":")[1])
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Записаться", callback_data=f"event_signup:{event_id}"))
    buttons = []
    if str(callback_query.from_user.id) in ADMIN:
        buttons.append(InlineKeyboardButton("Изменить", callback_data=f'edit_event:{event_id}'))
        buttons.append(InlineKeyboardButton("Удалить", callback_data=f'delete_event:{event_id}'))
    buttons.append(InlineKeyboardButton("Назад", callback_data='back'))
    keyboard.add(*buttons)
    await callback_query.message.edit_text(f"Информация о мероприятии:{event_id}", reply_markup=keyboard)


@dp.callback_query_handler(lambda query: query.data.startswith("event_signup:"), state='*')
async def handle_event_signup(callback_query: types.CallbackQuery, state: FSMContext):
    await States.handle_event_signup.set()
    event_id = int(callback_query.data.split(":")[1])
    user_id = callback_query.from_user.id

    db_functions.add_event_person_to_db(event_id, user_id)
    await States.main_menu.set()
    await callback_query.message.edit_text(f"Вы успешно записались на мероприятие!\n\n", reply_markup=main_menu())


@dp.callback_query_handler(lambda query: query.data.startswith("delete_event:"), state='*')
async def handle_delete_event(callback_query: types.CallbackQuery, state: FSMContext):
    await States.delete_event.set()
    event_id = int(callback_query.data.split(":")[1])
    if str(callback_query.from_user.id) in ADMIN:
        db_functions.delete_event_by_id(event_id)
    await callback_query.message.edit_text(f"Вы успешно удалили мероприятие!", reply_markup=main_menu())

@dp.callback_query_handler(lambda query: query.data.startswith("edit_event:"), state='*')
async def handle_edit_event(callback_query: types.CallbackQuery, state: FSMContext):
    await States.edit_event.set()
    event_id = int(callback_query.data.split(":")[1])
    await callback_query.message.edit_text(f"Выберите что вы хотите изменить", reply_markup=edit_event(event_id))

@dp.callback_query_handler(lambda query: query.data.startswith("edit_name:"), state='*')
async def handle_edit_name(callback_query: types.CallbackQuery, state: FSMContext):
    event_id = int(callback_query.data.split(":")[1])
    await States.edit_name.set()
    await state.update_data(event_id=event_id)
    await callback_query.message.edit_text("Введите новое название")

@dp.message_handler(state=States.edit_name)
async def process_suggestion(message: types.Message, state: FSMContext):
    new_name = message.text
    state_data = await state.get_data()
    event_id = state_data.get('event_id')
    if str(message.from_user.id) in ADMIN:
        db_functions.update_event_by_id(event_id, new_name=new_name)
    await message.answer("Вы успешно изменили название")



@dp.message_handler(state=States.waiting_for_suggestion)
async def process_suggestion(message: types.Message, state: FSMContext):
    suggestion = message.text

    db_functions.add_suggestion_to_db(message.chat.id, suggestion)

    await state.finish()

    await message.answer("Спасибо за предложение! Оно было успешно добавлено в базу данных.",  reply_markup=main_menu())

    # add_suggestion_to_db(message.chat.id, suggestion)
    #
    # await state.finish()
    #
    #
    # print('hahahha')
    # await States.edit_name.set()
    # print('hahahha')
    # event_id = int(callback_query.data.split(":")[1])
    # if str(callback_query.from_user.id) in ADMIN:
    #     print('hahahha')
    #     db_functions.update_event_by_id(event_id)
    # await callback_query.message.edit_text(f"Вы успешно изменили название", reply_markup=main_menu())

@dp.callback_query_handler(lambda query: query.data.startswith("back:"), state='*')
async def process_back_to_edit_event(callback_query: types.CallbackQuery, state: FSMContext):
    await States.edit_event.set()
    event_id = int(callback_query.data.split(":")[1])
    await callback_query.answer()
    await callback_query.message.edit_text('', reply_markup=edit_event(event_id))


@dp.callback_query_handler(lambda c: c.data == 'news', state='*')
async def process_news_menu(callback_query: types.CallbackQuery, state: FSMContext):
    await States.news.set()
    await callback_query.answer()
    await callback_query.message.edit_text("3НовостиРу", reply_markup=news())


@dp.callback_query_handler(lambda c: c.data == 'suggestions', state='*')
async def process_suggestions_menu(callback_query: types.CallbackQuery, state: FSMContext):
    await States.waiting_for_suggestion.set()
    await callback_query.answer()
    await callback_query.message.edit_text("Что бы вы предложили")






@dp.callback_query_handler(lambda c: c.data == 'faq', state='*')
async def process_faq_menu(callback_query: types.CallbackQuery, state: FSMContext):
    await States.faq.set()
    await callback_query.answer()
    await callback_query.message.edit_text("4вопрос-ответ", reply_markup=faq())


@dp.callback_query_handler(lambda c: c.data == 'back', state=(States.events, States.suggestions,
                                                              States.news, States.faq))
async def process_back(callback_query: types.CallbackQuery, state: FSMContext):
    await States.main_menu.set()
    await callback_query.answer()
    await callback_query.message.edit_text("Выберите действие:", reply_markup=main_menu())

@dp.callback_query_handler(lambda c: c.data == 'back', state=(States.list_of_events, States.sign_up_for_event))
async def process_back_to_events(callback_query: types.CallbackQuery, state: FSMContext):
    await States.events.set()
    await callback_query.answer()
    await callback_query.message.edit_text("Выберите действие:", reply_markup=events(str(callback_query.from_user.id)))

@dp.callback_query_handler(lambda c: c.data == 'back', state=States.handle_event_button)
async def process_back_to_events_from_description(callback_query: types.CallbackQuery, state: FSMContext):
    await States.sign_up_for_event.set()
    await callback_query.answer()
    list_of_events = db_functions.get_all_events()
    await callback_query.message.edit_text(list_of_events, reply_markup=sign_up_for_event(list_of_events))



def main_menu():
    keyboard = InlineKeyboardMarkup(row_width=1)
    buttons = [
        InlineKeyboardButton("Мероприятия", callback_data='events'),
        InlineKeyboardButton("Предложения", callback_data='suggestions'),
        InlineKeyboardButton("Новости", callback_data='news'),
        InlineKeyboardButton("Вопрос-Ответ", callback_data='faq')
    ]

    keyboard.add(*buttons)
    # button_phone = types.KeyboardButton(text="SHARE", request_contact=True)
    # keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    # keyboard.add(button_phone)
    return keyboard

def events(user_id):
    keyboard = InlineKeyboardMarkup(row_width=1)
    buttons = [
        InlineKeyboardButton("Записаться", callback_data='sign_up_for_event'),
        InlineKeyboardButton("Список мероприятии", callback_data='list_of_events'),

    ]
    if user_id in ADMIN:
        buttons.append(InlineKeyboardButton("Добавить мероприятие", callback_data='back'))
    buttons.append(InlineKeyboardButton("Назад", callback_data='back'))
    keyboard.add(*buttons)
    return keyboard

def list_of_events():
    keyboard = InlineKeyboardMarkup(row_width=1)
    buttons = [
        InlineKeyboardButton("Записаться", callback_data='sign_up'),
        InlineKeyboardButton("Список мероприятии", callback_data='list_of_events'),
        InlineKeyboardButton("Назад", callback_data='back')
    ]
    keyboard.add(*buttons)
    return keyboard

def edit_event(event_id):
    keyboard = InlineKeyboardMarkup(row_width=1)
    buttons = [
        InlineKeyboardButton("Изменить название", callback_data=f'edit_name:{event_id}'),
        InlineKeyboardButton("Изменить дату", callback_data=f'edit_date:{event_id}'),
        InlineKeyboardButton("Изменить описание", callback_data=f'edit_description:{event_id}'),
        InlineKeyboardButton("Назад", callback_data=f'back:{event_id}')
    ]
    keyboard.add(*buttons)
    return keyboard

def sign_up_for_event(list):
    list_of_events = list
    keyboard = InlineKeyboardMarkup(row_width=1)
    buttons = [InlineKeyboardButton(f"Мероприятие: {event[1]}", callback_data=f'event_button:{event[0]}') for event in list_of_events]
    buttons.append(InlineKeyboardButton("Назад", callback_data='back'))
    # buttons = [
    #
    #     InlineKeyboardButton("Записаться", callback_data='sign_up'),
    #     InlineKeyboardButton("Список мероприятии", callback_data='list_of_events'),
    #     InlineKeyboardButton("Назад", callback_data='back')
    # ]
    keyboard.add(*buttons)
    return keyboard

def suggestions():
    keyboard = InlineKeyboardMarkup(row_width=1)
    buttons = [
        InlineKeyboardButton("ввод данных", callback_data='add_suggestion'),
        InlineKeyboardButton("Назад", callback_data='back')
    ]
    keyboard.add(*buttons)
    return keyboard

def news():
    keyboard = InlineKeyboardMarkup(row_width=1)
    buttons = [
        InlineKeyboardButton("Назад", callback_data='back')
    ]
    keyboard.add(*buttons)
    return keyboard

def faq():
    keyboard = InlineKeyboardMarkup(row_width=1)
    buttons = [
        InlineKeyboardButton("Вопрос1", callback_data='question1'),
        InlineKeyboardButton("Вопрос2", callback_data='question2'),
        InlineKeyboardButton("Вопрос3", callback_data='question3'),
        InlineKeyboardButton("Вопрос4", callback_data='question4'),
        InlineKeyboardButton("Назад", callback_data='back')
    ]
    keyboard.add(*buttons)
    return keyboard


@dp.message_handler(lambda message: message.text.lower() == 'event')
async def start_adding_event(message: Message):
    event_name = message.text
    db_functions.add_event_to_db(event_name, 'trololo')
    await message.answer('Введите название мероприятия:' + event_name)



if __name__ == '__main__':
    if not os.path.exists(DB_PATH):
        dbinit.create_bd()
    executor.start_polling(dp, skip_updates=False)


# class dialog(StatesGroup):
#     spam = State()
#     blacklist = State()
#     whitelist = State()


# async def remind_about_bd_to_admin():
#     await bot.send_message(1036000641, f'keke')
#     print("its birthday of smt")



# @dp.message_handler(commands=['start'])
# async def start(message: Message):
#     cur = conn.cursor()
#     cur.execute(f"SELECT block FROM users WHERE user_id = {message.chat.id}")
#     result = cur.fetchone()
#     print(message.from_user.id)
#
#     if message.from_user.id == ADMIN:
#         keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
#         keyboard.add(types.InlineKeyboardButton(text="Рассылка"))
#         keyboard.add(types.InlineKeyboardButton(text="Добавить в ЧС"))
#         keyboard.add(types.InlineKeyboardButton(text="Убрать из ЧС"))
#         await message.answer('Добро пожаловать в Админ-Панель! Выберите действие на клавиатуре', reply_markup=keyboard)
#     else:
#         print(result)
#         if result is None:
#             cur = conn.cursor()
#             cur.execute(f'''SELECT * FROM users WHERE (user_id="{message.from_user.id}")''')
#             entry = cur.fetchone()
#             print(entry)
#             if entry is None:
#                 cur.execute(f'''INSERT INTO users VALUES ('{message.from_user.id}', '0')''')
#             conn.commit()
#             await message.answer('Ты был заблокирован!')
#         else:
#             await message.answer('Привет', reply_markup=inline_kb_full)


# @dp.message_handler(content_types=['text'], text='Рассылка')
# async def spam(message: Message):
#     if message.from_user.id == ADMIN:
#         await dialog.spam.set()
#         await message.answer('Напиши текст рассылки')
#     else:
#         await message.answer('Вы не являетесь админом')


# @dp.message_handler(state=dialog.spam)
# async def start_spam(message: Message, state: FSMContext):
#     if message.text == 'Назад':
#         keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
#         keyboard.add(types.InlineKeyboardButton(text="Рассылка"))
#         keyboard.add(types.InlineKeyboardButton(text="Добавить в ЧС"))
#         keyboard.add(types.InlineKeyboardButton(text="Убрать из ЧС"))
#         await message.answer('Главное меню', reply_markup=keyboard)
#         await state.finish()
#     else:
#         spam_base = cur.fetchall()
#         print(spam_base)
#         for z in range(len(spam_base)):
#             print(spam_base[z][0])
#         for z in range(len(spam_base)):
#             await bot.send_message(spam_base[z][0], message.text)
#         await message.answer('Рассылка завершена')
#         await state.finish()


# @dp.message_handler(state='*', text='Назад')
# async def back(message: Message):
#     if message.from_user.id == ADMIN:
#         keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
#         keyboard.add(types.InlineKeyboardButton(text="Рассылка"))
#         keyboard.add(types.InlineKeyboardButton(text="Добавить в ЧС"))
#         keyboard.add(types.InlineKeyboardButton(text="Убрать из ЧС"))
#         await message.answer('Главное меню', reply_markup=keyboard)
#     else:
#         await message.answer('Вам не доступна эта функция')


# @dp.message_handler(content_types=['text'], text='Добавить в ЧС')
# async def hanadler(message: types.Message, state: FSMContext):
#     if message.chat.id == ADMIN:
#         keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
#         keyboard.add(types.InlineKeyboardButton(text="Назад"))
#         await message.answer(
#             'Введите id пользователя, которого нужно заблокировать.\nДля отмены нажмите кнопку ниже',
#             reply_markup=keyboard)
#         await dialog.blacklist.set()


# @dp.message_handler(state=dialog.blacklist)
# async def proce(message: types.Message, state: FSMContext):
#     if message.text == 'Назад':
#         keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
#         keyboard.add(types.InlineKeyboardButton(text="Рассылка"))
#         keyboard.add(types.InlineKeyboardButton(text="Добавить в ЧС"))
#         keyboard.add(types.InlineKeyboardButton(text="Убрать из ЧС"))
#         await message.answer('Отмена! Возвращаю назад.', reply_markup=keyboard)
#         await state.finish()
#     else:
#         if message.text.isdigit():
#             cur = conn.cursor()
#             cur.execute(f"SELECT block FROM users WHERE user_id = {message.text}")
#             result = cur.fetchall()
#             # conn.commit()
#             if len(result) == 0:
#                 keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
#                 keyboard.add(types.InlineKeyboardButton(text="Рассылка"))
#                 keyboard.add(types.InlineKeyboardButton(text="Добавить в ЧС"))
#                 keyboard.add(types.InlineKeyboardButton(text="Убрать из ЧС"))
#                 await message.answer('Такой пользователь не найден в базе данных.', reply_markup=keyboard)
#                 await state.finish()
#             else:
#                 a = result[0]
#                 id = a[0]
#                 if id == 0:
#                     cur.execute(f"UPDATE users SET block = 1 WHERE user_id = {message.text}")
#                     conn.commit()
#                     keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
#                     keyboard.add(types.InlineKeyboardButton(text="Рассылка"))
#                     keyboard.add(types.InlineKeyboardButton(text="Добавить в ЧС"))
#                     keyboard.add(types.InlineKeyboardButton(text="Убрать из ЧС"))
#                     await message.answer('Пользователь успешно добавлен в ЧС.', reply_markup=keyboard)
#                     await state.finish()
#                     await bot.send_message(message.text, 'Ты получил от администрацией.')
#                 else:
#                     keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
#                     keyboard.add(types.InlineKeyboardButton(text="Рассылка"))
#                     keyboard.add(types.InlineKeyboardButton(text="Добавить в ЧС"))
#                     keyboard.add(types.InlineKeyboardButton(text="Убрать из ЧС"))
#                     await message.answer('Данный пользователь уже получил бан', reply_markup=keyboard)
#                     await state.finish()
#         else:
#             await message.answer('Ты вводишь буквы...\n\nВведи ID')


# @dp.message_handler(content_types=['text'], text='Убрать из ЧС')
# async def hfandler(message: types.Message, state: FSMContext):
#     cur = conn.cursor()
#     cur.execute(f"SELECT block FROM users WHERE user_id = {message.chat.id}")
#     result = cur.fetchone()
#     if result is None:
#         if message.chat.id == ADMIN:
#             keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
#             keyboard.add(types.InlineKeyboardButton(text="Назад"))
#             await message.answer(
#                 'Введите id пользователя, которого нужно разблокировать.\nДля отмены нажмите кнопку ниже',
#                 reply_markup=keyboard)
#             await dialog.whitelist.set()


# @dp.message_handler(state=dialog.whitelist)
# async def proc(message: types.Message, state: FSMContext):
#     if message.text == 'Отмена':
#         keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
#         keyboard.add(types.InlineKeyboardButton(text="Рассылка"))
#         keyboard.add(types.InlineKeyboardButton(text="Добавить в ЧС"))
#         keyboard.add(types.InlineKeyboardButton(text="Убрать из ЧС"))
#         await message.answer('Отмена! Возвращаю назад.', reply_markup=keyboard)
#         await state.finish()
#     else:
#         if message.text.isdigit():
#
#             if len(result) == 0:
#                 keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
#                 keyboard.add(types.InlineKeyboardButton(text="Рассылка"))
#                 keyboard.add(types.InlineKeyboardButton(text="Добавить в ЧС"))
#                 keyboard.add(types.InlineKeyboardButton(text="Убрать из ЧС"))
#                 await message.answer('Такой пользователь не найден в базе данных.', reply_markup=keyboard)
#                 await state.finish()
#             else:
#                 a = result[0]
#                 id = a[0]
#                 if id == 1:
#                     cur = conn.cursor()
#                     cur.execute(f"UPDATE users SET block = 0 WHERE user_id = {message.text}")
#                     conn.commit()
#                     keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
#                     keyboard.add(types.InlineKeyboardButton(text="Рассылка"))
#                     keyboard.add(types.InlineKeyboardButton(text="Добавить в ЧС"))
#                     keyboard.add(types.InlineKeyboardButton(text="Убрать из ЧС"))
#                     await message.answer('Пользователь успешно разбанен.', reply_markup=keyboard)
#                     await state.finish()
#                     await bot.send_message(message.text, 'Вы были разблокированы администрацией.')
#                 else:
#                     keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
#                     keyboard.add(types.InlineKeyboardButton(text="Рассылка"))
#                     keyboard.add(types.InlineKeyboardButton(text="Добавить в ЧС"))
#                     keyboard.add(types.InlineKeyboardButton(text="Убрать из ЧС"))
#                     await message.answer('Данный пользователь не получал бан.', reply_markup=keyboard)
#                     await state.finish()
#         else:
#             await message.answer('Ты вводишь буквы...\n\nВведи ID')
