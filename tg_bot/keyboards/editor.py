# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.constants import emoji, max_inline_button_text_len

def place_keyboard(is_full_place):
    """
    Creates place keyboard

    :param is_full_place: user's current `is_full_place` value
    :type is_full_place: bool
    :return: place keyboard
    :rtype: InlineKeyboardMarkup
    """
    if is_full_place:
        buttons = [InlineKeyboardButton(text=name, callback_data="Аудитория")
                   for name in ["Только аудитория"]]
    else:
        buttons = [InlineKeyboardButton(text=name, callback_data=name)
                   for name in ["Полностью"]]

    return InlineKeyboardMarkup().row(*buttons)


def events_keyboard(block):
    inline_keyboard = InlineKeyboardMarkup()
    events = [event.split("\n")[0] for event in block.split("\n\n")[1:-1]]
    for event in events:
        event_name = event.strip(" " + emoji["cross_mark"])[3:-4].split(" - ")
        button_text = "{0} - {1}".format(
            event_name[0], event_name[1].split(". ")[-1])
        inline_keyboard.row(
            *[InlineKeyboardButton(
                text=name, callback_data=name[:max_inline_button_text_len]
            ) for name in [button_text]]
        )
    inline_keyboard.row(
        *[InlineKeyboardButton(text=emoji[name], callback_data=name)
          for name in ["prev_block", "Отмена", "next_block"]]
    )