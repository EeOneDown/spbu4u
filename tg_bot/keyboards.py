# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from telebot import types
from datetime import date
from app.constants import emoji, all_stations


def main_keyboard():
    """
    Gets main menu keyboard
    :return: main menu keyboard
    :rtype: types.ReplyKeyboardMarkup
    """
    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True, one_time_keyboard=False
    )
    if date.today().month in [12, 1, 5, 6]:
        keyboard.row("Сессия", "Расписание")
    else:
        keyboard.row("Расписание")
        keyboard.row(
            emoji["info"], emoji["star"], emoji["settings"], emoji["suburban"],
            emoji["editor"]
        )
    return keyboard


def schedule_keyboard():
    """
    Gets schedule menu keyboard
    :return: schedule menu keyboard
    :rtype: types.ReplyKeyboardMarkup
    """
    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True, one_time_keyboard=False
    )
    keyboard.row("Сегодня", "Завтра", "Неделя")
    keyboard.row(
        emoji["back"], emoji["bust_in_silhouette"],
        emoji["arrows_counterclockwise"], emoji["alarm_clock"]
    )
    return keyboard


def settings_keyboard():
    """
    Gets settings menu keyboard
    :return: settings menu keyboard
    :rtype: types.ReplyKeyboardMarkup
    """
    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True, one_time_keyboard=False
    )
    keyboard.row("Сменить группу", "Завершить")
    keyboard.row("Назад", "Поддержка")
    return keyboard


def suburban_keyboard():
    """
    Gets suburbans menu keyboard
    :return: suburbans menu keyboard
    :rtype: types.ReplyKeyboardMarkup
    """
    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True, one_time_keyboard=False
    )
    keyboard.row("Домой", "В Универ", "Маршрут")
    keyboard.row("Назад", "Персонализация")
    return keyboard


def schedule_editor_keyboard():
    """
    Gets editor keyboard
    :return: editor menu keyboard
    :rtype: types.ReplyKeyboardMarkup
    """
    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True, one_time_keyboard=False
    )
    keyboard.row("Скрыть", "Выбрать", "Вернуть")
    keyboard.row("Назад", "Адрес")
    return keyboard


def start_station_keyboard():
    """
    Gets start station keyboard
    :return: start station keyboard
    :rtype: types.InlineKeyboardMarkup
    """
    inline_keyboard = types.InlineKeyboardMarkup(row_width=1)
    inline_keyboard.add(
        *[types.InlineKeyboardButton(text=name, callback_data=name)
          for name in all_stations.keys()]
    )
    inline_keyboard.row(
        *[types.InlineKeyboardButton(text=name, callback_data=name)
          for name in ["Домой", "В Универ"]]
    )
    return inline_keyboard


def end_station_keyboard(chosen_station):
    """
    Creates end station inline keyboard
    :param chosen_station: chosen station title
    :type chosen_station: str
    :return: inline keyboard
    :rtype: types.InlineKeyboardMarkup
    """
    inline_keyboard = types.InlineKeyboardMarkup()
    inline_keyboard.add(
        *[types.InlineKeyboardButton(text=name, callback_data=name)
          for name in all_stations.keys() if name != chosen_station]
    )
    inline_keyboard.row(
        *[types.InlineKeyboardButton(text=name, callback_data=name)
          for name in ["Изменить начальную"]]
    )
    return inline_keyboard


def select_day_keyboard():
    """
    Gets select day keyboard
    :return: select day keyboard
    :rtype: types.InlineKeyboardMarkup
    """
    inline_keyboard = types.InlineKeyboardMarkup()
    inline_keyboard.row(
        *[types.InlineKeyboardButton(text=name, callback_data=name)
          for name in ["Сегодня", "Завтра"]]
    )
    return inline_keyboard


def update_keyboard(is_tomorrow=False):
    """
    Gets suburbans update keyboard
    :param is_tomorrow:
    :return:
    """
    inline_keyboard = types.InlineKeyboardMarkup()

    if is_tomorrow:
        buttons = [types.InlineKeyboardButton(text=name, callback_data=name)
                   for name in ["Все на завтра"]]
    else:
        buttons = [types.InlineKeyboardButton(text=name, callback_data=name)
                   for name in ["Оставшиеся", "Обновить"]]

    inline_keyboard.row(*buttons)

    return inline_keyboard