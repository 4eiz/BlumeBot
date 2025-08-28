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


router = Router()


load_dotenv()
orders_photo = os.getenv("photo_orders")




@router.callback_query(k.Menu_callback.filter(F.menu == 'FAQ'))
async def profile(call: CallbackQuery, callback_data: k.Menu_callback, state: FSMContext):
    
    await call.message.delete()

    user_id = call.from_user.id

    whitelist_status = await w.is_in_whitelist(user_id=user_id)
    if not whitelist_status:
        return

    kb = k.cancel_profile_kb()

    # Формируем текст с HTML-форматированием
    text = '''
Первый выговор: Это обычное замечание или предупреждение сотруднику. Оно не влечет за собой никаких системных или материальных последствий.

Второй выговор: Это серьезное предупреждение, которое влияет на работу в студии. При наличии второго выговора система будет распределять заказы в пользу сотрудников без выговоров, даже если у вас одинаковые стеки. Вы получите заказ только в том случае, если сотрудник без выговора откажется от него или не будет заинтересован.

Третий выговор: Включает все последствия второго выговора, а также дополнительные меры: снижение оплаты на 10% и невозможность брать крупные заказы.
'''

    # Загружаем фото профиля
    photo = FSInputFile(f'photos/{orders_photo}')

    # Отправляем фото и текст с HTML-форматированием
    await call.message.answer_photo(photo=photo, caption=text, reply_markup=kb)
