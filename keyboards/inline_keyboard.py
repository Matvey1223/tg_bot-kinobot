from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder




# Функция для создания автоматической клавиатуры
def create_inline_kb(width: int,
                     *args: str,
                     **kwargs: str) -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()
    # Инициализируем список для кнопок
    buttons: list[InlineKeyboardButton] = []

    # Загружаем список кнопками из аргументов args и kwargs
    if args:
        for button in args:
            buttons.append(InlineKeyboardButton(
                text=button,
                callback_data=button))
    kb_builder.row(*buttons, width=width)
    # Возвращаем объект инлайн-клавиатуры
    return kb_builder.as_markup()

def create_url_kb(width: int, text: str, url: str) -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()
    # Инициализируем список для кнопок
    buttons: list[InlineKeyboardButton] = []

    # Загружаем список кнопками из аргументов args и kwargs
    if text:
        buttons.append(InlineKeyboardButton(text=text, callback_data=text, url=url))
    kb_builder.row(*buttons, width=width)
    return kb_builder.as_markup()

def create_inline_kb_by_list(width: int, texts: list[str]) -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()
    buttons: list[InlineKeyboardButton] = []

    for button in texts:
        buttons.append(InlineKeyboardButton(
            text=button,
            callback_data=button))
    kb_builder.row(*buttons, width=width)
    return kb_builder.as_markup()