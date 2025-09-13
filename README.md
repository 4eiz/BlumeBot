# 🪻 BlumeBot — Telegram Bot for Orders

![Python](https://img.shields.io/badge/Python-3.10%2B-blue) ![Aiogram](https://img.shields.io/badge/aiogram-3.x-ff69b4) ![License](https://img.shields.io/badge/license-MIT-green) ![Status](https://img.shields.io/badge/status-Active-success)  

## 📖 Project Description
**BlumeBot** — a multi-user Telegram bot for handling and processing studio orders.  
It supports user profiles, order creation and management, moderation, and broadcasts.  
Storage: **SQLite (aiosqlite)**, framework: **aiogram 3**, configuration via **.env**.  

> 💡 This project is a test and demo version developed for a developer from Croatia.  

Screenshots and GIFs can be placed in the `assets/` folder and added here.  

## ✨ Main Features
- 👤 User profile and active orders  
- 🧾 Order creation and management (forms)  
- 🛡️ Whitelist/ban control  
- 🗞️ Broadcast messages (admin panel)  
- ❓ FAQ and start menu  
- 🪪 Roles/statuses (admin rights stored in DB/code)  

## 🧱 Tech Stack
- **Python 3.10+**  
- **aiogram 3.x**  
- **aiosqlite**  
- **python-dotenv**  

## 📂 Project Structure (simplified)
```
BlumeBot/
├─ app/                 # handlers, forms, admin panels
├─ data/                # DB: users, orders, whitelist; init scripts
├─ keyboards/           # inline/reply keyboards
├─ config.py            # loads .env and initializes Bot
├─ main.py              # startup/dispatcher, router registration
├─ req.txt              # dependencies (aiogram, aiosqlite, python-dotenv)
└─ data/create_tables.sql
```

## ⚙️ Environment Variables
Create a `.env` file based on the example and fill in the values:
```
BOT_TOKEN=    # Telegram bot token (required)
admin=        # Administrator ID (integer)
admin_name=   # Admin username/name (optional, for auto-fill)
```
> `admin` and `admin_name` are used in `data/main.py`. `BOT_TOKEN` is used in `config.py`.  

## 🚀 Installation & Run
```bash
git clone https://github.com/<username>/blumebot.git
cd blumebot

# 1) Create and activate virtual environment
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows:
# .venv\Scripts\activate

# 2) Install dependencies
pip install -r BlumeBot/req.txt

# 3) Configure environment
cp .env.example .env
# then edit .env and insert your BOT_TOKEN and admin

# 4) Run the bot
python BlumeBot/main.py
```

### 🔌 Webhook (optional)
The project mentions `webhook` in `main.py`.  
If you want to use webhooks, prepare a public HTTPS URL (ngrok/Reverse proxy) and implement webhook setup logic.  
By default, you can work with `polling`.  

## 🧪 Tests / Code Quality (optional)
You can add: `pytest`, `ruff/flake8`, `black`, and CI.  

## 🛠 Useful Repo Commands
```bash
# initial repo setup
git init
git add .
git commit -m "chore: init BlumeBot repo"

# create GitHub repo via gh CLI
gh repo create 4eiz/blumebot --public --source=. --remote=origin --push
```

## 🧹 .gitignore & Secrets
- Do **not** commit `.env`. Only keep `.env.example` in the repo.  
- Binary artifacts, caches, virtual envs should go into `.gitignore`.  

## 📜 License
MIT — see `LICENSE`.  

---

**Author:** Robert • **Contact:** [Telegram](https://t.me/che1zi)
