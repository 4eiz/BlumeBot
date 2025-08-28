import os
from dotenv import load_dotenv

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext

from app.fsm import Price
from keyboards import client as k
from config import bot

from data import orders as o
from data import whitelist as w


router = Router()


load_dotenv()
orders_photo = os.getenv("photo_orders")
photo_order = os.getenv("photo_order")
admin = int(os.getenv("admin"))




@router.callback_query(k.Menu_callback.filter(F.menu == 'orders'))
async def get_orders(call: CallbackQuery, callback_data: k.Menu_callback, state: FSMContext):

    await call.message.delete()

    user_id = call.from_user.id

    whitelist_status = await w.is_in_whitelist(user_id=user_id)
    if not whitelist_status:
        return

    orders = await o.get_orders_for_user(user_id=user_id)

    kb = k.orders_kb(orders=orders)
    text = 'Список заказов:'
    photo = FSInputFile(f'photos/{orders_photo}')

    await call.message.answer_photo(photo=photo, caption=text, reply_markup=kb)



@router.callback_query(k.Menu_callback.filter(F.menu == 'order'))
async def get_order(call: CallbackQuery, callback_data: k.Menu_callback, state: FSMContext):
    
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
        photo = FSInputFile(f'photos/{photo_order}')
        kb = k.order_kb(admin_id=created_by, order_id=order_id)

        await call.message.answer_photo(photo=photo, caption=text, reply_markup=kb)
    else:
        await call.answer("Заказ не найден.", show_alert=True)




# -------------------------------------------------




@router.callback_query(k.Message_callback.filter(F.menu == 'accept_order'))
async def accept_order(call: CallbackQuery, callback_data: k.Message_callback, state: FSMContext):

    await call.message.delete()

    user_id = call.from_user.id
    order_id = callback_data.order_id
    admin_id = callback_data.user_id
    
    status = await o.set_order_status_in_progress(order_id=order_id)
    if not status:
        text = '<b>⚠️ Заказ уже приняли</b>'
        await call.message.answer(text=text)
        return  
    else:
        status = await o.assign_order_to_user(order_id=order_id, user_id=user_id)
        if not status:
            text = "<b>⚠️ У вас уже максимальное количество заказов</b>"
            await call.message.answer(text=text)
            return  

    text = '<b>Заказ принят</b>'
    photo = FSInputFile(f'photos/{orders_photo}')
    kb = k.order_accept_kb(admin_id=admin_id, order_id=order_id)

    await call.message.answer_photo(photo=photo, caption=text, reply_markup=kb)


    text = f"<b>🥳 Заказ <code>#{order_id}</code> был успешно взят сотрудником <code>{user_id}</code></b>"
    await bot.send_message(chat_id=admin_id, text=text)
    


@router.callback_query(k.Message_callback.filter(F.menu == 'decline_order'))
async def accept_order(call: CallbackQuery, callback_data: k.Message_callback, state: FSMContext):

    await call.message.delete()

    user_id = call.from_user.id
    order_id = callback_data.order_id
    await o.reject_order_assignment(order_id=order_id, user_id=user_id)
    # await o.update_order_status(order_id=order_id, new_status='in_progress') # Не трогать

    text = '<b>Заказ отклонён</b>'
    kb = k.cancel_menu_kb()
    photo = FSInputFile(f'photos/{orders_photo}')

    await call.message.answer_photo(photo=photo, caption=text, reply_markup=kb)




@router.callback_query(k.Menu_callback.filter(F.menu == 'offer_price'))
async def offer_price(call: CallbackQuery, callback_data: k.Menu_callback, state: FSMContext):

    await call.message.delete()

    order_id = str(callback_data.data)
    await state.update_data(order_id=order_id)

    text = '<b>Предложите сумму:</b>'
    kb = k.cancel_menu_kb()

    await call.message.answer(text=text, reply_markup=kb)
    await state.set_state(Price.price)



@router.message(Price.price)
async def send_msg2(message: Message, state: FSMContext):

    data = await state.get_data()
    order_id = data['order_id']

    try:
        price = int(message.text)
    except:
        text = '<b>⚠️ Цена должна быть числом (без символов)!</b>'
        await message.reply(text=text)
        return
    
    
    user_id = message.from_user.id
    user_name = message.from_user.username
    kb = k.price_offer_kb(price=price, order_id=order_id, user_id=user_id)
    if user_name is None:
        user_name = '-'
    else:
        user_name = f'@{user_name} '

    text = f"<b>📝 Новый ценник</b>\n\n" \
        f"<b>👤 Юзер</b> {user_name}(<code>{user_id}</code>)\n" \
        f"<b>⚡️ Заказ</b> <code>#{order_id}</code>\n\n" \
        f"<b>💸 Ценник: </b> <code>{price}</code>"
    
    await bot.send_message(chat_id=admin, text=text, reply_markup=kb)

    text = '<b>Ваша заявка отправлена!</b>'
    kb = k.cancel_menu_kb()
    await message.reply(text=text, reply_markup=kb)

    await state.clear()





@router.callback_query(k.Price_callback.filter(F.menu == 'accept_price'))
async def accept_price(call: CallbackQuery, callback_data: k.Price_callback, state: FSMContext):

    id_user_action = call.from_user.id
    if id_user_action != admin:
        text = 'Недостаточно прав!'
        await call.answer(text=text)
        return

    order_id = callback_data.order_id
    price = callback_data.price
    user_id = callback_data.user_id

    status = await o.update_order_price(order_id=order_id, new_price=price)
    if status:
        text = f'<b>Заявка на новый ценник для заказа <code>#{order_id}</code> была принята</b>'
        kb = k.order_price_kb(order_id=order_id)
        await bot.send_message(chat_id=user_id, text=text, reply_markup=kb)

        kb = k.accepted_kb()
        await call.message.edit_reply_markup(reply_markup=kb)




@router.callback_query(k.Price_callback.filter(F.menu == 'decline_price'))
async def decline_price(call: CallbackQuery, callback_data: k.Price_callback, state: FSMContext):

    id_user_action = call.from_user.id
    if id_user_action != admin:
        text = 'Недостаточно прав!'
        await call.answer(text=text)
        return

    kb = k.declined_kb()
    await call.message.edit_reply_markup(reply_markup=kb)

    order_id = callback_data.order_id
    user_id = callback_data.user_id
    text = f'<b>Заявка на новый ценник для заказа <code>#{order_id}</code> была отклонена</b>'
    kb = k.order_price_kb(order_id=order_id)

    await bot.send_message(chat_id=user_id, text=text, reply_markup=kb)