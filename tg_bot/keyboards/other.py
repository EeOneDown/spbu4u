# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


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


def check_spbu_status():
    """
    Create keyboard with button with url

    :return: keyboard
    :rtype: InlineKeyboardMarkup
    """
    return InlineKeyboardMarkup().row(
        InlineKeyboardButton(
            text="Проверить сайт",
            url="https://timetable.spbu.ru"
        )
    )
