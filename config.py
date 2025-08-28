import os
from dotenv import load_dotenv
from aiogram import Bot
from aiogram.client.bot import DefaultBotProperties


if not os.path.exists(".env"):
    raise FileNotFoundError("Файл .env не найден")

load_dotenv()

bot_token = os.getenv("BOT_TOKEN")
if not bot_token:
    raise ValueError(f"Токен бота не найден. Убедитесь, что переменная окружения BOT_TOKEN установлена. TOKEN = {bot_token}")


bot = Bot(token=bot_token, default=DefaultBotProperties(parse_mode='HTML'))