from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton


kb_client = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)

btn1 = KeyboardButton('Employee1')
btn2 = KeyboardButton('Employee2')
btn3 = KeyboardButton('Employee3')
btn4 = KeyboardButton('Employee4')
btn5 = KeyboardButton('Employee5')
btn6 = KeyboardButton('Employee6')
btn7 = KeyboardButton('Employee7')

kb_client.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7)

kb_help = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

btn1 = KeyboardButton('/start')
btn2 = KeyboardButton('/help')
btn3 = KeyboardButton('/employeeList')
btn4 = KeyboardButton('/mailing')
btn5 = KeyboardButton('/bonuses')

kb_help.add(btn1, btn2, btn3, btn4, btn5)


inline_btn_1 = InlineKeyboardButton('Мероприятия', callback_data='meets')
inline_kb1 = InlineKeyboardMarkup().add(inline_btn_1)

inline_kb_full = InlineKeyboardMarkup(row_width=2).add(inline_btn_1)
inline_kb_full.add(InlineKeyboardButton('Предложения', callback_data='suggests'))
inline_kb_full.add(InlineKeyboardButton('Новости', callback_data='news'))
inline_kb_full.add(InlineKeyboardButton('FAQ', callback_data='faq'))



# inline_btn_3 = InlineKeyboardButton('кнопка 3', callback_data='btn3')
# inline_btn_4 = InlineKeyboardButton('кнопка 4', callback_data='btn4')
# inline_btn_5 = InlineKeyboardButton('кнопка 5', callback_data='btn5')
# inline_kb_full.add(inline_btn_3, inline_btn_4, inline_btn_5)
# inline_kb_full.row(inline_btn_3, inline_btn_4, inline_btn_5)
# inline_kb_full.insert(InlineKeyboardButton("query=''", switch_inline_query=''))
# inline_kb_full.insert(InlineKeyboardButton("query='qwerty'", switch_inline_query='qwerty'))
# inline_kb_full.insert(InlineKeyboardButton("Inline в этом же чате", switch_inline_query_current_chat='wasd'))
# inline_kb_full.add(InlineKeyboardButton('Уроки aiogram', url='https://surik00.gitbooks.io/aiogram-lessons/content/'))
