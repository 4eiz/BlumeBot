from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext




class Form(StatesGroup):
    nickname = State()
    rules = State()
    role = State()
    stack = State()
    preferences = State()
    portfolie = State()
    conf = State()