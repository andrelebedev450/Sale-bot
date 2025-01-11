from aiogram import types, F
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardMarkup, KeyboardButton
from bot import dp, bot
from database.db_session import get_db
from database.models import User
from sqlalchemy.orm import Session

@dp.message(F.text == "Мой профиль ⁠🪪")
async def show_profile(message: types.Message):
    db = next(get_db())
    user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
    if user:
        await message.answer("🪪")
        
        profile_text = (
            f"🪪 *⁠Мой профиль*\n\n"
            f"ID: *{user.telegram_id}*\n"
            f"Регистрация: *{user.registration_time.strftime('%d.%m.%Y')}*\n\n"
            f"Основной баланс: *{user.balance}₽*\n"
            f"Партнерский баланс: *{user.partner_balance}₽*\n\n"
            f"*Статистика*\n"
            f"Всего покупок: *{user.total_purchases}*"
        )
        
        keyboard = InlineKeyboardBuilder()
        keyboard.row(
            types.InlineKeyboardButton(text="Мои заказы 📦", callback_data="my_orders"),
            types.InlineKeyboardButton(text="Пополнить 💳", callback_data="replenish")
        )
        keyboard.row(
            types.InlineKeyboardButton(text="Реферальная программа 👥", callback_data="referral_program")
        )
        
        await message.answer(profile_text, parse_mode='Markdown', reply_markup=keyboard.as_markup())
    else:
        await message.answer("Пользователь не найден.")

@dp.callback_query(F.data == 'my_orders')
async def my_orders_callback(callback_query: types.CallbackQuery):
    await callback_query.answer("Здесь будут ваши заказы.")

@dp.callback_query(F.data == 'replenish')
async def replenish_callback(callback_query: types.CallbackQuery):
    await callback_query.answer("Здесь можно пополнить баланс.")

@dp.callback_query(F.data == 'referral_program')
async def referral_program_callback(callback_query: types.CallbackQuery):
    await callback_query.answer("Здесь будет информация о реферальной программе.")

@dp.message(F.text == "Связаться 📞")
async def contact_support(message: types.Message):
    await message.answer("👨‍💻")
    support_text = "Здесь вы можете обратиться в службу поддержки."
    
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        types.InlineKeyboardButton(text="Создать обращение", callback_data="create_ticket")
    )
    keyboard.row(
        types.InlineKeyboardButton(text="Мои обращения", callback_data="my_tickets")
    )
    
    await message.answer(support_text, reply_markup=keyboard.as_markup())

@dp.callback_query(F.data == 'create_ticket')
async def create_ticket_callback(callback_query: types.CallbackQuery):
    message_text = "📩 *Связаться  ›  Выбор темы*\n\nВыберите тему обращения:"
    
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        types.InlineKeyboardButton(text="Проблема с заказом", callback_data="issue_order")
    )
    keyboard.row(
        types.InlineKeyboardButton(text="Проблема с пополнением", callback_data="issue_replenish")
    )
    keyboard.row(
        types.InlineKeyboardButton(text="Проблема с оплатой", callback_data="issue_payment")
    )
    keyboard.row(
        types.InlineKeyboardButton(text="Вопросы по товару", callback_data="issue_product")
    )
    keyboard.row(
        types.InlineKeyboardButton(text="< Назад", callback_data="back_to_support")
    )
    
    await callback_query.message.edit_text(message_text, reply_markup=keyboard.as_markup(), parse_mode="Markdown")

@dp.callback_query(F.data == 'my_tickets')
async def my_tickets_callback(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text("Здесь будут ваши обращения.")

@dp.callback_query(F.data == 'back_to_support')
async def back_to_support_callback(callback_query: types.CallbackQuery):
    support_text = "Здесь вы можете обратиться в службу поддержки."
    
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        types.InlineKeyboardButton(text="Создать обращение", callback_data="create_ticket")
    )
    keyboard.row(
        types.InlineKeyboardButton(text="Мои обращения", callback_data="my_tickets")
    )
    
    await callback_query.message.edit_text(support_text, reply_markup=keyboard.as_markup())