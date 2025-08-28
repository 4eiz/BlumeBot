import os
from dotenv import load_dotenv

from aiogram import Router
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, FSInputFile
from aiogram.fsm.context import FSMContext

from keyboards import client as k
from data import users as u
from data import whitelist as w
from data import orders as o

from app.fsm import Decline_order

from config import bot


router = Router()



load_dotenv()
photo_order = os.getenv("photo_order")




# Обработка нажатия кнопки 
@router.callback_query(k.Menu_callback.filter(F.menu == 'active_orders'))
async def active_ords(call: CallbackQuery, callback_data: k.Menu_callback, state: FSMContext):
    
    user_id = call.from_user.id
    whitelist_status = await w.is_in_whitelist(user_id=user_id)
    if not whitelist_status:
        return
    
    await call.message.delete()

    orders = await o.get_active_orders_for_user(user_id=user_id)
    kb = k.active_orders_kb(orders=orders)
    text = '<b>Активные заказы:</b>'

    await call.message.answer(text=text, reply_markup=kb)



# Обработка нажатия кнопки 
@router.callback_query(k.Menu_callback.filter(F.menu == 'active_order'))
async def active_ord(call: CallbackQuery, callback_data: k.Menu_callback, state: FSMContext):
    
    user_id = call.from_user.id
    whitelist_status = await w.is_in_whitelist(user_id=user_id)
    if not whitelist_status:
        return

    await call.message.delete()

    order_id = int(callback_data.data)
    order_data = await o.get_order_by_id(order_id=order_id)

    # Проверяем, существует ли заказ
    if order_data:
        # Распаковываем данные заказа из словаря
        title = order_data["title"]
        description = order_data["description"]
        required_skills = order_data["required_skills"]
        size = order_data["size"]
        price = order_data["price"]
        deadline = order_data["deadline"]
        status = order_data["status"]
        created_at = order_data["created_at"]
        created_by = order_data["created_by"]

        # Форматируем текст сообщения
        text = f"<b>⚡️ Заказ</b> <code>#{order_id}</code>\n\n" \
               f"<b>Краткое описание:</b> {title}\n\n" \
               f"<b>Большое описание:</b> {description}\n\n" \
               f"<b>💸 Сумма:</b> <code>{'-' if price is None else f'${price}'}</code>\n" \
               f"<b>📆 Сроки:</b> <code>{'-' if deadline is None else deadline}</code>"

        # Здесь photo переменная должна содержать имя файла фотографии, если она есть
        # photo = FSInputFile(f'photos/{orders_photo}')
        kb = k.order_profile_kb(admin_id=created_by, order_id=order_id)

        photo = FSInputFile(f'photos/{photo_order}')
        await call.message.answer_photo(photo=photo, caption=text, reply_markup=kb)
    else:
        await call.answer("Заказ не найден.", show_alert=True)



@router.callback_query(k.Message_callback.filter(F.menu == 'decline_active_order'))
async def decline_order(call: CallbackQuery, callback_data: k.Message_callback, state: FSMContext):

    await call.message.delete()

    order_id = int(callback_data.order_id)
    admin_id = int(callback_data.user_id)
    await state.update_data(order_id=order_id, admin_id=admin_id)
    # await o.reject_order_assignment(order_id=order_id, user_id=user_id)
    # await o.update_order_status(order_id=order_id, new_status='open')

    text = '<b>Введите причину отказа:</b>'

    await call.message.answer(text=text)

    await state.set_state(Decline_order.reason)



@router.message(Decline_order.reason)
async def decline_order_reason(message: Message, state: FSMContext):

    try:
        reason = message.text
    except:
        text = '<b>⚠️ Введите причину текстом</b>'
        await message.answer(text=text)
        return

    data = await state.get_data()
    order_id = data['order_id']
    admin_id = data['admin_id']
    user_id = message.from_user.id
    user_name = message.from_user.username

    order_data = await o.get_order_by_id(order_id=order_id)

    # Проверяем, существует ли заказ
    if order_data:
        # Распаковываем данные заказа из словаря
        title = order_data["title"]
        description = order_data["description"]
        required_skills = order_data["required_skills"]
        size = order_data["size"]
        price = order_data["price"]
        deadline = order_data["deadline"]
        status = order_data["status"]
        created_at = order_data["created_at"]
        created_by = order_data["created_by"]

        # Форматируем текст сообщения
        if user_name is not None:
            text = f"<b>⛔ ОТКАЗ ОТ ЗАКАЗА</b>\n\n\n" \
                f"<b>👤 Юзер</b> @{user_name} (<code>#{user_id}</code>)\n" \
                f"<b>⚡️ Заказ</b> <code>#{order_id}</code>\n\n" \
                f"<b>💬 Причина:</b> {reason}\n\n" \
                f"<b>💸 Сумма:</b> <code>{'-' if price is None else f'${price}'}</code>\n" \
                f"<b>📆 Сроки:</b> <code>{'-' if deadline is None else deadline}</code>"
            
        else:
            text = f"<b>⛔ ОТКАЗ ОТ ЗАКАЗА</b>\n\n\n" \
                f"<b>👤 Юзер</b> <code>#{user_id}</code>\n" \
                f"<b>⚡️ Заказ</b> <code>#{order_id}</code>\n\n" \
                f"<b>💬 Причина:</b> {reason}\n\n" \
                f"<b>💸 Сумма:</b> <code>{'-' if price is None else f'${price}'}</code>\n" \
                f"<b>📆 Сроки:</b> <code>{'-' if deadline is None else deadline}</code>"
            
        
        
    kb = k.decline_order_kb(user_id=user_id, order_id=order_id)
    await bot.send_message(chat_id=admin_id, text=text, reply_markup=kb)

    text = f'<b>Заявка на отказ от заказа была отправлена!</b>'
    kb = k.cancel_menu_kb()
    await message.answer(text=text, reply_markup=kb)

    await state.clear()



@router.callback_query(k.Message_callback.filter(F.menu == 'accept_request'))
async def accept_request(call: CallbackQuery, callback_data: k.Message_callback, state: FSMContext):

    order_id = int(callback_data.order_id)
    user_id = int(callback_data.user_id)

    text = f'<b>Заявка на отказ от заказа <code>#{order_id}</code> была принята</b>'
    await bot.send_message(chat_id=user_id, text=text)
    
    await o.reject_order_assignment(order_id=order_id, user_id=user_id)
    await o.set_order_status_open(order_id=order_id)

    kb = k.declined_kb()
    await call.message.edit_reply_markup(reply_markup=kb)


@router.callback_query(k.Message_callback.filter(F.menu == 'decline_request'))
async def decline_request(call: CallbackQuery, callback_data: k.Message_callback, state: FSMContext):

    kb = k.declined_kb()
    await call.message.edit_reply_markup(reply_markup=kb)

    order_id = int(callback_data.order_id)
    user_id = int(callback_data.user_id)

    text = f'<b>Заявка на отказ от заказа <code>#{order_id}</code> была отклонен</b>'
    await bot.send_message(chat_id=user_id, text=text)