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


def events_keyboard(answer):
    """

    :param answer:
    :type answer: str
    :return:
    """
    inline_keyboard = InlineKeyboardMarkup()
    events = answer.split("\n\n")[2:]
    inline_keyboard.add(
        *[InlineKeyboardButton(
            text=event.split("\n")[0].replace(
                "<b>", ""
            ).replace(
                "</b>", ""
            ).replace(
                " " + emoji["cross_mark"], ""
            )[:max_inline_button_text_len],
            callback_data=num
        )
          for num, event in enumerate(events)]
    )
    return inline_keyboard.row(
        *[InlineKeyboardButton(text=emoji[name], callback_data=name)
          for name in ["prev_block", "Отмена", "next_block"]]
    )
