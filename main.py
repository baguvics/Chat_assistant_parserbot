import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, executor, types


load_dotenv()
API_KEY = os.environ.get('TELEGRAM_TOKEN')

bot = Bot(token=API_KEY)
dp = Dispatcher(bot)

@dp.message_handler(commands='start')
async def start(message: types.Message):
    bot_started = False
    your_id = message.from_id
    chat_id = message.chat.id
    your_name = message.from_user.username
    if bot_started:
        await message.answer(f"Еще раз привет, {your_name}, айди {chat_id}!")
    else:
        bot_started = True
        await message.answer(f"Привет, {your_name} айди {chat_id}!")


@dp.message_handler(lambda message: "key" in message.text.lower())
@dp.edited_message_handler(lambda message: message.text and "key word" in message.text.lower())
async def some_keyword_handler(message: types.Message):
    your_id = message.from_id
    chat_id = message.chat.id
    your_name = message.from_user.username
    to_chat_id = "-949879393"
    await bot.forward_message(to_chat_id, chat_id, message.message_id)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
