import asyncio
import logging
from bot import bot, dp
from handlers import start, menu
from database.init_db import init_db
from database.db_session import get_db
from utils.config_reader import config

async def main():
    init_db() 
    await dp.start_polling(bot, allowed_updates=["message", "callback_query", "my_chat_member", "chat_member"])

if __name__ == "__main__":
    asyncio.run(main())