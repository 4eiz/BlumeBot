from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext



# Создания заказа
class OrderForm(StatesGroup):
    specialization = State()  # Выбор специализации
    stack = State()  # Выбор стека
    size = State()  # Выбор размера
    short_description = State()  # Краткое описание заказа
    full_description = State()  # Полное описание заказа
    deadlines = State()  # Указание сроков
    price = State()  # Указание цены
    confirmation = State()  # Подтверждение отправки заказа


# Отправка сообщений
class Send_message(StatesGroup):
    text = State()

class Price(StatesGroup):
    price = State()


# Добавление в вайтлист
class Whitelist(StatesGroup):
    add_user = State()
    ban_user = State()
    conf = State()


# Отказ от заказа
class Decline_order(StatesGroup):
    reason = State()
    conf = State()


# Рассылка
class Newsletters(StatesGroup):
    text = State()
