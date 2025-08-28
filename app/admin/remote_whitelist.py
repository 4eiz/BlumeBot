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
from data import users as u

from app.fsm import Whitelist



router = Router()

load_dotenv()
admin = os.getenv("admin")
photo_wh = os.getenv("photo_wh")



@router.callback_query(k.Menu_callback.filter(F.menu == 'add_user'))
async def add_to_whitelist(call: CallbackQuery, callback_data: k.Menu_callback, state: FSMContext):

    await call.message.delete()

    id_of_user = call.from_user.id
    response = await u.is_admin(user_id=id_of_user)
    if not response:
        return

    text = f'<b>Введите айди юзера, для добавления в вайт-лист:</b>'
    kb = k.cancel_admin_kb()
    photo = FSInputFile(f'photos/{photo_wh}')

    await call.message.answer_photo(photo=photo, caption=text, reply_markup=kb)
    
    await state.set_state(Whitelist.add_user)


@router.message(Whitelist.add_user)
async def get_id_for_add(message: Message, state: FSMContext):

    id_of_user = message.from_user.id
    response = await u.is_admin(user_id=id_of_user)
    if not response:
        return

    try:
        user_id = int(message.text)
    except:
        text = '<b>⚠️ Айди юзера должен быть числом!</b>'
        await message.reply(text=text)
        return
    

    await w.add_to_whitelist(user_id=user_id)

    text = f'<b>Пользователь с айди <code>{user_id}</code> добавлен в вайт-лист</b>'
    kb = k.cancel_admin_kb()
    await message.answer(text=text, reply_markup=kb)

    await state.clear()






@router.callback_query(k.Menu_callback.filter(F.menu == 'ban_user'))
async def delete_from_whitelist(call: CallbackQuery, callback_data: k.Menu_callback, state: FSMContext):

    await call.message.delete()

    user_id = call.from_user.id
    user_for_ban = int(callback_data.data)

    response = await u.is_admin(user_id=user_id)
    if not response:
        return

    text = f'<b>Вы уверены, что хотите выгнать юзера {user_for_ban}</b>'
    kb = k.ban_user_kb()

    await call.message.answer(text=text, reply_markup=kb)
    
    await state.set_state(Whitelist.ban_user)
    await state.update_data(user_for_ban=user_for_ban)



@router.callback_query(k.Menu_callback.filter(F.menu == 'yes'), Whitelist.ban_user)
async def get_id_for_ban(call: CallbackQuery, callback_data: k.Menu_callback, state: FSMContext):

    user_id = call.from_user.id
    await call.message.delete()

    response = await u.is_admin(user_id=user_id)
    if not response:
        text = '<b>У вас нет доступа</b>'
        await call.message.answer(text=text)
        return

    data = await state.get_data()
    user_for_ban = data['user_for_ban']
    
    status = await u.delete_user_data(user_id=user_for_ban)
    if status:
        text = f'<b>Пользователь с айди <code>{user_id}</code> был выгнан из студии</b>'

    else:
        text = f'<b>⚠️ Ошибка при удалении юзера с айди <code>{user_id}</code></b>'

    kb = k.cancel_menu_kb()
    await call.message.answer(text=text, reply_markup=kb)

    await state.clear()