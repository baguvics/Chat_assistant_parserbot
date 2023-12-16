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
ADMIN = 10360006411


logging.basicConfig(level=logging.INFO)

storage = MemoryStorage()
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)

class States(StatesGroup):
    events = State()
    suggestions = State()
    news = State()
    faq = State()

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    # Устанавливаем начальное состояние
    await States.events.set()
    await message.answer("Привет! Выберите действие:", reply_markup=main_menu())

@dp.callback_query_handler(lambda c: c.data == 'main_menu', state='*')
async def process_main_menu(callback_query: types.CallbackQuery, state: FSMContext):
    await States.events.set()
    await callback_query.answer()
    await callback_query.message.edit_text("1Главное", reply_markup=main_menu())

@dp.callback_query_handler(lambda c: c.data == 'events', state='*')
async def process_events_menu(callback_query: types.CallbackQuery, state: FSMContext):
    await States.suggestions.set()
    await callback_query.answer()
    await callback_query.message.edit_text("2Мероприятия", reply_markup=events())

@dp.callback_query_handler(lambda c: c.data == 'news', state='*')
async def process_news_menu(callback_query: types.CallbackQuery, state: FSMContext):
    await States.suggestions.set()
    await callback_query.answer()
    await callback_query.message.edit_text("3НовостиРу", reply_markup=news())

@dp.callback_query_handler(lambda c: c.data == 'suggestions', state='*')
async def process_suggestions_menu(callback_query: types.CallbackQuery, state: FSMContext):
    await States.suggestions.set()
    await callback_query.answer()
    await callback_query.message.edit_text("Что бы вы предложили", reply_markup=suggestions())

@dp.callback_query_handler(lambda c: c.data == 'faq', state='*')
async def process_faq_menu(callback_query: types.CallbackQuery, state: FSMContext):
    await States.suggestions.set()
    await callback_query.answer()
    await callback_query.message.edit_text("4вопрос-ответ", reply_markup=faq())

@dp.callback_query_handler(lambda c: c.data == 'back', state=States.suggestions)
@dp.callback_query_handler(lambda c: c.data == 'back', state=States.news)
@dp.callback_query_handler(lambda c: c.data == 'back', state=States.faq)
async def process_back(callback_query: types.CallbackQuery, state: FSMContext):
    await States.events.set()
    await callback_query.answer()
    await callback_query.message.edit_text("Выберите действие:", reply_markup=main_menu())

def main_menu():
    keyboard = InlineKeyboardMarkup(row_width=1)
    buttons = [
        InlineKeyboardButton("Мероприятия", callback_data='events'),
        InlineKeyboardButton("Предложения", callback_data='suggestions'),
        InlineKeyboardButton("Новости", callback_data='news'),
        InlineKeyboardButton("Вопрос-Ответ", callback_data='faq')
    ]
    keyboard.add(*buttons)
    return keyboard

def events():
    keyboard = InlineKeyboardMarkup(row_width=1)
    buttons = [
        InlineKeyboardButton("Записаться", callback_data='invite'),
        InlineKeyboardButton("Список мероприятии", callback_data='events'),
        InlineKeyboardButton("Назад", callback_data='back')
    ]
    keyboard.add(*buttons)
    return keyboard

def suggestions():
    keyboard = InlineKeyboardMarkup(row_width=1)
    buttons = [
        InlineKeyboardButton("ввод данных", callback_data='event_list'),
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
