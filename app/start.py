import os
from dotenv import load_dotenv

from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext

from keyboards import client as k
from app.form_app.fsm import Form

from data import users as u
from data import whitelist as w
from app.form_app.data import requests as r

from config import bot



load_dotenv()
start_photo = os.getenv("start_photo")
photo_menu = os.getenv("photo_menu")



router = Router()





@router.message(CommandStart())
async def start(message: Message, state: FSMContext):

    if state:
        await state.clear()

    await state.get_data()

    user_id = message.from_user.id
    whitelist_status = await w.is_in_whitelist(user_id=user_id)
    if not whitelist_status:
        return

    user = await u.get_user_info(user_id=user_id)

    if user == None:

        user_request = await r.get_request(user_id=user_id)
        if user_request:

            text = '<b>Вы уже отправили заявку.</b>'
            await message.answer(text=text)

            return

        kb = k.start_kb()
        photo = FSInputFile(f'photos/{start_photo}')
        text = '''
👋 Привет! Это бот для участников студии Blume. 

⚙️ Здесь будет происходить всё взаимодействие внутри нашей команды. Вы сможете просматривать свой профиль, заказы, а также ознакомиться с правилами. В боте будет много полезной информации и новостей о том, что происходит в студии.

🧡 Приятного использования!
'''
        await message.answer_photo(photo=photo, caption=text, reply_markup=kb)
        await state.set_state(Form.nickname)
        return
    


    response = await u.is_admin(user_id=user_id)
    if response:
        kb = k.menu_kb(Admin_status=True)
    else:
        kb = k.menu_kb(Admin_status=False)

    text = '''
<b>✨ Добро пожаловать в главное меню!</b>

Приятно видеть вас здесь! Мы готовы помочь вам с любым запросом — просто выберите действие из списка ниже. Будь то заказы, получение информации или просмотр статистики — мы всё предусмотрели! 

Всё, что вам нужно, находится на расстоянии одного клика. Давайте начнем! 👇'''

    photo = FSInputFile(f'photos/{photo_menu}')

    await message.answer_photo(photo=photo, caption=text, reply_markup=kb)
    

    



@router.callback_query(k.Menu_callback.filter(F.menu == 'menu'))
async def menu(call: CallbackQuery, callback_data: k.Menu_callback, state: FSMContext):

    if state:
        await state.clear()

    await call.message.delete()

    await state.get_data()

    user_id = call.from_user.id
    whitelist_status = await w.is_in_whitelist(user_id=user_id)
    if not whitelist_status:
        return

    user = await u.get_user_info(user_id=user_id)

    
    if user == None:

        user_request = await r.get_request(user_id=user_id)
        if user_request:

            photo = FSInputFile(f'photos/{start_photo}')
            text = '<b>Вы уже отправили заявку.</b>'
            await call.message.answer(text=text)

            return

        kb = k.start_kb()
        text = '''
👋 Привет! Это бот для участников студии Blume. 

⚙️ Здесь будет происходить всё взаимодействие внутри нашей команды. Вы сможете просматривать свой профиль, заказы, а также ознакомиться с правилами. В боте будет много полезной информации и новостей о том, что происходит в студии.

🧡 Приятного использования!
'''
        await call.message.answer_photo(photo=photo, caption=text, reply_markup=kb)
        await state.set_state(Form.nickname)
        return
    

    response = await u.is_admin(user_id=user_id)
    if response:
        kb = k.menu_kb(Admin_status=True)
    else:
        kb = k.menu_kb(Admin_status=False)

    text = '''
<b>✨ Добро пожаловать в главное меню!</b>

Приятно видеть вас здесь! Мы готовы помочь вам с любым запросом — просто выберите действие из списка ниже. Будь то заказы, получение информации или просмотр статистики — мы всё предусмотрели! 

Всё, что вам нужно, находится на расстоянии одного клика. Давайте начнем! 👇'''

    photo = FSInputFile(f'photos/{photo_menu}')
    await call.message.answer_photo(photo=photo, caption=text, reply_markup=kb)
