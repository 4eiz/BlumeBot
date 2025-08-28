from aiogram.types import CallbackQuery

from config import bot
from data import users as u
from keyboards import client as k


async def handle_blocked_user(call: CallbackQuery):
    user_id = call.from_user.id
    user = await u.get_user_info(user_id=user_id)
    
    if user[3] == 1:
        text = '<b>Вы заблокированны в боте</b>'
        kb = k.support_kb()
        await call.message.answer(text=text, reply_markup=kb)
        return True
    
    chat_id = call.from_user.id
    message_id = call.message.message_id
    await bot.delete_message(chat_id, message_id)
    
    return False