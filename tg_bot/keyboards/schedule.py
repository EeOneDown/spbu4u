from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from app.constants import emoji, week_day_number


def sending_keyboard(is_subscribed):
    """
    Gets sending keyboard

    :param is_subscribed: user's `is_subscriber` value
    :type is_subscribed: bool
    :return: sending keyboard
    :rtype: InlineKeyboardMarkup
    """
    if is_subscribed:
        buttons = [InlineKeyboardButton(text=name, callback_data="Отписаться")
                   for name in [emoji["cross_mark"] + " Отписаться"]]

    else:
        buttons = [InlineKeyboardButton(text=name, callback_data="Подписаться")
                   for name in [emoji["check_mark"] + " Подписаться"]]

    return InlineKeyboardMarkup().row(*buttons)


def status_templates_keyboard():
    """
    Gets status templates keyboard

    :return: status templates keyboard
    :rtype: InlineKeyboardMarkup
    """
    return InlineKeyboardMarkup().row(
        *[InlineKeyboardButton(text=name, callback_data=name)
          for name in ["Перезайти", "Ссылка"]]
    ).row(
        *[InlineKeyboardButton(text=name, callback_data=name)
          for name in ["Преподаватели", "Группы"]]
    )


def templates_list_keyboard(items, last_row):
    """
    Get templates list keyboard for items

    :param items:
    :type items: list
    :param last_row:
    :type: list
    :return: templates list keyboard
    :rtype: InlineKeyboardMarkup
    """
    inline_keyboard = InlineKeyboardMarkup(row_width=2)
    if items:
        inline_keyboard.add(
            *[InlineKeyboardButton(
                text=item.title, callback_data=item.id
            ) for item in items]
        )
    inline_keyboard.row(
        *[InlineKeyboardButton(text=name, callback_data=name)
          for name in last_row]
    )
    return inline_keyboard


def week_day_keyboard(for_editor=False):
    """
    Gets week day keyboard

    :param for_editor: is need to use `cancel` button instead of `all week`
    :type for_editor: bool
    :return: week day keyboard
    :rtype: InlineKeyboardMarkup
    """
    return InlineKeyboardMarkup().row(
        *[InlineKeyboardButton(text=name, callback_data=name)
          for name in week_day_number.keys()]
    ).row(
        *[InlineKeyboardButton(text=name, callback_data=name)
          for name in ["Отмена" if for_editor else "Вся неделя"]]
    )


def current_next_keyboard():
    """
    Get current next keyboard

    :return: current next keyboard
    :rtype: InlineKeyboardMarkup
    """
    return InlineKeyboardMarkup().row(
        *[InlineKeyboardButton(text=name, callback_data=name) for
          name in ["Текущее", "Следующее"]]
    )
