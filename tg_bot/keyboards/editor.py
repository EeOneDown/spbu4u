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


def types_keyboard(types, add=False):
    """
    Creates types keyboard

    :param types: special event type
    :type types: list of str
    :param add: (Optional)
    :type add: bool
    :return: types keyboard
    :rtype: InlineKeyboardMarkup
    """
    inline_keyboard = InlineKeyboardMarkup(row_width=3)

    short_types = list(subject_short_types.values())

    inline_keyboard.add(
        *[InlineKeyboardButton(
            text=(emoji["heavy_check_mark"] if not add and st in types else ""
                  ) + st,
            callback_data=st
        ) for st in short_types]
    )
    if add and types[0] not in short_types:
        inline_keyboard.row(
            *[InlineKeyboardButton(
                text=name,
                callback_data=name[:max_inline_button_text_len]
            ) for name in [types]]
        )
    return inline_keyboard.row(
        *[InlineKeyboardButton(text=name, callback_data=name)
          for name in ["Отмена", "Далее"]]
    )


def hide_keyboard():
    """
    Creates hide keyboard

    :return: hide keyboard
    :rtype: InlineKeyboardMarkup
    """
    inline_keyboard = InlineKeyboardMarkup(row_width=2)
    inline_keyboard.add(
        *[InlineKeyboardButton(text=name, callback_data=name)
          for name in ["ЛЛЛ", "ЛЛК", "КЛЛ", "КЛК", "ККК", "ККЛ", "ЛКК", "ЛКЛ"]]
    )
    return inline_keyboard
