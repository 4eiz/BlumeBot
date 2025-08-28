import os
from dotenv import load_dotenv

from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command, CommandObject
from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext

from keyboards import client as k
from data import users as u
from data import whitelist as w
from data import orders as o

from config import bot
from app.fsm import Newsletters



router = Router()

load_dotenv()
admin = int(os.getenv("admin"))





@router.callback_query(k.Menu_callback.filter(F.menu == 'newsletter'))
async def get_orders(call: CallbackQuery, callback_data: k.Menu_callback, state: FSMContext):
    
    await call.message.delete()

    user_id = call.from_user.id

    whitelist_status = await w.is_in_whitelist(user_id=user_id)
    if not whitelist_status:
        return
    
    response = await u.is_admin(user_id=user_id)
    if not response:
        return
    
    text = '<b>Выберите рассылку:</b>'

    kb = k.news_kb()

    await call.message.answer(text=text, reply_markup=kb)



@router.callback_query(k.Menu_callback.filter(F.menu == 'news'))
async def get_orders(call: CallbackQuery, callback_data: k.Menu_callback, state: FSMContext):
    
    await call.message.delete()

    user_id = call.from_user.id

    whitelist_status = await w.is_in_whitelist(user_id=user_id)
    if not whitelist_status:
        return
    
    response = await u.is_admin(user_id=user_id)
    if not response:
        return
    
    text = '<b>Введите сообщение:</b>'

    kb = k.cancel_news_kb()

    await call.message.answer(text=text, reply_markup=kb)

    await state.set_state(Newsletters.text)
    await state.update_data(type=callback_data.data)


@router.message(Newsletters.text)
async def get_orders(message: Message, state: FSMContext):

    user_id = message.from_user.id

    whitelist_status = await w.is_in_whitelist(user_id=user_id)
    if not whitelist_status:
        return
    
    response = await u.is_admin(user_id=user_id)
    if not response:
        return

    news_type = await state.get_data()
    news_type = news_type['type']


    text_news = message.text
    users = await u.get_all_users_notification_settings()

    text = '<b>Рассылка запущена!</b>'
    kb = k.cancel_menu_kb()
    await message.answer(text=text, reply_markup=kb)

    for user in users:

        chat_id = user['user_id']

        if news_type == 'regular':
            if user['rrn'] == 1:
                await bot.send_message(chat_id=chat_id, text=text_news)
            else:
                pass

        elif news_type == 'mandatory':
            await bot.send_message(chat_id=chat_id, text=text_news)

        else:
            text = '<b>⚠️ Ошибка!</b>'
            await message.reply(text=text)
            return




    await state.clear()