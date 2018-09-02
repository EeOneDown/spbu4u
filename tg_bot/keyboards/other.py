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
        *[InlineKeyboardButton(text=name, callback_data=name)
          for name in ["Благодарности"]]
    )
