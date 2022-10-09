from datetime import date

from telebot.types import (
    ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
)

from app.constants import emoji


def main_keyboard():
    """
    Creates main menu keyboard

    :return: main menu keyboard
    :rtype: ReplyKeyboardMarkup
    """
    keyboard = ReplyKeyboardMarkup(
        resize_keyboard=True, one_time_keyboard=False
    )
    keyboard.row(
        "Допса" if date.today().month in [2, 9] else "Сессия", "Расписание"
    )
    return keyboard.row(
        emoji["info"], emoji["star"], emoji["settings"], emoji["suburban"],
        emoji["editor"]
    )


def schedule_keyboard():
    """
    Creates schedule menu keyboard

    :return: schedule menu keyboard
    :rtype: ReplyKeyboardMarkup
    """
    return ReplyKeyboardMarkup(
        resize_keyboard=True, one_time_keyboard=False
    ).row(
        "Сегодня", "Завтра", "Неделя"
    ).row(
        emoji["back"], emoji["bust_in_silhouette"],
        emoji["arrows_counterclockwise"], emoji["alarm_clock"]
    )


def settings_keyboard():
    """
    Creates settings menu keyboard

    :return: settings menu keyboard
    :rtype: ReplyKeyboardMarkup
    """
    return ReplyKeyboardMarkup(
        resize_keyboard=True, one_time_keyboard=False
    ).row(
        "Перезайти", "Завершить"
    ).row(
        "Назад", "Поддержка"
    )


def suburban_keyboard():
    """
    Creates suburbans menu keyboard

    :return: suburbans menu keyboard
    :rtype: ReplyKeyboardMarkup
    """
    return ReplyKeyboardMarkup(
        resize_keyboard=True, one_time_keyboard=False
    ).row(
        "Домой", "В Универ", "Маршрут"
    ).row(
        "Назад", "Персонализация"
    )


def schedule_editor_keyboard():
    """
    Creates editor keyboard

    :return: editor menu keyboard
    :rtype: ReplyKeyboardMarkup
    """
    return ReplyKeyboardMarkup(
        resize_keyboard=True, one_time_keyboard=False
    ).row(
        "Скрыть", "Выбрать", "Вернуть"
    ).row(
        "Назад", "Адрес"
    )


def rate_keyboard(rate):
    """
    Creates rate keyboard

    :param rate: user's rate
    :type rate: int
    :return: rate keyboard
    :rtype: InlineKeyboardMarkup
    """
    inline_keyboard = InlineKeyboardMarkup(row_width=5)
    inline_keyboard.add(
        *[InlineKeyboardButton(
            text=emoji["star2"] if rate < count_of_stars else emoji["star"],
            callback_data=str(count_of_stars)
        ) for count_of_stars in (1, 2, 3, 4, 5)]
    )
    inline_keyboard.add(
        *[InlineKeyboardButton(text=name, callback_data=name)
          for name in ["Отзыв", "Статистика"]]
    )
    return inline_keyboard
