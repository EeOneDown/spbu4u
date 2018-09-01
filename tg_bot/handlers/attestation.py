# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from random import choice

from flask import g
from telebot.apihelper import ApiException

import telebot_login
from app import new_functions as nf
from app.constants import loading_text
from tg_bot import bot, functions as func
from tg_bot.keyboards import att_months_keyboard


# Session message
@bot.message_handler(
    func=lambda mess: mess.text.capitalize() == "Сессия",
    content_types=["text"]
)
@bot.message_handler(
    func=lambda mess: mess.text.capitalize() == "Допса",
    content_types=["text"]
)
@telebot_login.login_required_message
def attestation_handler(message):
    user = g.current_tbot_user

    bot.send_chat_action(user.tg_id, "typing")

    month = user.get_attestation_months()

    if month and message.text == "Сессия":
        answer = "Выбери месяц:"
    elif month and message.text == "Допса":
        answer = "Выбери месяц для <b>допсы</b>:"
    else:
        answer = "<i>Нет событий</i>"

    bot.send_message(
        chat_id=user.tg_id,
        text=answer,
        reply_markup=att_months_keyboard(month=month, text=message.text),
        parse_mode="HTML"
    )


# Switch callbacks
@bot.callback_query_handler(
    func=lambda call_back: call_back.data == "Допса"
)
@bot.callback_query_handler(
    func=lambda call_back: call_back.data == "Сессия"
)
@telebot_login.login_required_callback
def switch_session_type_handler(call_back):
    user = g.current_tbot_user

    bot_msg = bot.edit_message_text(
        text="{0}\U00002026".format(choice(loading_text["schedule"])),
        chat_id=call_back.message.chat.id,
        message_id=call_back.message.message_id
    )
    month = user.get_attestation_months()

    if month and call_back.data == "Сессия":
        answer = "Выбери месяц:"
    elif month and call_back.data == "Допса":
        answer = "Выбери месяц для <b>допсы</b>:"
    else:
        answer = "<i>Нет событий</i>"

    bot.edit_message_text(
        chat_id=call_back.message.chat.id,
        text=answer,
        message_id=bot_msg.message_id,
        parse_mode="HTML",
        reply_markup=att_months_keyboard(month=month, text=call_back.data)
    )


# Month callback
@bot.callback_query_handler(
    func=lambda call_back: "Выбери месяц" in call_back.message.text
)
@telebot_login.login_required_callback
def select_months_att_handler(call_back):
    user = g.current_tbot_user

    bot_msg = bot.edit_message_text(
        text="{0}\U00002026".format(choice(loading_text["schedule"])),
        chat_id=call_back.message.chat.id,
        message_id=call_back.message.message_id
    )
    answers = user.create_answers_for_interval(
        *nf.get_term_dates(),
        lessons_type="Attestation",
        is_resit=call_back.message.text != "Выбери месяц:"
    )
    try:
        bot.edit_message_text(
            text=answers[0],
            chat_id=user.tg_id,
            message_id=bot_msg.message_id,
            parse_mode="HTML"
        )
    except ApiException:
        func.send_long_message(bot, answers[0], user.tg_id)
    for answer in answers[1:]:
        func.send_long_message(bot, answer, user.tg_id)
