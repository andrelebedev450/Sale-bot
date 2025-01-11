import os
import logging
from aiogram import Bot, Dispatcher
from utils.config_reader import config

assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.bot_token.get_secret_value())
dp = Dispatcher()