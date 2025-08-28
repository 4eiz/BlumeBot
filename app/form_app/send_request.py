import os
import json
import re

from dotenv import load_dotenv

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext

from app.form_app.fsm import Form
from app.form_app import keyboards as k
from keyboards import client as kc
from app.form_app.data import requests as r

from config import bot

router = Router()


# Этот файл отвечает за функцию отправки заявки для использования бота
#
# Без надобности не трогать!
#
# В самом низу файла описаны действия для кнопкок назад в каждом пункте
# Может быть много костылей, но пока что иначе не придумал



# Импорты названий фотографий + айди админа

load_dotenv()
admin = os.getenv("admin")
photo_nickname = os.getenv("photo_nickname")
photo_rules = os.getenv("photo_rules")
photo_role = os.getenv("photo_role")
photo_stack = os.getenv("photo_stack1")
photo_preferences = os.getenv("photo_preferences")
photo_portfolie = os.getenv("photo_portfolie")
photo_conf = os.getenv("photo_conf")





# ----------------------------------------------



# Функция для перевода ролей и размеров
def translate_role(role):
    translations = {
        'designer': 'Дизайнер',
        'developer': 'Разработчик',
        'manager': 'Менеджер'
    }
    return translations.get(role, role)



def translate_sizes(sizes):
    translations = {
        'large': 'Большие',
        'small': 'Малые',
        'medium': 'Средние'
    }
    # Применяем перевод к каждому элементу списка и возвращаем обновленный список
    return [translations.get(size, size) for size in sizes]



# ----------------------------------------



# Обработчик нажатия на кнопку "Продолжить"
@router.callback_query(kc.Menu_callback.filter(F.menu == 'start'))
async def set_name(call: CallbackQuery, callback_data: k.Menu_callback, state: FSMContext):

    await call.message.delete()

    text = 'Пожалуйста, введите Ваш никнейм (только английские буквы, отсутствие цифр): '
    photo = FSInputFile(f'photos/{photo_nickname}')

    await call.message.answer_photo(photo=photo, caption=text)
    await state.set_state(Form.nickname)



@router.callback_query(k.Menu_callback.filter(F.menu == 'change'), Form.conf)
async def accept_rules_handler(call: CallbackQuery, callback_data: k.Menu_callback, state: FSMContext):

    message_id = call.message.message_id
    chat_id = call.from_user.id

    await bot.delete_message(chat_id=chat_id, message_id=message_id)
    
    text = 'Пожалуйста, введите Ваш никнейм (только английские буквы, отсутствие цифр): '
    photo = FSInputFile(f'photos/{photo_nickname}')

    await call.message.answer_photo(photo=photo, caption=text)
    await state.set_state(Form.nickname)



# Функция для обработки ввода после ника
@router.message(Form.nickname)
async def rules_state(message: Message, state: FSMContext):
    chat_id = message.from_user.id
    message_id = message.message_id

    # Проверка, что никнейм содержит только английские буквы
    nickname = message.text
    if not re.match("^[A-Za-z]+$", nickname):
        error_text = "<b>❌ Никнейм должен содержать только английские буквы без цифр и символов. Пожалуйста, введите ник заново.</b>"
        await message.reply(error_text)
        return  # Прерываем выполнение функции, чтобы пользователь ввел никнейм заново

    # Если никнейм валиден, продолжаем обработку
    await bot.delete_message(chat_id=chat_id, message_id=message_id)
    await bot.delete_message(chat_id=chat_id, message_id=message_id-1)

    await state.update_data(name=nickname)

    text = """
<b>🛡 Прежде чем начать работу в студии, убедитесь, что вы полностью ознакомлены с правилами и согласны с ними.</b>
"""
    kb = k.rules_kb()
    photo = FSInputFile(f'photos/{photo_rules}')

    await message.answer_photo(photo=photo, caption=text, reply_markup=kb)

    await state.set_state(Form.rules)



# Обработчик нажатия на кнопку "Принять правила"
@router.callback_query(k.Menu_callback.filter(F.menu == 'accept_rules'))
async def accept_rules_callback(call: CallbackQuery, state: FSMContext):

    await call.message.delete()
    
    text = "Выберите Вашу специализацию:"
    kb = k.role_kb()
    photo = FSInputFile(f'photos/{photo_role}')

    await call.message.answer_photo(photo=photo, caption=text, reply_markup=kb)

    await state.set_state(Form.role)



# # Обработчик нажатия на кнопку "Продолжить"
# @router.callback_query(k.Menu_callback.filter(F.menu == 'next'), Form.rules)
# async def continue_callback(call: CallbackQuery, state: FSMContext):

#     data = await state.get_data()
#     accepted = data.get('accepted', None)

#     await call.message.delete()


#     if not accepted:
#         accepted = data['accepted']
#         text = "Сначала прочитайте правила!"
#         await call.answer(text=text, show_alert=True)
#         return
    
#     text = "Выберите Вашу специализацию:"
#     kb = k.role_kb()
#     photo = FSInputFile(f'photos/{photo_role}')

#     await call.message.answer_photo(photo=photo, caption=text, reply_markup=kb)

#     await state.set_state(Form.role)



# Обработчик выбора роли
@router.callback_query(k.Menu_callback.filter(F.menu == 'role'), Form.role)
async def set_role(call: CallbackQuery, callback_data: k.Menu_callback, state: FSMContext):

    await call.message.delete()

    role = callback_data.data
    await state.update_data(role=role)
    
    if role == 'developer':
        text = 'Пожалуйста, выберите Ваш стек:'
        kb = k.stack_kb()
        await state.set_state(Form.stack)

    elif role == 'designer':
        text = 'Пожалуйста, выберите Ваш стек:'
        kb = k.stack_kb_designer()
        await state.set_state(Form.stack)

    elif role == 'manager':
        text = 'Выберите размер заказа:'
        kb = k.order_size_kb()
        photo = photo_preferences
        await state.set_state(Form.preferences)

    photo = FSInputFile(f'photos/{photo_stack}')

    await call.message.answer_photo(photo=photo, caption=text, reply_markup=kb)



# Обработчик выбора технологии
@router.callback_query(k.Menu_callback.filter(F.menu == 'tech'), Form.stack)
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
@router.callback_query(k.Menu_callback.filter(F.menu == 'next'), Form.stack)
async def continue_selection(call: CallbackQuery, state: FSMContext):

    # await call.message.delete()

    data = await state.get_data()
    st = data.get('selected_technologies', None)

    if not st:
        text = "Выберите хотя бы одну технологию для продолжения!"
        await call.answer(text=text, show_alert=True)
        return
    
    await call.message.delete()

    text = 'Выберите предпочтительные заказы:'
    kb = k.order_size_kb()
    photo = FSInputFile(f'photos/{photo_preferences}')

    await call.message.answer_photo(photo=photo, caption=text, reply_markup=kb)

    await state.set_state(Form.preferences)



@router.callback_query(k.Menu_callback.filter(F.menu == 'order_size'), Form.preferences)
async def handle_order_size(call: CallbackQuery, callback_data: k.Menu_callback, state: FSMContext):

    selected_size = callback_data.data
    data = await state.get_data()
    selected_sizes = data.get('selected_sizes', [])

    if selected_size in selected_sizes:
        selected_sizes.remove(selected_size)
    else:
        selected_sizes.append(selected_size)

    await state.update_data(selected_sizes=selected_sizes)


    kb = k.order_size_kb(selected_sizes)
    await call.message.edit_reply_markup(reply_markup=kb)



# Обработчик кнопки "Продолжить"
@router.callback_query(k.Menu_callback.filter(F.menu == 'next'), Form.preferences)
async def continue_selection(call: CallbackQuery, state: FSMContext):


    data = await state.get_data()
    selected_sizes = data.get('selected_sizes', None)
    role = data.get('role')

    if not selected_sizes:
        text = 'Выберите хотя бы один размер для продолжения!'
        await call.answer(text=text, show_alert=True)
        return
    
    await call.message.delete()

    kb = k.cancel_kb()

    # print(role)
    if role in ('developer', 'manager'):

        # await call.message.delete()

        form_data = await state.get_data()
        name = form_data.get('name')
        role_tr = translate_role(role=role)
        
        # Преобразуем стек и размеры проектов в строки
        stack = form_data.get('selected_technologies', [])
        stack_list = ', '.join(stack)

        sizes = form_data.get('selected_sizes', [])
        sizes_list = translate_sizes(sizes=sizes)
        sizes_list = ', '.join(sizes_list)


        text = f'''<b>
Ваша анкета:

Имя: <code>{name}</code>
Специализация: <code>{role_tr}</code>
Стек: <code>{stack_list}</code>
Размеры проектов: <code>{sizes_list}</code></b>
'''

        kb = k.conf_kb()
        photo = FSInputFile(f'photos/{photo_conf}')

        await call.message.answer_photo(photo=photo, caption=text, reply_markup=kb)

        await state.set_state(Form.conf)

    else:

        text = 'Укажите ссылку на ваше портфолио.'
        photo = FSInputFile(f'photos/{photo_portfolie}')
        kb = k.port_kb()

        await call.message.answer_photo(photo=photo, caption=text, reply_markup=kb)

        await state.set_state(Form.portfolie)



# Функция для обработки портфолио
@router.message(Form.portfolie)
async def set_portfolio(message: Message, state: FSMContext):
    chat_id = message.from_user.id
    message_id = message.message_id

    await bot.delete_message(chat_id=chat_id, message_id=message_id)
    await bot.delete_message(chat_id=chat_id, message_id=message_id - 1)

    form_data = await state.get_data()
    name = form_data.get('name')
    role = form_data.get('role')
    role_tr = translate_role(role=role)
    
    # Преобразуем стек и размеры проектов в строки
    stack = form_data.get('selected_technologies', [])
    stack_list = ', '.join(stack)

    sizes = form_data.get('selected_sizes', [])
    sizes_list = translate_sizes(sizes=sizes)
    sizes_list = ', '.join(sizes_list)

    await state.update_data(portfolio=message.text)  # Сохраняем портфолио

    # Отправляем сообщение с анкетой и клавиатурой
    text = f'''<b>
Ваша анкета:

Имя: <code>{name}</code>
Специализация: <code>{role_tr}</code>
Стек: <code>{stack_list}</code>
Размеры проектов: <code>{sizes_list}</code>
Портфолио: <code>{message.text}</code></b>
'''

    kb = k.conf_kb()
    photo = FSInputFile(f'photos/{photo_conf}')

    await message.answer_photo(photo=photo, caption=text, reply_markup=kb)

    await state.set_state(Form.conf)



@router.callback_query(k.Menu_callback.filter(F.menu == 'no'), Form.portfolie)
async def set_deadline(call: CallbackQuery, callback_data: k.Menu_callback, state: FSMContext):

    await call.message.delete()

    form_data = await state.get_data()
    name = form_data.get('name')
    role = form_data.get('role')
    role_tr = translate_role(role=role)
    
    # Преобразуем стек и размеры проектов в строки
    stack = form_data.get('selected_technologies', [])
    stack_list = ', '.join(stack)

    sizes = form_data.get('selected_sizes', [])
    sizes_list = translate_sizes(sizes=sizes)
    sizes_list = ', '.join(sizes_list)

    await state.update_data(portfolio='-')  # Сохраняем портфолио

    # Отправляем сообщение с анкетой и клавиатурой
    text = f'''<b>
Ваша анкета:

Имя: <code>{name}</code>
Специализация: <code>{role_tr}</code>
Стек: <code>{stack_list}</code>
Размеры проектов: <code>{sizes_list}</code>
Портфолио: <code>-</code></b>
'''

    kb = k.conf_kb()
    photo = FSInputFile(f'photos/{photo_conf}')

    await call.message.answer_photo(photo=photo, caption=text, reply_markup=kb)

    await state.set_state(Form.conf)





@router.callback_query(k.Menu_callback.filter(F.menu == 'confirmation'), Form.conf)
async def confirm_request(call: CallbackQuery, callback_data: k.Menu_callback, state: FSMContext):
    
    await call.message.delete()

    form_data = await state.get_data()
    name = form_data.get('name')
    role = form_data.get('role')
    role_tr = translate_role(role=role)
    portfolio = form_data.get('portfolio', None)

    # Преобразуем стек и размеры проектов в строки
    stack = form_data.get('selected_technologies', [])
    stack_list = ', '.join(stack)

    sizes = form_data.get('selected_sizes', [])
    sizes_list = translate_sizes(sizes=sizes)
    sizes_list = ', '.join(sizes_list)

    user_id = call.from_user.id
    username = call.from_user.username

    if username:
        username = f'@{username} | '
    else:
        username = ''


    text = f'''<b>
Анкета {username}<code>{user_id}</code>:

Имя: <code>{name}</code>
Специализация: <code>{role_tr}</code>
Стек: <code>{stack_list}</code>
Размеры проектов: <code>{sizes_list}</code></b>
'''
    if portfolio:
        portfolio = f'\n<b>Портфолио: {portfolio}</b>'
        text = text + portfolio
    else:
        pass

    data = {
        'user_id': user_id,
        'name': name,
        'specialty': role,
        'stack': stack,
        'preferred_orders': sizes
    }

    data['stack'] = ','.join(data['stack'])
    data['preferred_orders'] = ','.join(data['preferred_orders'])

    data_str = json.dumps(data)

    kb = k.admin_conf(user_id=user_id)
    await bot.send_message(chat_id=admin, text=text, reply_markup=kb)

    text = f'<b>Ваша заявка принята на рассмотрение</b>'
    await call.message.answer(text=text)

    await r.add_request(user_id=user_id, data=data_str)
    
    await state.clear()



# --------------------------------

# Добавляем обработчик кнопки "Отмена" в каждом состоянии

@router.callback_query(k.Menu_callback.filter(F.menu == 'cancel'), Form.rules)
async def cancel_nickname(call: CallbackQuery, state: FSMContext):

    await call.message.delete()

    text = "Пожалуйста, введите Ваш никнейм (только английские буквы, отсутствие цифр):"
    photo = FSInputFile(f'photos/{photo_nickname}')

    await call.message.answer_photo(photo=photo, caption=text)
    await state.set_state(Form.nickname)



@router.callback_query(k.Menu_callback.filter(F.menu == 'cancel'), Form.role)
async def cancel_rules(call: CallbackQuery, state: FSMContext):

    await call.message.delete()

    text = """
<b>🛡 Прежде чем начать работу в студии, убедитесь, что вы полностью ознакомлены с правилами и согласны с ними.</b>
"""
    kb = k.rules_kb()
    photo = FSInputFile(f'photos/{photo_rules}')

    await call.message.answer_photo(photo=photo, caption=text, reply_markup=kb)

    await state.set_state(Form.rules)



@router.callback_query(k.Menu_callback.filter(F.menu == 'cancel'), Form.stack)
async def cancel_stack(call: CallbackQuery, state: FSMContext):

    await call.message.delete()

    await state.update_data(selected_technologies=[])
    text = "Выберите Вашу специализацию:"

    kb = k.role_kb()
    photo = FSInputFile(f'photos/{photo_role}')

    await call.message.answer_photo(photo=photo, caption=text, reply_markup=kb)

    await state.set_state(Form.role)



@router.callback_query(k.Menu_callback.filter(F.menu == 'cancel'), Form.preferences)
async def cancel_stack(call: CallbackQuery, state: FSMContext):

    await call.message.delete()

    text = "Пожалуйста, выберите Ваш стек:"
    await state.update_data(selected_technologies=[])
    
    role = (await state.get_data()).get('role')

    if role == 'developer':
        kb = k.stack_kb()
    elif role == 'designer':
        kb = k.stack_kb_designer()

    photo = FSInputFile(f'photos/{photo_stack}')

    await call.message.answer_photo(photo=photo, caption=text, reply_markup=kb)

    await state.set_state(Form.stack)



@router.callback_query(k.Menu_callback.filter(F.menu == 'cancel'), Form.portfolie)
async def cancel_preferences(call: CallbackQuery, state: FSMContext):

    await call.message.delete()

    await state.update_data(selected_sizes=[])

    text = "Выберите предпочтительные заказы:"
    kb = k.order_size_kb()
    photo = FSInputFile(f'photos/{photo_preferences}')

    await call.message.answer_photo(photo=photo, caption=text, reply_markup=kb)

    await state.set_state(Form.preferences)