import os
import string
import random
from aiogram import types
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardMarkup, KeyboardButton
from bot import dp, bot, assets_dir
from aiogram.types import FSInputFile
from keyboards.menu_keyboards import menu_keyboard
from database.db_session import get_db
from database.models import User
from sqlalchemy.orm import Session

def generate_referral_code():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    db = next(get_db())
    user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
    
    if not user:
        referral_code = generate_referral_code()
        user = User(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            full_name=message.from_user.full_name,
            referral_code=referral_code
        )
        db.add(user)
        db.commit()
        
        args = message.text.split()
        if len(args) > 1:
            referrer_code = args[1]
            if referrer_code != referral_code:
                referrer = db.query(User).filter(User.referral_code == referrer_code).first()
                if referrer:
                    referrer.invited_count += 1
                    referrer.total_earned += 10 
                    db.commit()

    bot_info = await bot.get_me()
    bot_username = bot_info.username
    welcome_text = (
        "Добро пожаловать.\n\n"
        "Скорее всего у многих из вас появится вопрос - \"почему всё так дёшево?\", и он более чем логичен, ведь цены у нас и в правду крайне низкие, я отвечу вам на него.\n\n"
        "Мы зарабатываем на том, что покупаем дорогостоящие материалы, и продаём их за более низкий прайс чем у их авторов, но на более обширную аудиторию!\n\n"
        f"❗️Правила магазина: [ссылка](https://telegra.ph/Pravila-soglasheniya-i-politika-08-06).\n\n"
        f"Ваш реферальный код: {user.referral_code}\n"
        f"Ссылка для приглашения друзей: https://t.me/{bot_username}?start={user.referral_code}"
    )
    photo_path = os.path.join(assets_dir, 'img', 'hello_img.jpg')
    if os.path.exists(photo_path):
        photo = FSInputFile(photo_path)
        await message.answer_photo(photo, caption=welcome_text, parse_mode='Markdown', reply_markup=menu_keyboard)
    else:
        pass

