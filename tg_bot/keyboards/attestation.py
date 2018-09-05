from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def att_months_keyboard(month, text):
    """
    Creates attestation months keyboard

    :param month: available months dict
    :type month: dict
    :param text: user's (or bot's) message text
    :type text: str
    :return: attestation months keyboard
    :rtype: InlineKeyboardMarkup
    """
    inline_keyboard = InlineKeyboardMarkup(row_width=1)
    for key in month.keys():
        inline_keyboard.row(
            *[InlineKeyboardButton(text=month[key], callback_data=str(key))]
        )
    return inline_keyboard.row(
        InlineKeyboardButton(
            text="Допса" if text == "Сессия" else "Сессия",
            callback_data="Допса" if text == "Сессия" else "Сессия"
        )
    )
