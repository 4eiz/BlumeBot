# 🪻 BlumeBot — бот студии для выполнения заказов

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Aiogram](https://img.shields.io/badge/aiogram-3.x-ff69b4)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-Active-success)

## 📖 Описание проекта
BlumeBot — многоюзерный Telegram‑бот студии для приёма и обработки заказов.
Поддерживает работу с профилем пользователя, заказами, модерацией и рассылками.
Хранение — **SQLite (aiosqlite)**, фреймворк — **aiogram 3**. Конфигурация через **.env**.

> Скриншоты и GIF можно положить в `assets/` и вставить сюда.

## ✨ Основные возможности
- 👤 Профиль пользователя и активные заказы
- 🧾 Создание и управление заказами (формы)
- 🛡️ Вайтлист/бан‑контроль
- 🗞️ Рассылка сообщений администраторами
- ❓ FAQ и стартовое меню
- 🪪 Роли/статусы (права админа в коде/БД)

## 🧱 Технологии
- **Python 3.10+**
- **aiogram 3.x**
- **aiosqlite**
- **python‑dotenv**

## 📂 Структура проекта (сокращённо)
```
BlumeBot/
├─ app/                 # хендлеры, формы, панели админа
├─ data/                # БД: users, orders, whitelist; init-скрипты
├─ keyboards/           # инлайн/реплай клавиатуры
├─ config.py            # загрузка .env и инициализация Bot
├─ main.py              # запуск/диспетчер, регистрация роутеров
├─ req.txt              # зависимости (aiogram, aiosqlite, python-dotenv)
└─ data/create_tables.sql
```

## ⚙️ Переменные окружения
Создайте `.env` на основе примера и заполните значения:
```
BOT_TOKEN=    # токен Telegram-бота (обязательно)
admin=        # ID администратора (целое число)
admin_name=   # username/имя админа (опционально, для автозаполнения)
```
> Переменные `admin` и `admin_name` читаются в `data/main.py`. `BOT_TOKEN` — в `config.py`.

## 🚀 Установка и запуск
```bash
git clone https://github.com/<username>/blumebot.git
cd blumebot

# 1) Создать и активировать виртуальную среду
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows:
# .venv\Scripts\activate

# 2) Установить зависимости
pip install -r BlumeBot/req.txt

# 3) Настроить окружение
cp .env.example .env
# затем отредактируйте .env и вставьте ваш BOT_TOKEN и admin

# 4) Запуск
python BlumeBot/main.py
```

### 🔌 Вебхук (опционально)
В проекте есть упоминание `webhook` в `main.py`. Если вы используете вебхуки, подготовьте публичный HTTPS URL (ngrok/Reverse proxy) и добавьте логику установки вебхука (если требуется). По умолчанию можно работать в `polling`.

## 🧪 Тесты/качество кода (опционально)
Добавьте по желанию: `pytest`, `ruff/flake8`, `black` и CI.

## 🛠 Полезные команды для репозитория
```bash
# первичная инициализация
git init
git add .
git commit -m "chore: init BlumeBot repo"

# создать репозиторий на GitHub через gh CLI
gh repo create <username>/blumebot --public --source=. --remote=origin --push
```

## 🧹 .gitignore и секреты
- Файл `.env` **не коммитим**. В репозитории держим только `.env.example`.
- Бинарные артефакты, кеши, виртуальные среды — в `.gitignore`.

## 📜 Лицензия
MIT. См. `LICENSE`.

---

**Автор:** Роберт • **Контакты:** [Telegram](https://t.me/che1zi)
