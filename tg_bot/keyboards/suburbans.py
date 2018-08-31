# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from app.constants import all_stations


def start_station_keyboard():
    """
    Creates start station keyboard

    :return: start station keyboard
    :rtype: InlineKeyboardMarkup
    """
    inline_keyboard = InlineKeyboardMarkup(row_width=1)
    inline_keyboard.add(
        *[InlineKeyboardButton(text=name, callback_data=name)
          for name in all_stations.keys()]
    )
    inline_keyboard.row(
        *[InlineKeyboardButton(text=name, callback_data=name)
          for name in ["Домой", "В Универ"]]
    )
    return inline_keyboard


def end_station_keyboard(chosen_station):
    """
    Creates end station inline keyboard

    :param chosen_station: chosen station title
    :type chosen_station: str
    :return: inline keyboard
    :rtype: InlineKeyboardMarkup
    """
    inline_keyboard = InlineKeyboardMarkup(row_width=1)
    inline_keyboard.add(
        *[InlineKeyboardButton(text=name, callback_data=name)
          for name in all_stations.keys() if name != chosen_station]
    )
    inline_keyboard.row(
        *[InlineKeyboardButton(text=name, callback_data=name)
          for name in ["Изменить начальную"]]
    )
    return inline_keyboard


def select_day_keyboard():
    """
    Creates select day keyboard

    :return: select day keyboard
    :rtype: InlineKeyboardMarkup
    """
    return InlineKeyboardMarkup().row(
        *[InlineKeyboardButton(text=name, callback_data=name)
          for name in ["Сегодня", "Завтра"]]
    )


def update_keyboard(show_less=False, for_tomorrow=False):
    """
    Creates suburbans update keyboard

    :param show_less: is need to use nearest's buttons
    :type show_less: bool
    :param for_tomorrow: is need to use tomorrow's buttons
    :type for_tomorrow: bool
    :return: suburbans update keyboard
    :rtype: InlineKeyboardMarkup
    """
    if for_tomorrow:
        if show_less:
            buttons = [InlineKeyboardButton(text=name, callback_data=name)
                       for name in ["Самые ранние"]]
        else:
            buttons = [InlineKeyboardButton(text=name, callback_data=name)
                       for name in ["Все на завтра"]]
    else:
        if show_less:
            buttons = [InlineKeyboardButton(text=name, callback_data=name)
                       for name in ["Ближайшие", "Обновить"]]
        else:
            buttons = [InlineKeyboardButton(text=name, callback_data=name)
                       for name in ["Оставшиеся", "Обновить"]]

    return InlineKeyboardMarkup().row(*buttons)


def stations_keyboard():
    """
    Gets stations keyboard

    :return: stations keyboard
    :rtype: InlineKeyboardMarkup
    """
    inline_keyboard = InlineKeyboardMarkup(row_width=1)
    inline_keyboard.add(
        *[InlineKeyboardButton(text=item[0], callback_data=item[1])
          for item in all_stations.items()]
    )
    return inline_keyboard


def personalization_keyboard():
    """
    Gets personalization keyboard

    :return: personalization keyboard
    :rtype: InlineKeyboardMarkup
    """
    return InlineKeyboardMarkup().row(
        *[InlineKeyboardButton(text=name, callback_data=name)
          for name in ["Домашняя", "Университетская"]]
    )
