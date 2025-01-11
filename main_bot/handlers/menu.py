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
    await callback_query.message.edit_text("📩 *Связаться  ›  Все обращения*\n\n Здесь будут ваши обращения.", parse_mode="Markdown")

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

async def edit_message_to_previous_state(callback_query: types.CallbackQuery, previous_text: str, previous_keyboard: InlineKeyboardBuilder):
    await callback_query.message.delete()
    
    await bot.send_message(callback_query.message.chat.id, previous_text, reply_markup=previous_keyboard.as_markup(), parse_mode="Markdown")

@dp.message(F.text == "🎁 ПОЛУЧИ БОНУСЫ 🎁")
async def get_bonuses(message: types.Message):
    await message.answer("💰")
    
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        types.InlineKeyboardButton(text="⚡🎁 Розыгрыши (N) 🎁⚡", callback_data="lotteries")
    )
    keyboard.row(
        types.InlineKeyboardButton(text="Акции и бонусы (N)", callback_data="promotions")
    )
    keyboard.row(
        types.InlineKeyboardButton(text="Деньги за друзей", callback_data="referral_money")
    )
    
    await message.answer("🎁 Бонусы, розыгрыши и задания", reply_markup=keyboard.as_markup())

@dp.callback_query(F.data == 'lotteries')
async def lotteries_callback(callback_query: types.CallbackQuery):
    message_text = "🎰 *Розыгрыши*\n\nВыберите розыгрыш:"
    
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        types.InlineKeyboardButton(text="🎫Мои билеты", callback_data="my_tickets_lotteries")
    )
    keyboard.row(
        types.InlineKeyboardButton(text="< Назад", callback_data="back_to_bonuses")
    )
    
    await callback_query.message.edit_text(message_text, reply_markup=keyboard.as_markup(), parse_mode="Markdown")

@dp.callback_query(F.data == 'promotions')
async def promotions_callback(callback_query: types.CallbackQuery):
    message_text = "🎁 *Акции и бонусы*\n\nВыберите нужный пункт:"
    
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        types.InlineKeyboardButton(text="< Назад", callback_data="back_to_bonuses")
    )
    
    await callback_query.message.edit_text(message_text, reply_markup=keyboard.as_markup(), parse_mode="Markdown")

@dp.callback_query(F.data == 'referral_money')
async def referral_money_callback(callback_query: types.CallbackQuery):
    message_text = (
        "💸 *Деньги за друзей*\n\n"
        "Приглашено: *0*\n"
        "Баланс: *0₽*\n\n"
        "Получай *10₽ за одного* приглашенного друга\n\n"
        "Ссылка для друга:\n"
        "[https://t.me/this_bot?start=50ANa9toFQ](https://t.me/this_bot?start=50ANa9toFQ)"
    )
    
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        types.InlineKeyboardButton(text="Вывести средства", callback_data="withdraw_funds")
    )
    keyboard.row(
        types.InlineKeyboardButton(text="< Назад", callback_data="back_to_bonuses")
    )
    
    await callback_query.message.edit_text(message_text, reply_markup=keyboard.as_markup(), parse_mode="Markdown")

@dp.callback_query(F.data == 'withdraw_funds')
async def withdraw_funds_callback(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text("Здесь можно вывести средства.", parse_mode="Markdown")

@dp.callback_query(F.data == 'back_to_bonuses')
async def back_to_bonuses_callback(callback_query: types.CallbackQuery):
    previous_text = "🎁 Бонусы, розыгрыши и задания"
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        types.InlineKeyboardButton(text="⚡🎁 Розыгрыши (N) 🎁⚡", callback_data="lotteries")
    )
    keyboard.row(
        types.InlineKeyboardButton(text="Акции и бонусы (N)", callback_data="promotions")
    )
    keyboard.row(
        types.InlineKeyboardButton(text="Деньги за друзей", callback_data="referral_money")
    )
    await edit_message_to_previous_state(callback_query, previous_text, keyboard)

@dp.callback_query(F.data == 'my_tickets_lotteries')
async def my_tickets_lotteries_callback(callback_query: types.CallbackQuery):
    message_text = "🎫 *Мои билеты*\n\nВсего билетов: *0*"
    
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        types.InlineKeyboardButton(text="< Назад", callback_data="back_to_lotteries")
    )
    
    await callback_query.message.edit_text(message_text, reply_markup=keyboard.as_markup(), parse_mode="Markdown")

@dp.callback_query(F.data == 'back_to_lotteries')
async def back_to_lotteries_callback(callback_query: types.CallbackQuery):
    previous_text = "🎰 *Розыгрыши*\n\nВыберите розыгрыш:"
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        types.InlineKeyboardButton(text="🎫Мои билеты", callback_data="my_tickets_lotteries")
    )
    keyboard.row(
        types.InlineKeyboardButton(text="< Назад", callback_data="back_to_bonuses")
    )
    await edit_message_to_previous_state(callback_query, previous_text, keyboard)