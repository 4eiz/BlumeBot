import os
import json
from dotenv import load_dotenv

from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext


from app.form_app import keyboards as k
from config import bot
from app.form_app.data import requests as r
from data import users as u


router = Router()


load_dotenv()
admin = os.getenv("admin")



# ----------------------------------


def deserialize_data(serialized_data):
    # Десериализация данных обратно в словарь
    pairs = serialized_data.split(';')
    data = {key: value for key, value in (pair.split('=') for pair in pairs)}
    return data











@router.callback_query(k.Answer_callback.filter(F.answer == 'accept'))
async def accept_form(call: CallbackQuery, callback_data: k.Answer_callback, state: FSMContext):

    user_id = callback_data.user_id
    data = await r.get_request(user_id=user_id)
    data = json.loads(data[1])  # Преобразуем обратно в словарь


    user_id = data['user_id']
    name = data['name']
    specialty = data['specialty']
    stack = data['stack']
    preferred_orders = data['preferred_orders']
    rank = callback_data.rank


    await r.delete_request(user_id=user_id)
    await u.add_user(
        user_id=user_id, 
        username=name, 
        role=rank, 
        specialty=specialty, 
        stack=stack, 
        preferred_orders=preferred_orders
    )

    
    kb = k.menu_kb()
    text = "<b>Заявка рассмотрена ✅</b>"
    await bot.send_message(chat_id=user_id, text=text, reply_markup=kb)

    kb = k.accept()
    await call.message.edit_reply_markup(reply_markup=kb)







@router.callback_query(k.Answer_callback.filter(F.answer == 'decline'))
async def decline_form(call: CallbackQuery, callback_data: k.Answer_callback, state: FSMContext):

    user_id = callback_data.user_id

    text = '<b>Ваша заявка отклонена</b>'
    await bot.send_message(chat_id=user_id, text=text)

    kb = k.decline()
    await call.message.edit_reply_markup(reply_markup=kb)
    
    await r.delete_request(user_id=user_id)