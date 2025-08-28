import os
from dotenv import load_dotenv

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters.callback_data import CallbackData

from typing import Optional
from datetime import datetime, timedelta



class Menu_callback(CallbackData, prefix="menu"):
    menu: str
    data: Optional[str] = None
    data2: Optional[str] = None


class Price_callback(CallbackData, prefix="price"):
    menu: str
    order_id: Optional[int] = None
    price: Optional[int] = None
    user_id: Optional[int] = None


class Message_callback(CallbackData, prefix="message"):
    menu: str
    user_id: int
    order_id: int
    topic: Optional[str] = None


load_dotenv()
id_admin = os.getenv("admin")
rules_url = os.getenv("rules_url")



def orders_kb(orders):
    """
    Создает клавиатуру для отображения заказов.
    :param orders: Список заказов, каждый из которых содержит информацию о заказе.
    :return: InlineKeyboardMarkup с кнопками заказов.
    """
    kb = []

    for order in orders:
        # print(order)
        # Преобразуем каждый заказ в словарь
        order_id = order["id"]
        title = order["title"]
        created_at = order["created_at"]

        # Преобразуем дату создания в нужный формат
        try:
            created_at_dt = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
            created_at_str = created_at_dt.strftime('%Y-%m-%d')  # Форматируем как YYYY-MM-DD
        except ValueError:
            created_at_str = 'Неизвестная дата'  # Обработка некорректной даты

        # Создаем кнопку с кратким названием и датой
        button_text = f"{title} | {created_at_str}"
        callback_data = Menu_callback(menu='order', data=str(order_id)).pack()

        kb.append([
            InlineKeyboardButton(
                text=button_text,
                callback_data=callback_data
            )
        ])

    # Добавляем кнопку "Назад" в конец
    kb.append([
        InlineKeyboardButton(
            text='◀️ Назад',
            callback_data=Menu_callback(menu='menu').pack()
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=kb)


def active_orders_kb(orders):
    """
    Создает клавиатуру для отображения заказов.
    :param orders: Список заказов, каждый из которых содержит информацию о заказе.
    :return: InlineKeyboardMarkup с кнопками заказов.
    """
    kb = []

    for order in orders:
        # print(order)
        # Преобразуем каждый заказ в словарь
        order_id = order["id"]
        title = order["title"]
        created_at = order["created_at"]

        # Преобразуем дату создания в нужный формат
        try:
            created_at_dt = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
            created_at_str = created_at_dt.strftime('%Y-%m-%d')  # Форматируем как YYYY-MM-DD
        except ValueError:
            created_at_str = 'Неизвестная дата'  # Обработка некорректной даты

        # Создаем кнопку с кратким названием и датой
        button_text = f"{title} | {created_at_str}"
        callback_data = Menu_callback(menu='active_order', data=str(order_id)).pack()

        kb.append([
            InlineKeyboardButton(
                text=button_text,
                callback_data=callback_data
            )
        ])

    # Добавляем кнопку "Назад" в конец
    kb.append([
        InlineKeyboardButton(
            text='◀️ Назад',
            callback_data=Menu_callback(menu='profile').pack()
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=kb)


def user_kb(orders, user_id, admin_status=False):
    """
    Создает клавиатуру для отображения заказов.
    :param orders: Список заказов, каждый из которых содержит информацию о заказе.
    :return: InlineKeyboardMarkup с кнопками заказов.
    """
    kb = []

    if admin_status:
        kb.append(
            [
                InlineKeyboardButton(text='Выгнать участника', callback_data=Menu_callback(menu='ban_user', data=str(user_id)).pack()),
            ]
        )

    kb.append(
        [
            InlineKeyboardButton(text='+ Варн', callback_data=Menu_callback(menu='add_warn', data=str(user_id)).pack()),
            InlineKeyboardButton(text='- Варн', callback_data=Menu_callback(menu='remove_warn', data=str(user_id)).pack()),
        ]
    )

    for order in orders:
        # print(order)
        # Преобразуем каждый заказ в словарь
        order_id = order["id"]
        title = order["title"]
        created_at = order["created_at"]

        # Преобразуем дату создания в нужный формат
        try:
            created_at_dt = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
            created_at_str = created_at_dt.strftime('%Y-%m-%d')  # Форматируем как YYYY-MM-DD
        except ValueError:
            created_at_str = 'Неизвестная дата'  # Обработка некорректной даты

        # Создаем кнопку с кратким названием и датой
        button_text = f"{title} | {created_at_str}"
        callback_data = Menu_callback(menu='admin_order', data=str(order_id)).pack()

        kb.append([
            InlineKeyboardButton(
                text=button_text,
                callback_data=callback_data
            )
        ])

    # Добавляем кнопку "Назад" в конец
    kb.append([
        InlineKeyboardButton(text='◀️ Назад', callback_data=Menu_callback(menu='users').pack())
    ])

    return InlineKeyboardMarkup(inline_keyboard=kb)


def start_kb():
    kb = [
        [
            InlineKeyboardButton(text='🚀 Начать', callback_data=Menu_callback(menu='start').pack()),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=kb)


def decline_order_kb(user_id, order_id):
    kb = [
        [
            InlineKeyboardButton(text='✅ Принять запрос', callback_data=Message_callback(menu='accept_request', user_id=user_id, order_id=order_id).pack()),
        ],
        [
            InlineKeyboardButton(text='❌ Отклонить запрос', callback_data=Message_callback(menu='decline_request', user_id=user_id, order_id=order_id).pack()),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=kb)


def price_offer_kb(price, order_id, user_id):
    kb = [
        [
            InlineKeyboardButton(text='✅ Принять цену', callback_data=Price_callback(menu='accept_price', order_id=order_id, price=price, user_id=user_id).pack()),
        ],
        [
            InlineKeyboardButton(text='❌ Отклонить запрос', callback_data=Price_callback(menu='accept_price', order_id=order_id, price=price, user_id=user_id).pack()),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=kb)


def accepted_kb():
    kb = [
        [
            InlineKeyboardButton(text='✅ Принято', callback_data=Menu_callback(menu='accepted').pack()),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=kb)


def ban_user_kb():
    kb = [
        [
            InlineKeyboardButton(text='✅ Подтвердить', callback_data=Menu_callback(menu='yes').pack()),
        ],
        [
            InlineKeyboardButton(text='Отмена', callback_data=Menu_callback(menu='admin_panel').pack()),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=kb)


def declined_kb():
    kb = [
        [
            InlineKeyboardButton(text='❌ Отклонено', callback_data=Menu_callback(menu='declined').pack()),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=kb)


def admin_kb(general_admin=False):
    kb = [
        [
            InlineKeyboardButton(text='📋 Список участников', callback_data=Menu_callback(menu='users').pack()),
        ],
        [
            InlineKeyboardButton(text='📩 Создать заказ', callback_data=Menu_callback(menu='new_order').pack()),
        ],
        [
            InlineKeyboardButton(text='📘 Добавить в вайт-лист', callback_data=Menu_callback(menu='add_user').pack()),
        ],
    ]

    if general_admin:
        kb.append(
        [
            InlineKeyboardButton(text='📬 Рассылка', callback_data=Menu_callback(menu='newsletter').pack()),
        ],)

    kb.append(
        [
            InlineKeyboardButton(text='◀️ Назад', callback_data=Menu_callback(menu='menu').pack()),
        ],
    )

    return InlineKeyboardMarkup(inline_keyboard=kb)


def profile_kb(notifications):

    if notifications:
        status = '🟢'
    else:
        status = '🔴'

    kb = [
        [
            InlineKeyboardButton(text=f'{status} Уведомления', callback_data=Menu_callback(menu='notifications').pack()),
        ],
        [
            InlineKeyboardButton(text='📦 Активные заказы', callback_data=Menu_callback(menu='active_orders').pack()),
        ],
        [
            InlineKeyboardButton(text='❓ FAQ по выговорам', callback_data=Menu_callback(menu='FAQ').pack()),
        ],
        [
            InlineKeyboardButton(text='📙 Правила', url=rules_url),
        ],
        [
            InlineKeyboardButton(text='◀️ Назад', callback_data=Menu_callback(menu='menu').pack()),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=kb)


def users_kb(users: list):

    kb = []

    for i in range(0, len(users), 3):
        row = []
        for user in users[i:i + 3]:
            # Определяем, выбрана ли технология
            row.append(
                InlineKeyboardButton(
                    text=f"{user['username']}",
                    callback_data=Menu_callback(menu='user', data=str(user['id'])).pack()
                )
            )
        kb.append(row)

    kb.append(
        [InlineKeyboardButton(
            text='◀️ Назад', 
            callback_data=Menu_callback(menu='admin_panel').pack()
        )],
    )

    return InlineKeyboardMarkup(inline_keyboard=kb)


def order_kb(admin_id, order_id):
    kb = [
        [
            InlineKeyboardButton(text='✅ Принять', callback_data=Message_callback(menu='accept_order', user_id=admin_id, order_id=order_id).pack()),
            InlineKeyboardButton(text='❌ Отклонить', callback_data=Message_callback(menu='decline_order', user_id=admin_id, order_id=order_id).pack()),
        ],
        [
            InlineKeyboardButton(text='📝 Предложить сумму', callback_data=Menu_callback(menu='offer_price', data=str(order_id)).pack()),
            InlineKeyboardButton(text='❓ Уточнить ТЗ', callback_data=Message_callback(menu='message', user_id=admin_id, order_id=order_id, topic=' ❓Уточнение ТЗ').pack()),
        ],
        [   
            InlineKeyboardButton(text='◀️ Назад', callback_data=Menu_callback(menu='orders').pack()),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=kb)


def news_kb():
    kb = [
        [
            InlineKeyboardButton(text='🔕 Обычная', callback_data=Menu_callback(menu='news', data='regular').pack()),
            InlineKeyboardButton(text='🔔 Обязательная', callback_data=Menu_callback(menu='news', data='mandatory').pack()),
        ],
        [   
            InlineKeyboardButton(text='◀️ Назад', callback_data=Menu_callback(menu='admin_panel').pack()),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=kb)


def order_admin_kb(order_id, user_id):
    kb = [
        [
            InlineKeyboardButton(text='✅ Завершить заказ', callback_data=Menu_callback(menu='comlete_order', data=str(order_id), data2=str(user_id)).pack()),
        ],
        [
            InlineKeyboardButton(text='❌ Удалить заказ', callback_data=Menu_callback(menu='rejected_order', data=str(order_id), data2=str(user_id)).pack()),
        ],
        [   
            InlineKeyboardButton(text='◀️ Назад', callback_data=Menu_callback(menu='admin_panel').pack()),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=kb)


def order_profile_kb(admin_id, order_id):
    kb = [
        [
            InlineKeyboardButton(text='❓ Уточнить ТЗ', callback_data=Message_callback(menu='message', user_id=admin_id, order_id=order_id).pack()),
            InlineKeyboardButton(text='📝 Предложить сумму', callback_data=Menu_callback(menu='offer_price', data=str(order_id)).pack()),
        ],
        # [
        #     InlineKeyboardButton(text='✅ Заказ выполнен', callback_data=Message_callback(menu='end_active_order', user_id=admin_id, order_id=order_id).pack()),
        # ],
        [
            InlineKeyboardButton(text='❌ Отказаться', callback_data=Message_callback(menu='decline_active_order', user_id=admin_id, order_id=order_id).pack()),
        ],
        [   
            InlineKeyboardButton(text='◀️ Назад', callback_data=Menu_callback(menu='active_orders').pack()),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=kb)



def reply_kb(user_id, order_id, topic):

    kb = []
    if topic is None:
        button = [
            InlineKeyboardButton(text='Ответить', callback_data=Message_callback(menu='message', user_id=user_id, order_id=order_id).pack()),
        ]
        kb.append(button)

    else:
        button = [
            InlineKeyboardButton(text='Ответить', callback_data=Message_callback(menu='message', user_id=user_id, order_id=order_id, topic=topic).pack()),
        ]
        kb.append(button)
        


    return InlineKeyboardMarkup(inline_keyboard=kb)


def confirm_order_kb():
    kb = [
        [
            InlineKeyboardButton(text='Создать заказ', callback_data=Menu_callback(menu='confirm_order').pack()),
        ],
        [
            InlineKeyboardButton(text='◀️ Назад', callback_data=Menu_callback(menu='cancel').pack()),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=kb)


def cancel_menu_kb():
    kb = [
        [
            InlineKeyboardButton(text='◀️ Назад', callback_data=Menu_callback(menu='menu').pack()),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=kb)


def cancel_admin_kb():
    kb = [
        [
            InlineKeyboardButton(text='◀️ Назад', callback_data=Menu_callback(menu='admin_panel').pack()),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=kb)


def cancel_news_kb():
    kb = [
        [
            InlineKeyboardButton(text='Отмена', callback_data=Menu_callback(menu='newsletter').pack()),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=kb)


def cancel_kb():
    kb = [
        [
            InlineKeyboardButton(text='◀️ Назад', callback_data=Menu_callback(menu='cancel').pack()),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=kb)


def cancel_profile_kb():
    kb = [
        [
            InlineKeyboardButton(text='◀️ Назад', callback_data=Menu_callback(menu='profile').pack()),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=kb)


def menu_kb(Admin_status=False):

    kb = [
        [
            InlineKeyboardButton(text='📦 Заказы', callback_data=Menu_callback(menu='orders').pack()),
        ],
        [
            InlineKeyboardButton(text='⚙️ Профиль', callback_data=Menu_callback(menu='profile').pack()),
        ],
    ]

    if Admin_status:

        button = [InlineKeyboardButton(text='🛠 Админ панель', callback_data=Menu_callback(menu='admin_panel').pack())]
        kb.append(button)

    return InlineKeyboardMarkup(inline_keyboard=kb)


def order_price_kb(order_id):
    kb = [
        [
            InlineKeyboardButton(text='Посмотреть заказ', callback_data=Menu_callback(menu='order', data=str(order_id)).pack()),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=kb)


def order_accept_kb(admin_id, order_id):
    kb = [
        [
            InlineKeyboardButton(text='⚡️ Написать менеджеру', callback_data=Message_callback(menu='message', user_id=admin_id, order_id=order_id, topic='⚡️ Сообщение').pack()),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=kb)


def role_kb():
    kb = [
        [
            InlineKeyboardButton(text='🎨 Дизайнер', callback_data=Menu_callback(menu='role', data='designer').pack()),
        ],
        [
            InlineKeyboardButton(text='💻 Разработчик', callback_data=Menu_callback(menu='role', data='developer').pack()),
        ],
        [
            InlineKeyboardButton(text='◀️ Назад', callback_data=Menu_callback(menu='menu').pack()),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=kb)


def role_order_kb():
    kb = [
        [
            InlineKeyboardButton(text='🎨 Дизайнер', callback_data=Menu_callback(menu='role', data='designer').pack()),
        ],
        [
            InlineKeyboardButton(text='💻 Разработчик', callback_data=Menu_callback(menu='role', data='developer').pack()),
        ],
        [
            InlineKeyboardButton(text='◀️ Назад', callback_data=Menu_callback(menu='admin_panel').pack()),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=kb)


def deadline_kb():

    kb = [
        [
            InlineKeyboardButton(text='❌ Не указано', callback_data=Menu_callback(menu='no').pack()),
        ],
        [
            InlineKeyboardButton(text='◀️ Назад', callback_data=Menu_callback(menu='cancel').pack()),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=kb)



def price_kb():

    kb = [
        [
            InlineKeyboardButton(text='❌ Не указано', callback_data=Menu_callback(menu='no').pack()),
        ],
        [
            InlineKeyboardButton(text='◀️ Назад', callback_data=Menu_callback(menu='cancel').pack()),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=kb)



def order_size_kb(selected_sizes=None):

    if selected_sizes is None:
        selected_sizes = set()

    order_sizes = {
    'Малый': 'small',
    'Средний': 'medium',
    'Большой': 'large'
    }

    kb = []
    
    for size, code in order_sizes.items():
        text = f'{size} ✅' if code in selected_sizes else size
        kb.append([
            InlineKeyboardButton(
                text=text, 
                callback_data=Menu_callback(menu='order_size', data=code).pack()
            )
        ])

    # kb.append(
    #     [InlineKeyboardButton(
    #         text='Продолжить', 
    #         callback_data=Menu_callback(menu='next').pack()
    #     )],
    # )
    kb.append(
        [InlineKeyboardButton(
            text='◀️ Назад', 
            callback_data=Menu_callback(menu='cancel').pack()
        )],
    )


    return InlineKeyboardMarkup(inline_keyboard=kb)



# Функция для создания клавиатуры стека для дизайнеров
def stack_kb_designer(selected_technologies=[]):
    """
    Создает клавиатуру для выбора технологий с чекбоксами для дизайнеров.
    :param selected_technologies: Список выбранных технологий.
    :return: InlineKeyboardMarkup с кнопками технологий и "Продолжить".
    """
    technologies = ['GFX', 'UI/UX', 'Web', 'Motion', '3D']

    kb = []

    # Создаем кнопки из списка по 3 в ряд
    for i in range(0, len(technologies), 3):
        row = []
        for tech in technologies[i:i + 3]:
            emoji = "✅" if tech in selected_technologies else ""
            row.append(
                InlineKeyboardButton(
                    text=f"{tech} {emoji}",
                    callback_data=Menu_callback(menu='tech', data=tech).pack()
                )
            )
        kb.append(row)

    # Добавляем кнопку "Продолжить" в конец
    kb.append([
        InlineKeyboardButton(
            text='🚀 Продолжить',
            callback_data=Menu_callback(menu='next').pack()
        )],
    )
    kb.append(
        [InlineKeyboardButton(
            text='◀️ Назад', 
            callback_data=Menu_callback(menu='cancel').pack()
        )],
    )

    return InlineKeyboardMarkup(inline_keyboard=kb)



def stack_kb(selected_technologies=[]):
    """
    Создает клавиатуру для выбора технологий с чекбоксами.
    :param selected_technologies: Список выбранных технологий.
    :return: InlineKeyboardMarkup с кнопками технологий и "Продолжить".
    """
    technologies = [
        'JavaScript', 'TypeScript', 'Python', 'Java', 'C#', 'C++', 
        'PHP', 'Go (Golang)', 'Kotlin', 'Swift', 'Ruby', 'SQL', 
        'Node.js', 'React.js', 'Vue.js', 'Angular', 'Django', 
        'Flask', 'GraphQL', 'Docker', 'AioGram', 'Requests', 'FastAPI'
    ]

    kb = []

    # Создаем кнопки из списка по 3 в ряд
    for i in range(0, len(technologies), 3):
        row = []
        for tech in technologies[i:i + 3]:
            # Определяем, выбрана ли технология
            emoji = "✅" if tech in selected_technologies else ""
            row.append(
                InlineKeyboardButton(
                    text=f"{tech} {emoji}",
                    callback_data=Menu_callback(menu='tech', data=tech).pack()
                )
            )
        kb.append(row)

    # Добавляем кнопку "Продолжить" в конец
    kb.append([
        InlineKeyboardButton(
            text='🚀 Продолжить', 
            callback_data=Menu_callback(menu='next').pack()
        )]
    )
    kb.append(
        [InlineKeyboardButton(
            text='◀️ Назад', 
            callback_data=Menu_callback(menu='cancel').pack()
        )],
    )

    return InlineKeyboardMarkup(inline_keyboard=kb)