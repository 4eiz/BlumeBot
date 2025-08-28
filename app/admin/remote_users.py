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



router = Router()

load_dotenv()
admin = int(os.getenv("admin"))
photo_users = os.getenv("photo_users")
photo_stats = os.getenv("photo_stats")





@router.callback_query(k.Menu_callback.filter(F.menu == 'users'))
async def get_orders(call: CallbackQuery, callback_data: k.Menu_callback, state: FSMContext):
    
    await call.message.delete()

    user_id = call.from_user.id

    whitelist_status = await w.is_in_whitelist(user_id=user_id)
    if not whitelist_status:
        return
    
    response = await u.is_admin(user_id=user_id)
    if not response:
        return
    
    text = '<b>Список юзеров:</b>'
    photo = FSInputFile(f'photos/{photo_users}')
    users_list = await u.get_users_by_role(requester_id=user_id)
    kb = k.users_kb(users_list)

    await call.message.answer_photo(photo=photo, caption=text, reply_markup=kb)




@router.callback_query(k.Menu_callback.filter(F.menu == 'user'))
async def get_orders(call: CallbackQuery, callback_data: k.Menu_callback, state: FSMContext):
    
    await call.message.delete()

    user_id = call.from_user.id

    whitelist_status = await w.is_in_whitelist(user_id=user_id)
    if not whitelist_status:
        return
    
    response = await u.is_admin(user_id=user_id)
    if not response:
        return


    user_info_id = int(callback_data.data)
    stats = await u.get_user_statistics(user_id=user_info_id)

    warns = stats['warnings']
    if stats['warnings'] is None:
        warns = 0

    text = (
        f"<b>Статистика юзера <code>{stats['username']}</code> | <code>{user_info_id}</code>:</b>\n\n"
        f"<b>Дата присоединения:</b> <code>{stats['joined_at']}</code>\n"
        f"<b>Заработано денег:</b> <code>${stats['total_earnings']}</code>\n"
        f"<b>Выговоры:</b> <code>{warns}</code>\n\n"
        f"<b>Активные заказы:</b> <code>{stats['active_orders_count']}</code>\n"
        f"<b>Отклонённые заказы:</b> <code>{stats['rejected_orders_count']}</code>\n"
    )

    orders = await o.get_active_orders_for_user(user_id=user_info_id)
    
    if admin == user_id:
        admin_status = True
    else:
        admin_status = False

    kb = k.user_kb(orders=orders, user_id=user_info_id, admin_status=admin_status)
    photo = FSInputFile(f'photos/{photo_stats}')

    await call.message.answer_photo(photo=photo, caption=text, reply_markup=kb)





@router.callback_query(k.Menu_callback.filter(F.menu == 'admin_order'))
async def end_order(call: CallbackQuery, callback_data: k.Menu_callback, state: FSMContext):

    await call.message.delete()

    order_id = int(callback_data.data)
    order_data = await o.get_order_by_id(order_id=order_id)
    user_id = await o.get_user_by_order(order_id=order_id)

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
    kb = k.order_admin_kb(order_id=order_id, user_id=user_id)

    await call.message.answer(text=text, reply_markup=kb)




@router.callback_query(k.Menu_callback.filter(F.menu == 'comlete_order'))
async def end_order(call: CallbackQuery, callback_data: k.Menu_callback, state: FSMContext):

    await call.message.delete()

    order_id = int(callback_data.data)
    user_id = int(callback_data.data2)


    status = await o.complete_order(order_id=order_id)
    if status:
        text = f'<b>Заказ с айди <code>#{order_id}</code> успешно завершён!</b>'
    else:
        text = f'<b>Ошибка завершения заказа с айди <code>#{order_id}</code>!</b>'

    # Здесь photo переменная должна содержать имя файла фотографии, если она есть
    # photo = FSInputFile(f'photos/{orders_photo}')
    kb = k.cancel_menu_kb()
    await call.message.answer(text=text, reply_markup=kb)

    text = f'<b>⭐️ Заказ <code>#{order_id}</code> завершен. Спасибо за работу!</b>'
    await bot.send_message(chat_id=user_id, text=text)



@router.callback_query(k.Menu_callback.filter(F.menu == 'rejected_order'))
async def end_order(call: CallbackQuery, callback_data: k.Menu_callback, state: FSMContext):

    await call.message.delete()

    order_id = int(callback_data.data)
    user_id = int(callback_data.data2)


    status = await o.reject_order(order_id=order_id)
    if status:
        text = f'<b>Заказ с айди <code>#{order_id}</code> успешно удалён!</b>'
    else:
        text = f'<b>Ошибка удаления заказа с айди <code>#{order_id}</code>!</b>'

    # Здесь photo переменная должна содержать имя файла фотографии, если она есть
    # photo = FSInputFile(f'photos/{orders_photo}')
    kb = k.cancel_menu_kb()
    await call.message.answer(text=text, reply_markup=kb)

    text = f'<b>♻️ Заказ <code>#{order_id}</code> удалён.</b>'
    await bot.send_message(chat_id=user_id, text=text)





@router.callback_query(k.Menu_callback.filter(F.menu == 'add_warn'))
async def end_order(call: CallbackQuery, callback_data: k.Menu_callback, state: FSMContext):

    await call.message.delete()

    user_id = int(callback_data.data)

    status = await u.add_warning(user_id=user_id)
    # print(status)
    if status:
        text = f'Предупреждение {user_id} успешно выдано'
    else:
        text = f'Ошибка выдачи предупреждения {user_id}!'

    await call.answer(text=text)


    user_info_id = int(callback_data.data)
    stats = await u.get_user_statistics(user_id=user_info_id)

    warns = stats['warnings']
    if stats['warnings'] is None:
        warns = 0

    text = (
        f"<b>Статистика юзера <code>{stats['username']}</code> | <code>{user_info_id}</code>:</b>\n\n"
        f"<b>Дата присоединения:</b> <code>{stats['joined_at']}</code>\n"
        f"<b>Заработано денег:</b> <code>${stats['total_earnings']}</code>\n"
        f"<b>Выговоры:</b> <code>{warns}</code>\n\n"
        f"<b>Активные заказы:</b> <code>{stats['active_orders_count']}</code>\n"
        f"<b>Отклонённые заказы:</b> <code>{stats['rejected_orders_count']}</code>\n"
    )

    orders = await o.get_active_orders_for_user(user_id=user_info_id)
    
    id_from_user = call.from_user.id

    if admin == id_from_user:
        admin_status = True
    else:
        admin_status = False

    # print(text)
    kb = k.user_kb(orders=orders, user_id=user_info_id, admin_status=admin_status)
    photo = FSInputFile(f'photos/{photo_stats}')

    await call.message.answer_photo(photo=photo, caption=text, reply_markup=kb)


@router.callback_query(k.Menu_callback.filter(F.menu == 'remove_warn'))
async def end_order(call: CallbackQuery, callback_data: k.Menu_callback, state: FSMContext):

    await call.message.delete()

    user_id = int(callback_data.data)

    status = await u.remove_warning(user_id=user_id)
    if status:
        text = f'Предупреждение {user_id} успешно удалено!'
    else:
        text = f'Ошибка удаления предупреждения {user_id}!'

    await call.answer(text=text)


    user_id = int(callback_data.data)
    stats = await u.get_user_statistics(user_id=user_id)

    warns = stats['warnings']
    if stats['warnings'] is None:
        warns = 0

    text = (
        f"<b>Статистика юзера <code>{stats['username']}</code> | <code>{user_id}</code>:</b>\n\n"
        f"<b>Дата присоединения:</b> <code>{stats['joined_at']}</code>\n"
        f"<b>Заработано денег:</b> <code>${stats['total_earnings']}</code>\n"
        f"<b>Выговоры:</b> <code>{warns}</code>\n\n"
        f"<b>Активные заказы:</b> <code>{stats['active_orders_count']}</code>\n"
        f"<b>Отклонённые заказы:</b> <code>{stats['rejected_orders_count']}</code>\n"
    )

    orders = await o.get_active_orders_for_user(user_id=user_id)
    
    id_from_user = call.from_user.id

    if admin == id_from_user:
        admin_status = True
    else:
        admin_status = False

    kb = k.user_kb(orders=orders, user_id=user_id, admin_status=admin_status)

    photo = FSInputFile(f'photos/{photo_stats}')
    await call.message.answer_photo(photo=photo, caption=text, reply_markup=kb)