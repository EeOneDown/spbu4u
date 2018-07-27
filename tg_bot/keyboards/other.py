# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import spbu

from telebot.types import (
    InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
)
from datetime import date
from app.constants import emoji, all_stations, max_inline_button_text_len


def special_thanks_keyboard():
    """
    Creates special thanks keyboard

    :return: special thanks keyboard
    :rtype: InlineKeyboardMarkup
    """
    inline_keyboard = InlineKeyboardMarkup()
    inline_keyboard.row(
        *[InlineKeyboardButton(text=name, callback_data=name)
          for name in ["Благодарности"]]
    )
    return inline_keyboard
