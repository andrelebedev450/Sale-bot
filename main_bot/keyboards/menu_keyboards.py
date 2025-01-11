from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Каталог товаров 🛍️"), KeyboardButton(text="Пополнить баланс 💳")],
        [KeyboardButton(text="Мой профиль ⁠🪪"), KeyboardButton(text="Связаться 📞")],
        [KeyboardButton(text="🎁 ПОЛУЧИ БОНУСЫ 🎁")]
    ],
    resize_keyboard=True,
    selective=True
)
