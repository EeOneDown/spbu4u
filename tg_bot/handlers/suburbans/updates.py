# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from flask import g
from telebot.apihelper import ApiException
from telebot.types import InlineKeyboardMarkup

import telebot_login
from app import new_functions as nf
from app.constants import emoji
from tg_bot import bot
from tg_bot.keyboards import update_keyboard


# Update callback
@bot.callback_query_handler(
    func=lambda call_back: call_back.data == "Обновить"
)
# Remaining callback
@bot.callback_query_handler(
    func=lambda call_back: call_back.data == "Оставшиеся"
)
# Closest callback
@bot.callback_query_handler(
    func=lambda call_back: call_back.data == "Ближайшие"
)
# All for tomorrow callback
@bot.callback_query_handler(
    func=lambda call_back: call_back.data == "Все на завтра"
)
# Earliest for tomorrow callback
@bot.callback_query_handler(
    func=lambda call_back: call_back.data == "Самые ранние"
)
@telebot_login.login_required_callback
def update_yandex_handler(call_back):
    user = g.current_tbot_user

    show_more = call_back.data in ("Оставшиеся", "Все на завтра")
    for_tomorrow = call_back.data in ("Самые ранние", "Все на завтра")

    answer, is_tomorrow, is_error = nf.update_suburbans_answer(
        text=call_back.message.text,
        show_more=show_more,
        for_tomorrow=for_tomorrow
    )
    if not is_error:
        if is_tomorrow:
            inline_answer = emoji["warning"] + " На сегодня нет электричек"
            bot.answer_callback_query(
                call_back.id, inline_answer, show_alert=True
            )
        inline_keyboard = update_keyboard(
            show_less=not show_more, for_tomorrow=for_tomorrow or is_tomorrow
        )
    else:
        inline_keyboard = InlineKeyboardMarkup()

    try:
        bot.edit_message_text(text=answer,
                              chat_id=user.tg_id,
                              message_id=call_back.message.message_id,
                              parse_mode="HTML",
                              reply_markup=inline_keyboard)
    except ApiException:
        pass
    finally:
        if call_back.data == "Обновить":
            call_back.data = "Обновлено"
        inline_answer = "{0} {1}".format(emoji["check_mark"], call_back.data)

        bot.answer_callback_query(call_back.id, inline_answer, cache_time=1)
