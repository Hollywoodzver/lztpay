from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.types import KeyboardButton

def get_main_kb():
    keyboard=ReplyKeyboardBuilder()
    keyboard.add(KeyboardButton(text="Отправить деньги"))
    return keyboard.as_markup(resize_keyboard=True)

def get_hold_kb():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="Включить холд", callback_data="holdon")
    keyboard.button(text="Без холда", callback_data="holdoff")
    return keyboard.as_markup()

def get_msg_kb():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text='Добавить комментарий', callback_data='msgadd')
    keyboard.button(text='Не нужен', callback_data='msgdel')
    return keyboard.as_markup()

def get_inline_kb():
    keyboard=InlineKeyboardBuilder()
    keyboard.button(text="Подтверждаю", callback_data="approve_")
    keyboard.button(text="Отмена", callback_data="reject_")
    return keyboard.as_markup()

