import os
from aiogram import types, F
from aiogram.types import FSInputFile
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardMarkup, KeyboardButton
from bot import dp, bot, assets_dir
from database.db_session import get_db
from database.models import *
from sqlalchemy.orm import Session
from aiogram.fsm.context import FSMContext
from states.states import SupportTicketStates

TICKETS_PER_PAGE = 5  # Define the number of tickets per page

TOPIC_MAP = {
    "order": "Проблема с заказом",
    "replenish": "Проблема с пополнением",
    "payment": "Проблема с оплатой",
    "product": "Вопросы по товару"
}

async def edit_message_to_previous_state(callback_query: types.CallbackQuery, previous_state_function, delete_previous_message=False):
    await callback_query.message.delete()
    if delete_previous_message:
        try:
            await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id - 1)
        except:
            pass
    if 'user' in previous_state_function.__code__.co_varnames:
        await previous_state_function(callback_query.message, callback_query.from_user)
    else:
        await previous_state_function(callback_query.message)

@dp.message(F.text == "Мой профиль ⁠🪪")
async def show_profile(message: types.Message, user: types.User = None):
    db = next(get_db())
    user_id = user.id if user else message.from_user.id
    user = db.query(User).filter(User.telegram_id == user_id).first()
    if user:
        await message.answer("🪪")
        
        profile_text = (
            f"🪪 *⁠Мой профиль*\n\n"
            f"ID: *{user.telegram_id}*\n"
            f"Регистрация: *{user.registration_time.strftime('%d.%m.%Y')}*\n\n"
            f"Основной баланс: *{user.balance}₽*\n"
            f"Партнерский баланс: *{user.partner_balance}₽*\n\n"
            f"*Статистика*\n"
            f"Всего покупок: *{user.total_purchases}*\n\n"
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

@dp.callback_query(F.data == 'referral_program')
async def referral_program_callback(callback_query: types.CallbackQuery):
    db = next(get_db())
    user = db.query(User).filter(User.telegram_id == callback_query.from_user.id).first()
    if user:
        bot_info = await bot.get_me()
        bot_username = bot_info.username
        referral_link = f"https://t.me/{bot_username}?start={user.referral_code}"
        message_text = (
            f"💸 *Деньги за друзей*\n\n"
            f"Приглашено: *{user.invited_count}*\n"
            f"Баланс: *{user.total_earned}₽*\n\n"
            f"Получай *10₽ за одного* приглашенного друга\n\n"
            f"Ссылка для друга:\n"
            f"[{referral_link}]({referral_link})"
        )
        
        keyboard = InlineKeyboardBuilder()
        keyboard.row(
            types.InlineKeyboardButton(text="Вывести средства", callback_data="withdraw_funds")
        )
        keyboard.row(
            types.InlineKeyboardButton(text="< Назад", callback_data="back_to_profile:show_profile:True")
        )
        
        await callback_query.message.edit_text(message_text, reply_markup=keyboard.as_markup(), parse_mode="Markdown")

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
        types.InlineKeyboardButton(text="< Назад", callback_data="back_to_support:contact_support:True")
    )
    
    await callback_query.message.edit_text(message_text, reply_markup=keyboard.as_markup(), parse_mode="Markdown")

@dp.callback_query(F.data == 'my_tickets')
async def my_tickets_callback(callback_query: types.CallbackQuery, state: FSMContext):
    await state.update_data(page=1)
    await show_tickets(callback_query.message, callback_query.from_user.id, 1)

async def show_tickets(message: types.Message, user_id: int, page: int):
    db = next(get_db())
    user = db.query(User).filter(User.telegram_id == user_id).first()
    if user:
        tickets = db.query(SupportTicket).filter(SupportTicket.user_id == user.id).order_by(SupportTicket.created_at.desc()).all()
        total_pages = (len(tickets) + TICKETS_PER_PAGE - 1) // TICKETS_PER_PAGE
        start = (page - 1) * TICKETS_PER_PAGE
        end = start + TICKETS_PER_PAGE
        tickets_page = tickets[start:end]

        message_text = "📩 *Связаться  ›  Все обращения*\n\nЗдесь вы можете управлять обращениями."
        keyboard = InlineKeyboardBuilder()
        
        for ticket in tickets_page:
            keyboard.row(types.InlineKeyboardButton(text=f"{ticket.topic} ({ticket.status})", callback_data=f"ticket_{ticket.id}"))
        
        keyboard.row(
            types.InlineKeyboardButton(text="⬅️", callback_data="prev_page"),
            types.InlineKeyboardButton(text=f"{page}/{total_pages}", callback_data="current_page"),
            types.InlineKeyboardButton(text="➡️", callback_data="next_page")
        )
        keyboard.row(
            types.InlineKeyboardButton(text="< Назад", callback_data="back_to_support:contact_support:True")
        )
        
        await message.edit_text(message_text, reply_markup=keyboard.as_markup(), parse_mode="Markdown")

@dp.callback_query(F.data == 'prev_page')
async def prev_page_callback(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    page = data.get("page", 1)
    if page > 1:
        page -= 1
        await state.update_data(page=page)
        await show_tickets(callback_query.message, callback_query.from_user.id, page)

@dp.callback_query(F.data == 'next_page')
async def next_page_callback(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    page = data.get("page", 1)
    db = next(get_db())
    user = db.query(User).filter(User.telegram_id == callback_query.from_user.id).first()
    if user:
        total_tickets = db.query(SupportTicket).filter(SupportTicket.user_id == user.id).count()
        total_pages = (total_tickets + TICKETS_PER_PAGE - 1) // TICKETS_PER_PAGE
        if page < total_pages:
            page += 1
            await state.update_data(page=page)
            await show_tickets(callback_query.message, callback_query.from_user.id, page)

@dp.callback_query(F.data.startswith('ticket_'))
async def ticket_details_callback(callback_query: types.CallbackQuery):
    ticket_id = int(callback_query.data.split('_')[1])
    db = next(get_db())
    ticket = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()
    if ticket:
        message_text = (
            f"📩 *Обращение*\n\n"
            f"Тема: {ticket.topic}\n"
            f"Текст: {ticket.message}\n"
            f"Статус: {ticket.status}"
        )
        
        keyboard = InlineKeyboardBuilder()
        keyboard.row(
            types.InlineKeyboardButton(text="< Назад", callback_data="back_to_tickets")
        )
        
        await callback_query.message.edit_text(message_text, reply_markup=keyboard.as_markup(), parse_mode="Markdown")

@dp.callback_query(F.data == 'back_to_tickets')
async def back_to_tickets_callback(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    page = data.get("page", 1)
    await show_tickets(callback_query.message, callback_query.from_user.id, page)

@dp.callback_query(F.data == 'my_tickets')
async def my_tickets_callback(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text("📩 *Связаться  ›  Все обращения*\n\n Здесь будут ваши обращения.", parse_mode="Markdown")

@dp.callback_query(F.data.startswith('issue_'))
async def issue_topic_callback(callback_query: types.CallbackQuery, state: FSMContext):
    topic_code = callback_query.data.split('_')[1]
    topic = TOPIC_MAP.get(topic_code, topic_code)
    message_text = (
        f"📩 *Связаться  ›  Создание обращения*\n\n"
        f"Тема: {topic}\n\n"
        f"Пришлите в ответ текст вашего обращения:"
    )
    
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        types.InlineKeyboardButton(text="< Назад", callback_data="back_to_support:contact_support:True")
    )
    
    await callback_query.message.edit_text(message_text, reply_markup=keyboard.as_markup(), parse_mode="Markdown")
    await state.update_data(topic=topic)
    await state.set_state(SupportTicketStates.waiting_for_message)

@dp.message(SupportTicketStates.waiting_for_message)
async def handle_support_message(message: types.Message, state: FSMContext):
    data = await state.get_data()
    topic = data.get("topic")
    if topic:
        db = next(get_db())
        user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
        if user:
            ticket = SupportTicket(
                user_id=user.id,
                topic=topic,
                message=message.text
            )
            db.add(ticket)
            db.commit()
            await message.answer("Ваше обращение было успешно создано.")
        await state.clear()

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
        types.InlineKeyboardButton(text="< Назад", callback_data="back_to_bonuses:get_bonuses:True")
    )
    
    await callback_query.message.edit_text(message_text, reply_markup=keyboard.as_markup(), parse_mode="Markdown")

@dp.callback_query(F.data == 'my_tickets_lotteries')
async def my_tickets_lotteries_callback(callback_query: types.CallbackQuery):
    message_text = "🎫 *Мои билеты*\n\nВсего билетов: *0*"
    
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        types.InlineKeyboardButton(text="< Назад", callback_data="back_to_bonuses:get_bonuses:True")
    )
    
    await callback_query.message.edit_text(message_text, reply_markup=keyboard.as_markup(), parse_mode="Markdown")

@dp.callback_query(F.data == 'promotions')
async def promotions_callback(callback_query: types.CallbackQuery):
    message_text = "🎁 *Акции и бонусы*\n\nВыберите нужный пункт:"
    
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        types.InlineKeyboardButton(text="< Назад", callback_data="back_to_bonuses:get_bonuses:True")
    )
    
    await callback_query.message.edit_text(message_text, reply_markup=keyboard.as_markup(), parse_mode="Markdown")

@dp.callback_query(F.data == 'referral_money')
async def referral_money_callback(callback_query: types.CallbackQuery):
    db = next(get_db())
    user = db.query(User).filter(User.telegram_id == callback_query.from_user.id).first()
    if user:
        bot_info = await bot.get_me()
        bot_username = bot_info.username
        referral_link = f"https://t.me/{bot_username}?start={user.referral_code}"
        message_text = (
            f"💸 *Деньги за друзей*\n\n"
            f"Приглашено: *{user.invited_count}*\n"
            f"Баланс: *{user.total_earned}₽*\n\n"
            f"Получай *10₽ за одного* приглашенного друга\n\n"
            f"Ссылка для друга:\n"
            f"[{referral_link}]({referral_link})"
        )
        
        keyboard = InlineKeyboardBuilder()
        keyboard.row(
            types.InlineKeyboardButton(text="Вывести средства", callback_data="withdraw_funds")
        )
        keyboard.row(
            types.InlineKeyboardButton(text="< Назад", callback_data="back_to_bonuses:get_bonuses:True")
        )
        
        await callback_query.message.edit_text(message_text, reply_markup=keyboard.as_markup(), parse_mode="Markdown")

@dp.callback_query(F.data == 'withdraw_funds')
async def withdraw_funds_callback(callback_query: types.CallbackQuery):
    await callback_query.message.edit_text("Здесь можно вывести средства.", parse_mode="Markdown")

@dp.callback_query(F.data.startswith('back_to_'))
async def universal_back_callback(callback_query: types.CallbackQuery, state: FSMContext):
    data = callback_query.data.split(':')
    function_name = data[1]
    delete_previous_message = data[2] == 'True'
    function = globals()[function_name]
    await edit_message_to_previous_state(callback_query, function, delete_previous_message)
    await state.clear()

@dp.message(F.text == "Каталог товаров 🛍️")
async def show_catalog(message: types.Message):
    await message.answer("🛒")
    photo_path = os.path.join(assets_dir, 'img', 'catalog_img.jpg')
    if os.path.exists(photo_path):
        photo = FSInputFile(photo_path)
        await message.answer_photo(photo)
    else:
        pass

@dp.message(F.text == "Пополнить баланс 💳")
async def replenish_balance_text(message: types.Message):
    await replenish_balance(message)

@dp.callback_query(F.data == 'replenish')
async def replenish_balance_callback(callback_query: types.CallbackQuery):
    await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id - 1)
    await callback_query.message.delete()
    await replenish_balance(callback_query.message)

async def replenish_balance(message: types.Message):
    await message.answer("💸")
    
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        types.InlineKeyboardButton(text="250₽", callback_data="replenish_250"),
        types.InlineKeyboardButton(text="500₽", callback_data="replenish_500"),
        types.InlineKeyboardButton(text="1000₽", callback_data="replenish_1000"),
        types.InlineKeyboardButton(text="2000₽", callback_data="replenish_2000")
    )
    keyboard.row(
        types.InlineKeyboardButton(text="3000₽", callback_data="replenish_3000"),
        types.InlineKeyboardButton(text="4000₽", callback_data="replenish_4000"),
        types.InlineKeyboardButton(text="5000₽", callback_data="replenish_5000")
    )
    keyboard.row(
        types.InlineKeyboardButton(text="10000₽", callback_data="replenish_10000"),
        types.InlineKeyboardButton(text="15000₽", callback_data="replenish_15000"),
        types.InlineKeyboardButton(text="20000₽", callback_data="replenish_20000")
    )
    keyboard.row(
        types.InlineKeyboardButton(text="⬇️ Другая сумма ⬇️", callback_data="replenish_other")
    )
    
    await message.answer("💳 Пополнение баланса", reply_markup=keyboard.as_markup())

@dp.callback_query(F.data == 'replenish_other')
async def replenish_other_callback(callback_query: types.CallbackQuery):
    await callback_query.answer("♻️ Теперь укажите в сообщении сумму, на которую хотите пополнить баланс и отправьте боту", show_alert=True)