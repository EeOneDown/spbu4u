from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from app import new_functions as nf
from app.constants import (
    emoji, max_inline_button_text_len, subject_short_types, no_lessons_answer,
    no_hidden_lessons_answer, no_chosen_educators_answer
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
    inline_keyboard = InlineKeyboardMarkup(row_width=1)

    if answer == no_lessons_answer:
        return inline_keyboard

    events = answer.split("\n\n")[2:-1]
    inline_keyboard.add(
        *[InlineKeyboardButton(
            text=event.split("\n")[0].replace(
                "<b>", ""
            ).replace(
                "</b>", ""
            ).replace(
                " " + emoji["cross_mark"], ""
            )[:max_inline_button_text_len],
            callback_data=str(i)
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
            ) for name in types]
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


def choose_keyboard():
    """
    Creates choose keyboard

    :return: choose keyboard
    :rtype: InlineKeyboardMarkup
    """
    return InlineKeyboardMarkup().row(
        *[InlineKeyboardButton(text=name, callback_data=name)
          for name in ["Преподавателя", "Занятие"]]
    )


def reset_keyboard():
    """
    Creates reset keyboard

    :return: reset keyboard
    :rtype: InlineKeyboardMarkup
    """
    return InlineKeyboardMarkup().row(
        *[InlineKeyboardButton(text=name, callback_data=name)
          for name in ["Преподавателей", "Занятия"]]
    ).row(
        *[InlineKeyboardButton(text=name, callback_data=name)
          for name in ["Полный сброс"]]
    )


def hidden_lessons_keyboard(text):
    """
    Creates hidden lessons keyboard

    :param text: bot's answer created by `User.create_lessons_reset_answer()`
    :type text: str
    :return: hidden lessons keyboard
    :rtype: InlineKeyboardMarkup
    """
    inline_keyboard = InlineKeyboardMarkup()

    if text == no_hidden_lessons_answer:
        return inline_keyboard

    for lesson in text.split("\n\n")[1:-1]:
        lesson_data = lesson.split("\n")

        inline_keyboard.row(
            *[InlineKeyboardButton(
                text="{0}. {1}".format(
                    lesson_data[0][7:-4], lesson_data[1][17:]
                )[:max_inline_button_text_len],
                callback_data=lesson_data[0][7:-4]
            )]
        )
    return inline_keyboard.row(
        *[InlineKeyboardButton(text=name, callback_data=name)
          for name in ["Отмена", "Вернуть всё"]]
    )


def chosen_educators_keyboard(text):
    """
    Creates chosen educators keyboard

    :param text: bot's answer created by `User.create_educators_reset_answer()`
    :type text: str
    :return: chosen educators keyboard
    :rtype: InlineKeyboardMarkup
    """
    inline_keyboard = InlineKeyboardMarkup()

    if text == no_chosen_educators_answer:
        return inline_keyboard

    for lesson in text.split("\n\n")[1:-1]:
        lesson_data = lesson.split("\n")

        inline_keyboard.row(
            *[InlineKeyboardButton(
                text="{0}. {1}".format(
                    lesson_data[0][7:-4], lesson_data[1][17:]
                )[:max_inline_button_text_len],
                callback_data=lesson_data[0][7:-4]
            )]
        )
    return inline_keyboard.row(
        *[InlineKeyboardButton(text=name, callback_data=name)
          for name in ["Отмена", "Вернуть всех"]]
    )


def selectable_blocks_keyboard(selectable_blocks_keys):
    """
    Creates selectable blocks keyboard

    :param selectable_blocks_keys: keys from `User.get_selectable_blocks()`
    :type selectable_blocks_keys: dict_keys
    :return: selectable blocks keyboard
    :rtype: InlineKeyboardMarkup
    """
    inline_keyboard = InlineKeyboardMarkup(row_width=1)
    inline_keyboard.add(
        *[InlineKeyboardButton(text=name, callback_data=name)
          for name in selectable_blocks_keys]
    )
    if selectable_blocks_keys:
        inline_keyboard.row(
            *[InlineKeyboardButton(text=name, callback_data=name)
              for name in ["Отмена"]]
        )
    return inline_keyboard


def block_lessons_keyboard(block):
    """
    Creates block lessons keyboard

    :param block: block from `User.get_selectable_blocks()`
    :return: block lessons keyboard
    :rtype: InlineKeyboardMarkup
    """
    inline_keyboard = InlineKeyboardMarkup()
    for num, event in enumerate(block):
        text = "{0}. {1}".format(
            num + 1, nf.parse_event_subject(event)[:max_inline_button_text_len]
        )
        inline_keyboard.row(
            InlineKeyboardButton(text=text, callback_data=str(num))
        )
    return inline_keyboard.row(
        InlineKeyboardButton(text="Отмена", callback_data="Отмена")
    )
