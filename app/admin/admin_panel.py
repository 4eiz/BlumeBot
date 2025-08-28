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

from config import bot


router = Router()


load_dotenv()
admin = int(os.getenv("admin"))




@router.callback_query(k.Menu_callback.filter(F.menu == 'admin_panel'))
async def get_orders(call: CallbackQuery, callback_data: k.Menu_callback, state: FSMContext):
    
    await call.message.delete()

    if state:
        await state.clear()

    user_id = call.from_user.id

    whitelist_status = await w.is_in_whitelist(user_id=user_id)
    if not whitelist_status:
        return
    
    response = await u.is_admin(user_id=user_id)
    if not response:
        return
    
    text = '<b>Админ панель</b>'
    if user_id == admin:
        kb = k.admin_kb(general_admin=True)
    else:
        kb = k.admin_kb()

    

    await call.message.answer(text=text, reply_markup=kb)