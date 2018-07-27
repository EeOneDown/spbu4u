# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import spbu

from telebot.types import (
    InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
)
from datetime import date
from app.constants import emoji, all_stations, max_inline_button_text_len


def place_keyboard(is_full_place):
    """
    Creates place keyboard

    :param is_full_place: user's current `is_full_place` value
    :type is_full_place: bool
    :return: place keyboard
    :rtype: InlineKeyboardMarkup
    """
    inline_keyboard = InlineKeyboardMarkup()

    if is_full_place:
        buttons = [InlineKeyboardButton(text=name, callback_data="Аудитория")
                   for name in ["Только аудитория"]]
    else:
        buttons = [InlineKeyboardButton(text=name, callback_data=name)
                   for name in ["Полностью"]]
    inline_keyboard.row(*buttons)

    return inline_keyboard
