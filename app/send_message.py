import os
from dotenv import load_dotenv

from aiogram import Router
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from keyboards import client as k
from data import users as u
from data import whitelist as w

from config import bot
from app.fsm import Send_message


router = Router()



load_dotenv()
admin = int(os.getenv("admin"))





# Обработка нажатия кнопки 
@router.callback_query(k.Message_callback.filter(F.menu == 'message'))
async def send_msg(call: CallbackQuery, callback_data: k.Message_callback, state: FSMContext):
    
    user_id = call.from_user.id
    whitelist_status = await w.is_in_whitelist(user_id=user_id)
    if not whitelist_status:
        return
    
    text = '<b>🤗 Напиши своё сообщение:</b>'
    await call.message.answer(text=text)
    await state.set_state(Send_message.text)

    topic = callback_data.topic
    user_id_for_send = callback_data.user_id
    order_id = callback_data.order_id
    await state.update_data(user_id_for_send=user_id_for_send, order_id=order_id, topic=topic)




# Обработка файла
@router.message(Send_message.text)
async def send_msg2(message: Message, state: FSMContext):

    user_id = message.from_user.id
    message_id = message.message_id
    username = message.from_user.username

    await bot.delete_message(chat_id=user_id, message_id=message_id-1)

    data = await state.get_data()
    user_id_for_send = data['user_id_for_send']
    order_id = data['order_id']
    topic = data['topic']
    text_original = message.text

    admin_status = await u.is_admin(user_id=user_id)
    if admin_status:
        print('admin_status')

        text = f'<b>Заказ:</b> <code>#{order_id}</code>\n\n{text_original}'

        if user_id == admin:

            admin_username = message.from_user.username
            admin_text = f'<b>Ответ от @{admin_username} (<code>{user_id_for_send}</code>)</b>\n'
            text = admin_text + text

        else:

            admin_text = f'<b>Ответ от менеджера (<code>{user_id_for_send}</code>)</b>\n'
            text = admin_text + text

    else:
        
        text = f'<b>{topic} от @{username} (<code>{user_id_for_send}</code>)</b>\n<b>Заказ:</b> <code>#{order_id}</code>\n\n{text_original}'


        


    kb = k.reply_kb(user_id=user_id, order_id=order_id, topic=topic)

    await bot.send_message(chat_id=user_id_for_send, text=text, reply_markup=kb)
    
    text = '✅ <b><u>Сообщение доставлено!</u></b>'
    await message.answer(text=text)

    await state.clear()