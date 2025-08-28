import asyncio
import logging
from aiogram import Dispatcher

from config import bot
from data.main import script, settings_set

from app import start, orders, send_message, profile, active_orders, faq
from app.form_app import send_request, admin_conf
from app.admin import remote_whitelist, remote_users, admin_panel, newsletter
from app.form_order import create_order




async def start_bot():
    dp = Dispatcher()

    dp.include_routers(
        start.router,
        send_request.router,
        admin_conf.router,
        remote_whitelist.router,
        create_order.router,
        orders.router,
        send_message.router,
        profile.router,
        remote_users.router,
        admin_panel.router,
        active_orders.router,
        faq.router,
        newsletter.router,
    )

    await script()
    await settings_set()
    
    logging.basicConfig(level=logging.INFO)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(start_bot())
