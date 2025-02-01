from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Создаем клавиатуру с кнопками команд
commands_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="/status")],   # Первая строка
    ],
    resize_keyboard=True,  # Кнопки подстраиваются под размер экрана
    one_time_keyboard=True  # Кнопки не исчезают после нажатия
)