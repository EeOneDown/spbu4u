# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.constants import (
    emoji, max_inline_button_text_len, subject_short_types, no_lessons_answer
)


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
    Creates events keyboard from bot's answer

    :param answer: bot's answer created by `User.get_block_answer()`
    :type answer: str
    :return: events keyboard
    :rtype: InlineKeyboardMarkup
    """
    inline_keyboard = InlineKeyboardMarkup()

    if answer == no_lessons_answer:
        return inline_keyboard

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
            callback_data=i
        )
          for i, event in enumerate(events)]
    )
    return inline_keyboard.row(
        *[InlineKeyboardButton(text=emoji[name], callback_data=name)
          for name in ["prev_block", "Отмена", "next_block"]]
    )


def types_keyboard(event_type=None):
    """
    Creates types keyboard

    :param event_type: (Optional) special event type
    :type event_type: str
    :return: types keyboard
    :rtype: InlineKeyboardMarkup
    """
    inline_keyboard = InlineKeyboardMarkup(row_width=3)

    short_types = list(subject_short_types.values())

    if event_type and event_type not in short_types:
        is_special_type = True
    else:
        is_special_type = False

    inline_keyboard.add(
        *[InlineKeyboardButton(text=name, callback_data=name)
          for name in short_types]
    )
    if is_special_type:
        inline_keyboard.row(
            *[InlineKeyboardButton(
                text=name,
                callback_data=name[:max_inline_button_text_len]
            ) for name in [event_type]]
        )
    return inline_keyboard.row(
        *[InlineKeyboardButton(text=name, callback_data=name)
          for name in ["Отмена", "Далее"]]
    )
