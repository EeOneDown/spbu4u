from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from app.constants import current_week_text


def special_thanks_keyboard():
    """
    Creates special thanks keyboard

    :return: special thanks keyboard
    :rtype: InlineKeyboardMarkup
    """
    return InlineKeyboardMarkup().row(
        InlineKeyboardButton(
            text="Благодарности", callback_data="Благодарности"
        )
    )


def link_button(text:str = None, link: str = None):
    """
    Create keyboard with button with url

    :param text: button text
    :type text: str
    :param link: custom link
    :type link: str

    :return: keyboard
    :rtype: InlineKeyboardMarkup
    """
    return InlineKeyboardMarkup().row(
        InlineKeyboardButton(
            text=text or "Проверить сайт",
            url=link or "https://timetable.spbu.ru"
        )
    )


def current_week_keyboard():
    """
    Creates keyboard with current_week_text

    :return: keyboard
    :rtype: InlineKeyboardMarkup
    """
    return InlineKeyboardMarkup().row(
        InlineKeyboardButton(
            text=current_week_text,
            callback_data=current_week_text
        )
    )
