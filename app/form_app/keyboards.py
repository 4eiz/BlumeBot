import os
from dotenv import load_dotenv

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData
from typing import Optional




class Menu_callback(CallbackData, prefix="menu"):
    menu: str
    data: Optional[str] = None

class Answer_callback(CallbackData, prefix="answer"):
    answer: str
    user_id: int
    rank: Optional[str] = None


class Accept_callback(CallbackData, prefix="answer"):
    menu: str


rules_url = os.getenv("rules_url")





def order_size_kb(selected_sizes=None):

    if selected_sizes is None:
        selected_sizes = set()

    order_sizes = {
    'Мелкие': 'small',
    'Средние': 'medium',
    'Большие': 'large'
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

    kb.append(
        [InlineKeyboardButton(
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


def rules_kb():
    kb = [
        [
            InlineKeyboardButton(text='📙 Правила', url=rules_url),
        ],
        [
            InlineKeyboardButton(text='✅ Я прочитал, далее', callback_data=Menu_callback(menu='accept_rules').pack()),
        ],
        [
            InlineKeyboardButton(text='◀️ Назад', callback_data=Menu_callback(menu='cancel').pack()),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=kb)


def menu_kb():
    kb = [
        [
            InlineKeyboardButton(text='🏠 Главное меню', callback_data=Menu_callback(menu='menu').pack()),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=kb)


# def rules_kb():
#     kb = [
#         [
#             InlineKeyboardButton(text='Я прочитал', callback_data=Menu_callback(menu='accept_rules').pack()),
#         ],
#         [
#             InlineKeyboardButton(text='Продолжить', callback_data=Menu_callback(menu='next').pack()),
#         ],
#         [
#             InlineKeyboardButton(
#             text='Назад', 
#             callback_data=Menu_callback(menu='cancel').pack()
#         )],
#     ]

#     return InlineKeyboardMarkup(inline_keyboard=kb)


# def rules_accepted_kb():
#     kb = [
#         [
#             InlineKeyboardButton(text='Я прочитал ✅', callback_data=Menu_callback(menu='accepted').pack()),
#         ],
#         [
#             InlineKeyboardButton(text='Продолжить', callback_data=Menu_callback(menu='next').pack()),
#         ],
#         [InlineKeyboardButton(
#             text='Назад ◀️', 
#             callback_data=Menu_callback(menu='cancel').pack()
#         )],
#     ]

#     return InlineKeyboardMarkup(inline_keyboard=kb)


def role_kb():
    kb = [
        [
            InlineKeyboardButton(text='🎨 Дизайнер', callback_data=Menu_callback(menu='role', data='designer').pack()),
        ],
        [
            InlineKeyboardButton(text='💻 Разработчик', callback_data=Menu_callback(menu='role', data='developer').pack()),
        ],
        [
            InlineKeyboardButton(text='👨🏻‍💻 Менеджер', callback_data=Menu_callback(menu='role', data='manager').pack()),
        ],
        [
            InlineKeyboardButton(text='◀️ Назад', callback_data=Menu_callback(menu='cancel').pack()),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=kb)



def cancel_kb():
    kb = [
        [
            InlineKeyboardButton(text='◀️ Назад', callback_data=Menu_callback(menu="cancel").pack())
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


def port_kb():
    kb = [
        [
            InlineKeyboardButton(text='❌ Не указано', callback_data=Menu_callback(menu='no').pack()),
        ],
        [
            InlineKeyboardButton(text='◀️ Назад', callback_data=Menu_callback(menu="cancel").pack()),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=kb)


def conf_kb():
    kb = [
        [
            InlineKeyboardButton(text='✅ Подтвердить', callback_data=Menu_callback(menu='confirmation').pack()),
        ],
        [
            InlineKeyboardButton(text='✏️ Изменить', callback_data=Menu_callback(menu="change").pack()),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=kb)


def admin_conf(user_id):

    kb = []
    ranks = {
        '🤵🏻 Работник': 'member',
        '👨🏻‍💻 Админ': 'admin'
    }

    for name, code in ranks.items():
        button = [
            InlineKeyboardButton(text=name, callback_data=Answer_callback(answer="accept", user_id=user_id, rank=code).pack())
        ]
        kb.append(button)

    button = [
        InlineKeyboardButton(text='❌ Отклонить', callback_data=Answer_callback(answer="decline", user_id=user_id).pack())
    ]
    kb.append(button)

    return InlineKeyboardMarkup(inline_keyboard=kb)


def accept():
    kb = [
        [
            InlineKeyboardButton(text='✅ Принято', callback_data=Menu_callback(menu="accepted").pack())
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


def decline():
    kb = [
        [
            InlineKeyboardButton(text='❌ Отклонено', callback_data=Menu_callback(menu="declined").pack())
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)