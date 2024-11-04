import asyncio
import logging
import requests
import re
import keyboards as kb
from aiogram.fsm.context import FSMContext
from aiogram import types, F, Router
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import CommandStart, StateFilter
from config import TOKEN, FTOKEN, ADMIN_IDS, secret
from LOLZTEAM.API import Forum, Market

logging.basicConfig(level=logging.INFO)

rt = Router()
market = Market(token=FTOKEN, language="en")
forum = Forum(token=FTOKEN, language="en")

class Form(StatesGroup):
    waiting_for_link = State()
    waiting_for_amount = State()
    waiting_for_hold = State()
    waiting_for_message = State()

hvalue = None
hoption = None
hold_meaning = False

@rt.message(CommandStart())
async def start(message: types.Message):
    if message.from_user.id in ADMIN_IDS:
        await message.answer("Привет, ты попал в бота для переводов LOLZTEAM", reply_markup=kb.get_main_kb())

@rt.message(F.text == "Отправить деньги")
async def send(message: types.Message, state: FSMContext):
    if message.from_user.id in ADMIN_IDS:
        sent_message = await message.answer("Отправьте ссылку на пользователя/Его никнейм на форуме")
        await state.update_data(sent_message_id=sent_message.message_id)
        await state.set_state(Form.waiting_for_link)
        await message.delete()

@rt.message(StateFilter(Form.waiting_for_link))
async def get_link(message: types.Message, state: FSMContext):
    link = message.text
    global sent_message_id
    data = await state.get_data()
    sent_message_id = data.get("sent_message_id")
    matc = re.search(r'([^/]+)/?$', link)
    matc1 = re.search(r'members/(\d+)', link)
    global user_n, user_nick, user_tg
    user_nick = message.text
    
    if matc:
        user_n = matc.group(1)
        print(user_n)
        
        url = f"https://api.zelenka.guru/users/{user_n}"
        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {FTOKEN}"
            }
        response = requests.get(url, headers=headers)
        print(response.json()['user']['user_id'])
        try:
            user_nick = response.json()['user']['username']
            user_n = response.json()['user']['user_id']
        except KeyError:
            await message.reply(response.json()['errors'])
            state.clear()
        try:
            user_us = response.json()['user']['custom_fields']['telegram']
            user_tg = f't.me/{user_us}'
        except KeyError:
            user_tg = 'не привязан'
    elif matc1:
         user_n = matc1.group(1)
         print(user_n)
         url = f"https://api.zelenka.guru/users/{user_n}"
         headers = {
             "accept": "application/json",
             "authorization": f"Bearer {FTOKEN}"
             }
         response = requests.get(url, headers=headers)
         print(response.json()['user']['user_id'])
         try:
             user_nick = response.json()['user']['username']
             user_n = response.json()['user']['user_id']
         except KeyError:
             await message.reply(response.json()['errors'])
             state.clear()
         try:
             user_us = response.json()['user']['custom_fields']['telegram']
             user_tg = f't.me/{user_us}'
         except KeyError:
             user_tg = 'не привязан'          
    else:
        
        response = forum.users.search(username=user_nick)
        print(response.json()['users'][0]['user_id'])
        try:
            user_n = response.json()['users'][0]['user_id']
        except KeyError:
            await message.bot.edit_message_text(chat_id=message.chat.id,
                                                message_id=sent_message_id,
                                                text='произошла ошибка')
            state.clear()
        try:
            user_tg = response.json()['users'][0]['custom_fields']['telegram']
        except KeyError:
            user_tg = 'не привязан'

    if sent_message_id:
        await message.delete()
        await message.bot.edit_message_text(chat_id=message.chat.id,
                                            message_id=sent_message_id,
                                            text=f'Пользователь: lzt.market/members/{user_n}\nВведите сумму в рублях')
        await state.set_state(Form.waiting_for_amount)
        
@rt.message(StateFilter(Form.waiting_for_amount))
async def amount(message: types.Message, state: FSMContext):
    global price_id
    price = message.text
    print(price)
    if price.isdigit():    
        price_id = int(price)
        print(f'qq{price_id}')
        if price_id>=10:
            await message.bot.edit_message_text(chat_id=message.chat.id,
                                                message_id=sent_message_id,
                                                text=f"Сумма: {price_id}₽\nНикнейм получателя: {user_nick}\nСсылка на получателя: lzt.market/members/{user_n}\nTelegram получателя: {user_tg}\nНужен ли холд?", reply_markup=kb.get_hold_kb())
        else:
            global hold_meaning
            hold_meaning = False
            await message.bot.edit_message_text(chat_id=message.chat.id,
                                                message_id=sent_message_id,
                                                text=f"Сумма: {price_id}₽\nНикнейм получателя: {user_nick}\nСсылка на получателя: lzt.market/members/{user_n}\nTelegram получателя: {user_tg}\nОставить комментарий к платежу?", reply_markup=kb.get_msg_kb())
    else:
        await message.answer("Сумма должна быть числом")
        await state.clear()
    await message.delete()

@rt.callback_query(F.data == 'holdon')
async def holdon(callback_query: types.CallbackQuery, state: FSMContext):
    global hold_meaning
    hold_meaning = True
    await callback_query.message.edit_text("Введите продолжительность холда\nДоступные параметры: 'hour', 'day', 'week', 'month'\nПример: 3 day")
    await state.set_state(Form.waiting_for_hold)

@rt.message(StateFilter(Form.waiting_for_hold))
async def hold(message: types.Message, state: FSMContext):  
    try:
        global hvalue, hoption
        holdam = message.text
        parts = [part.strip() for part in holdam.split(" ")]
        hvalue = parts[0]
        hoption = parts[1]
        await message.bot.edit_message_text(chat_id=message.chat.id,
                                            message_id=sent_message_id,
                                            text=f'Сумма: {price_id}₽\nНикнейм получателя: {user_nick}\nСсылка на получателя: lzt.market/members/{user_n}\nTelegram получателя: {user_tg}\nХолд: {hvalue} {hoption}\nОставить комментарий к платежу?', reply_markup=kb.get_msg_kb())
    except Exception as e:
        await message.answer(f"{e}")
        await state.clear()
    await message.delete()

@rt.callback_query(F.data == 'holdoff')
async def holdoff(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text(f'Сумма: {price_id}₽\nНикнейм получателя: {user_nick}\nСсылка на получателя: lzt.market/members/{user_n}\nTelegram получателя: {user_tg}\nОставить комментарий к платежу?', reply_markup=kb.get_msg_kb())


@rt.callback_query(F.data == 'msgadd')
async def msgadd(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.edit_text("Введите комментарий к платежу:")
    await state.set_state(Form.waiting_for_message)

@rt.message(StateFilter(Form.waiting_for_message))
async def wait_msg(message: types.Message, state: FSMContext):
    global pay_msg
    pay_msg=message.text
    if hold_meaning == True:
        await message.bot.edit_message_text(chat_id=message.chat.id,
                                                message_id=sent_message_id,
                                                text=f'Сумма: {price_id}₽\nНикнейм получателя: {user_nick}\nСсылка на получателя: lzt.market/members/{user_n}\nTelegram получателя: {user_tg}\nХолд: {hvalue} {hoption}\nКомментарий: {pay_msg}\nОтправить деньги?', reply_markup=kb.get_inline_kb())
    else:
        await message.bot.edit_message_text(chat_id=message.chat.id,
                                                message_id=sent_message_id,
                                                text=f'Сумма: {price_id}₽\nНикнейм получателя: {user_nick}\nСсылка на получателя: lzt.market/members/{user_n}\nTelegram получателя: {user_tg}\nКомментарий: {pay_msg}\nОтправить деньги?', reply_markup=kb.get_inline_kb())
    await message.delete()
    await state.clear()
        
@rt.callback_query(F.data == 'msgdel')
async def msgdel(callback_query: types.CallbackQuery):
    global pay_msg
    pay_msg = None
    if hold_meaning == True:
        await callback_query.message.edit_text(f'Сумма: {price_id}₽\nНикнейм получателя: {user_nick}\nСсылка на получателя: lzt.market/members/{user_n}\nTelegram получателя: {user_tg}\nХолд: {hvalue} {hoption}\nОтправить деньги?', reply_markup=kb.get_inline_kb())       
    else:
        await callback_query.message.edit_text(f'Сумма: {price_id}₽\nНикнейм получателя: {user_nick}\nСсылка на получателя: lzt.market/members/{user_n}\nTelegram получателя: {user_tg}\nОтправить деньги?', reply_markup=kb.get_inline_kb())

        





@rt.callback_query(F.data == 'approve_')
async def approve(callback_query: types.CallbackQuery):
   
    response = market.payments.transfer(user_id=user_n, amount=price_id, currency="rub", transfer_hold=hold_meaning, hold_length_value=hvalue, hold_length_option=hoption, comment=pay_msg, secret_answer=secret)
    if 'errors' in response.json():
        errors = response.json()['errors']
        await callback_query.message.edit_text(f'Произошла ошибка: {errors}')
    else:
        await callback_query.message.edit_text(f'{price_id}₽ успешно отправлено пользователю lzt.market/members/{user_n} ({user_nick})')


@rt.callback_query(F.data == 'reject_')
async def reject(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text('Отменено')




