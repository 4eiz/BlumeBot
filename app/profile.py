import os
from dotenv import load_dotenv

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext

from app.fsm import OrderForm
from keyboards import client as k
from config import bot

from data import users as u
from data import whitelist as w
from data import orders as o

router = Router()


load_dotenv()
orders_photo = os.getenv("photo_orders")




@router.callback_query(k.Menu_callback.filter(F.menu == 'profile'))
async def profile(call: CallbackQuery, callback_data: k.Menu_callback, state: FSMContext):
    
    await call.message.delete()

    user_id = call.from_user.id

    whitelist_status = await w.is_in_whitelist(user_id=user_id)
    if not whitelist_status:
        return

    stats = await u.get_user_statistics(user_id=user_id)

    

    # Формируем текст с HTML-форматированием
    text = (
        f"<b>Ваша статистика:</b>\n\n"
        f"<b>Дата присоединения:</b> <code>{stats['joined_at']}</code>\n"
        f"<b>Заработано денег:</b> <code>${stats['total_earnings']}</code>\n"
        f"<b>Выговоры:</b> <code>{stats['warnings']}</code>\n\n"
        f"<b>Активные заказы:</b> <code>{stats['active_orders_count']}</code>\n"
        f"<b>Отклонённые заказы:</b> <code>{stats['rejected_orders_count']}</code>\n"
    )

    notifications = await u.check_regular_notifications(user_id=user_id)

    # Загружаем фото профиля
    photo = FSInputFile(f'photos/{orders_photo}')
    kb = k.profile_kb(notifications=notifications)

    # Отправляем фото и текст с HTML-форматированием
    await call.message.answer_photo(photo=photo, caption=text, reply_markup=kb)



@router.callback_query(k.Menu_callback.filter(F.menu == 'notifications'))
async def profile(call: CallbackQuery, callback_data: k.Menu_callback, state: FSMContext):


    user_id = call.from_user.id

    whitelist_status = await w.is_in_whitelist(user_id=user_id)
    if not whitelist_status:
        return

    await u.toggle_regular_notifications(user_id=user_id)


    notifications = await u.check_regular_notifications(user_id=user_id)
    kb = k.profile_kb(notifications=notifications)

    await call.message.edit_reply_markup(reply_markup=kb)