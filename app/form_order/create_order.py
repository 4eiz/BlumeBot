import os
import json
from dotenv import load_dotenv

from typing import Optional

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext

from app.fsm import OrderForm
from keyboards import client as k
from config import bot

from data import orders as o
from data import users as u
from data import whitelist as w



router = Router()


# Этот файл отвечает за функцию создания заказа
# 
# Без надобности не трогать!
#
# В самом низу файла описаны действия для кнопок назад в каждом пункте
# Может быть много костылей, но пока что иначе не придумал



# Импорты названий фотографий + айди админа

load_dotenv()
admin = os.getenv("admin")
photo_specialization = os.getenv("photo_specialization")
photo_stack = os.getenv("photo_stack2")
photo_size = os.getenv("photo_size")
photo_short_description = os.getenv("photo_short_description")
photo_full_description = os.getenv("photo_full_description")
photo_deadlines = os.getenv("photo_deadlines")
photo_price = os.getenv("photo_price")
photo_conf = os.getenv("photo_confirmation")
photo_order = os.getenv("photo_order")









# ----------------------------------------------



# Функция для перевода ролей и размеров
def translate_role(role):
    translations = {
        'designer': 'Дизайнер',
        'developer': 'Разработчик'
    }
    return translations.get(role, role)



def translate_sizes(size):
    translations = {
        'large': 'Большой',
        'small': 'Малый',
        'medium': 'Средний'
    }
    # Применяем перевод к каждому элементу списка и возвращаем обновленный список
    return translations.get(size, size)



# ----------------------------------------



# Шаг 1: Выбор специализации
@router.callback_query(k.Menu_callback.filter(F.menu == 'new_order'))
async def start_order(call: CallbackQuery, state: FSMContext):

    user_id = call.from_user.id

    whitelist_status = await w.is_in_whitelist(user_id=user_id)
    if not whitelist_status:
        return

    admin_status = await u.is_admin(user_id=user_id)
    if admin_status is None:
        return

    await call.message.delete()

    text = "Выберите специализацию для заказа:"
    kb = k.role_order_kb()
    photo = FSInputFile(f'photos/{photo_specialization}')

    await call.message.answer_photo(photo=photo, caption=text, reply_markup=kb)

    await state.set_state(OrderForm.specialization)


# Шаг 2: Выбор стека технологий
@router.callback_query(k.Menu_callback.filter(F.menu == 'role'), OrderForm.specialization)
async def select_role(call: CallbackQuery, callback_data: k.Menu_callback, state: FSMContext):

    await call.message.delete()

    role = callback_data.data
    await state.update_data(role=role)
    
    if role == 'developer':
        text = 'Выберите стек технологий для заказа:'
        kb = k.stack_kb()
    elif role == 'designer':
        text = 'Выберите навыки для заказа:'
        kb = k.stack_kb_designer()

    photo = FSInputFile(f'photos/{photo_stack}')

    await call.message.answer_photo(photo=photo, caption=text, reply_markup=kb)

    await state.set_state(OrderForm.stack)


# Обработчик выбора технологии
@router.callback_query(k.Menu_callback.filter(F.menu == 'tech'), OrderForm.stack)
async def select_technology(call: CallbackQuery, callback_data: k.Menu_callback, state: FSMContext):

    selected_tech = callback_data.data
    data = await state.get_data()
    selected_technologies = data.get("selected_technologies", [])
    role = data.get("role")

    if selected_tech in selected_technologies:
        selected_technologies.remove(selected_tech)
    else:
        selected_technologies.append(selected_tech)

    await state.update_data(selected_technologies=selected_technologies)

    if role == 'developer':
        kb = k.stack_kb(selected_technologies)
    elif role == 'designer':
        kb = k.stack_kb_designer(selected_technologies)
    else:
        kb = None

    if kb:
        await call.message.edit_reply_markup(reply_markup=kb)


# Обработчик кнопки "Продолжить"
@router.callback_query(k.Menu_callback.filter(F.menu == 'next'), OrderForm.stack)
async def continue_selection(call: CallbackQuery, state: FSMContext):

    # await call.message.delete()

    data = await state.get_data()
    st = data.get('selected_technologies', None)

    if not st:
        text = "Выберите хотя бы одну технологию для продолжения!"
        await call.answer(text=text, show_alert=True)
        return
    
    text = 'Выберите размер заказа:'
    kb = k.order_size_kb()
    photo = FSInputFile(f'photos/{photo_size}')

    await call.message.answer_photo(photo=photo, caption=text, reply_markup=kb)

    await state.set_state(OrderForm.size)



@router.callback_query(k.Menu_callback.filter(F.menu == 'order_size'), OrderForm.size)
async def handle_order_size(call: CallbackQuery, callback_data: k.Menu_callback, state: FSMContext):

    selected_size = callback_data.data

    await state.update_data(selected_sizes=selected_size)

    await call.message.delete()

    kb = k.cancel_kb()
    text = 'Введите краткое описание заказа:'
    photo = FSInputFile(f'photos/{photo_short_description}')

    await call.message.answer_photo(photo=photo, caption=text, reply_markup=kb)

    await state.set_state(OrderForm.short_description)



# # Обработчик кнопки "Продолжить"
# @router.callback_query(k.Menu_callback.filter(F.menu == 'next'), OrderForm.size)
# async def continue_selection(call: CallbackQuery, state: FSMContext):

#     data = await state.get_data()
#     selected_sizes = data.get('selected_sizes', None)

#     if not selected_sizes:
#         text = 'Выберите хотя бы один размер для продолжения!'
#         await call.answer(text=text, show_alert=True)
#         return
    
#     await call.message.delete()

#     kb = k.cancel_kb()
#     text = 'Введите краткое описание заказа:'
#     photo = FSInputFile(f'photos/{photo_short_description}')

#     await call.message.answer_photo(photo=photo, caption=text, reply_markup=kb)

#     await state.set_state(OrderForm.short_description)



@router.message(OrderForm.short_description)
async def receive_short_description(message: Message, state: FSMContext):

    await state.update_data(short_description=message.text)

    message_id = message.message_id
    chat_id = message.from_user.id

    await bot.delete_message(chat_id=chat_id, message_id=message_id)
    await bot.delete_message(chat_id=chat_id, message_id=message_id-1)

    text = "Введите полное описание заказа:"
    kb = k.cancel_kb()
    photo = FSInputFile(f'photos/{photo_full_description}')

    await message.answer_photo(photo=photo, caption=text, reply_markup=kb)

    await state.set_state(OrderForm.full_description)



@router.message(OrderForm.full_description)
async def receive_full_description(message: Message, state: FSMContext):

    full_description = message.text

    # Проверка на длину описания
    if len(full_description) > 1000:
        await message.reply("<b>⚠️ Описание слишком длинное. Пожалуйста, сократите описание до 1000 символов.</b>")
        return

    await state.update_data(full_description=full_description)

    message_id = message.message_id
    chat_id = message.from_user.id

    await bot.delete_message(chat_id=chat_id, message_id=message_id)
    await bot.delete_message(chat_id=chat_id, message_id=message_id - 1)

    kb = k.deadline_kb()
    text = "Укажите сроки выполнения заказа или нажмите 'Не указано'."
    photo = FSInputFile(f'photos/{photo_deadlines}')

    await message.answer_photo(photo=photo, caption=text, reply_markup=kb)

    await state.set_state(OrderForm.deadlines)




# Шаг 5: Выбор сроков
@router.message(OrderForm.deadlines)
async def set_deadline1(message: Message, state: FSMContext):

    deadline = message.text
    try:
        deadline = int(deadline)
    except:
        text = '<b>⚠️ Цена должна быть указана числом!</b>'
        await message.reply(text=text)
        return

    await state.update_data(deadline=deadline)

    message_id = message.message_id
    chat_id = message.from_user.id

    await bot.delete_message(chat_id=chat_id, message_id=message_id)
    await bot.delete_message(chat_id=chat_id, message_id=message_id-1)

    kb = k.price_kb()
    text = "Укажите стоимость заказа или нажмите 'Не указано'."
    photo = FSInputFile(f'photos/{photo_price}')

    await message.answer_photo(photo=photo, caption=text, reply_markup=kb)

    await state.set_state(OrderForm.price)


@router.callback_query(k.Menu_callback.filter(F.menu == 'no'), OrderForm.deadlines)
async def set_deadline(call: CallbackQuery, callback_data: k.Menu_callback, state: FSMContext):

    await call.message.delete()

    deadline = callback_data.data
    await state.update_data(deadline=deadline)

    kb = k.price_kb()
    text = "Укажите стоимость заказа или нажмите 'Не указано'."
    photo = FSInputFile(f'photos/{photo_price}')

    await call.message.answer_photo(photo=photo, caption=text, reply_markup=kb)

    await state.set_state(OrderForm.price)




# Шаг 6: Выбор цены
@router.message(OrderForm.price)
async def set_deadline(message: Message, state: FSMContext):

    price = message.text
    try:
        price = float(price)
    except:
        text = '<b>⚠️ Цена должна быть указана числом!</b>'
        await message.reply(text=text)
        return

    await state.update_data(price=price)

    message_id = message.message_id
    chat_id = message.from_user.id

    await bot.delete_message(chat_id=chat_id, message_id=message_id)
    await bot.delete_message(chat_id=chat_id, message_id=message_id-1)

    data = await state.get_data()

    role = data.get("role")
    role_tr = translate_role(role=role)

    stack = ', '.join(data.get("selected_technologies", []))

    size = data.get('selected_sizes')
    size = translate_sizes(size=size)

    short_desc = data.get("short_description")
    full_desc = data.get("full_description")
    deadline = data.get("deadline", "Не указано")
    if deadline is None:
        deadline = '-'
    price = data.get("price", "Не указано")
    if price is None:
        price = '-'

    # Предпросмотр заказа
    text = f"""<b>Предпросмотр заказа:</b>

Специализация: <code>{role_tr}</code>
Стек: <code>{stack}</code>
Размер: <code>{size}</code>
Краткое описание: <code>{short_desc}</code>
Полное описание: <code>{full_desc}</code>
Сроки: <code>{deadline}</code>
Цена: <code>{price}</code>
"""

    kb = k.confirm_order_kb()
    photo = FSInputFile(f'photos/{photo_conf}')

    await message.answer_photo(photo=photo, caption=text, reply_markup=kb)

    await state.set_state(OrderForm.confirmation)


# Шаг 6: Выбор цены
@router.callback_query(k.Menu_callback.filter(F.menu == 'no'), OrderForm.price)
async def set_deadline(call: CallbackQuery, callback_data: k.Menu_callback, state: FSMContext):

    await call.message.delete()

    price = callback_data.data
    await state.update_data(price=price)

    data = await state.get_data()

    role = data.get("role")
    role_tr = translate_role(role=role)

    stack = ', '.join(data.get("selected_technologies", []))

    size = data.get('selected_sizes')
    size_tr = translate_sizes(size=size)

    short_desc = data.get("short_description")
    full_desc = data.get("full_description")
    deadline = data.get("deadline", "Не указано")
    if deadline is None:
        deadline = '-'
    price = data.get("price", "Не указано")
    if price is None:
        price = '-'

    # Предпросмотр заказа
    text = f"""<b>Предпросмотр заказа:</b>

Специализация: <code>{role_tr}</code>
Стек: <code>{stack}</code>
Размер: <code>{size_tr}</code>
Краткое описание: <code>{short_desc}</code>
Полное описание: <code>{full_desc}</code>
Сроки: <code>{deadline}</code>
Цена: <code>{price}</code>
"""

    kb = k.confirm_order_kb()
    photo = FSInputFile(f'photos/{photo_conf}')

    await call.message.answer_photo(photo=photo, caption=text, reply_markup=kb)

    await state.set_state(OrderForm.confirmation)




# Шаг 7: Подтверждение заказа (пока выводим в консоль)
@router.callback_query(k.Menu_callback.filter(F.menu == 'confirm_order'), OrderForm.confirmation)
async def confirm_order(call: CallbackQuery, state: FSMContext):
    await call.message.delete()

    # Получаем данные из состояния
    data = await state.get_data()
    # print(f"Заказ: {data}")

    # Расшифровка данных
    role = data.get('role')
    title = data.get('short_description', '')
    description = data.get('full_description', '')
    required_skills = ','.join(data.get('selected_technologies', []))  # Преобразуем список в строку
    size = data.get('selected_sizes')  # Преобразуем список в строку

    price = data.get('price')  # Преобразуем цену в число с плавающей точкой
    if price != None:
        price = float(price)

    deadline = data.get('deadline')  # Преобразуем дедлайн в целое число
    if deadline != None:
        deadline = int(deadline)

    admin_id = call.from_user.id

    # Добавляем заказ в базу данных
    order = await o.add_order_to_db(
        title=title,
        description=description,
        required_skills=required_skills,
        size=size,
        specialty=role,
        created_by=admin_id,
        price=price,
        deadline=deadline
    )



    text = '<b>Заказ создан!</b>'
    await call.message.answer(text=text)

    users = await o.get_users_for_order(technologies=required_skills, order_size=size, role=role)
    for user in users:

        text = f"<b>⚡️ Заказ</b> <code>#{order}</code>\n\n" \
                f"<b>Краткое описание:</b> {title}\n\n" \
                f"<b>Большое описание:</b> {description}\n\n" \
                f"<b>💸 Сумма:</b> <code>{'-' if price is None else f'${price}'}</code>\n" \
                f"<b>📆 Сроки:</b> <code>{'-' if deadline is None else deadline}</code>"
        
        kb = k.order_kb(admin_id=admin_id, order_id=order)
        photo = FSInputFile(f'photos/{photo_order}')

        await bot.send_photo(chat_id=user, photo=photo, caption=text, reply_markup=kb)

    await state.clear()




# --------------------------------



# Обработчик кнопки "Назад" для выбора специализации
@router.callback_query(k.Menu_callback.filter(F.menu == 'cancel'), OrderForm.stack)
async def back_to_specialization(call: CallbackQuery, state: FSMContext):

    await call.message.delete()
    await state.update_data(selected_technologies=[])

    text = "Выберите специализацию для заказа:"
    kb = k.role_order_kb()
    photo = FSInputFile(f'photos/{photo_specialization}')

    await call.message.answer_photo(photo=photo, caption=text, reply_markup=kb)

    await state.set_state(OrderForm.specialization)



# Обработчик кнопки "Назад" для выбора стека технологий
@router.callback_query(k.Menu_callback.filter(F.menu == 'cancel'), OrderForm.size)
async def back_to_stack(call: CallbackQuery, state: FSMContext):

    await call.message.delete()

    await state.update_data(selected_technologies=[])
    data = await state.get_data()
    role = data.get('role')
    
    if role == 'developer':
        kb = k.stack_kb()
    elif role == 'designer':
        kb = k.stack_kb_designer()
    else:
        kb = None

    text = 'Выберите стек технологий для заказа:'
    photo = FSInputFile(f'photos/{photo_specialization}')

    await call.message.answer_photo(photo=photo, caption=text, reply_markup=kb)

    await state.set_state(OrderForm.stack)



# Обработчик кнопки "Назад" для выбора размера заказа
@router.callback_query(k.Menu_callback.filter(F.menu == 'cancel'), OrderForm.short_description)
async def back_to_size(call: CallbackQuery, state: FSMContext):

    await call.message.delete()

    await state.update_data(selected_sizes=[])

    text = 'Выберите размер заказа:'
    kb = k.order_size_kb()
    photo = FSInputFile(f'photos/{photo_size}')

    await call.message.answer_photo(photo=photo, caption=text, reply_markup=kb)

    await state.set_state(OrderForm.size)



# Обработчик кнопки "Назад" для ввода краткого описания
@router.callback_query(k.Menu_callback.filter(F.menu == 'cancel'), OrderForm.full_description)
async def back_to_short_description(call: CallbackQuery, state: FSMContext):

    await call.message.delete()

    text = 'Введите краткое описание заказа:'
    kb = k.cancel_kb()
    photo = FSInputFile(f'photos/{photo_short_description}')

    await call.message.answer_photo(photo=photo, caption=text, reply_markup=kb)

    await state.set_state(OrderForm.short_description)



# Обработчик кнопки "Назад" для ввода полного описания
@router.callback_query(k.Menu_callback.filter(F.menu == 'cancel'), OrderForm.deadlines)
async def back_to_full_description(call: CallbackQuery, state: FSMContext):

    await call.message.delete()

    text = 'Введите полное описание заказа:'
    kb = k.cancel_kb()
    photo = FSInputFile(f'photos/{photo_full_description}')

    await call.message.answer_photo(photo=photo, caption=text, reply_markup=kb)

    await state.set_state(OrderForm.full_description)



# Обработчик кнопки "Назад" для выбора сроков
@router.callback_query(k.Menu_callback.filter(F.menu == 'cancel'), OrderForm.price)
async def back_to_deadlines(call: CallbackQuery, state: FSMContext):

    await call.message.delete()

    text = "Укажите сроки выполнения заказа или нажмите «Не указано»."
    kb = k.deadline_kb()
    photo = FSInputFile(f'photos/{photo_deadlines}')

    await call.message.answer_photo(photo=photo, caption=text, reply_markup=kb)

    await state.set_state(OrderForm.deadlines)



# Обработчик кнопки "Назад" для выбора цены
@router.callback_query(k.Menu_callback.filter(F.menu == 'cancel'), OrderForm.confirmation)
async def back_to_price(call: CallbackQuery, state: FSMContext):

    await call.message.delete()

    text = "Укажите стоимость заказа или нажмите «Не указано»."
    kb = k.price_kb()
    photo = FSInputFile(f'photos/{photo_price}')

    await call.message.answer_photo(photo=photo, caption=text, reply_markup=kb)

    await state.set_state(OrderForm.price)