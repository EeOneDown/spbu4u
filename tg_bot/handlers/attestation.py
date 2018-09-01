# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from random import choice

from flask import g

from telebot.apihelper import ApiException
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from tg_bot import bot, functions as func
from tg_bot.keyboards import att_months_keyboard
from app.constants import loading_text
import telebot_login


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

    json_attestation = func.get_json_attestation(call_back.message.chat.id)
    answers = []
    is_full_place = func.is_full_place(call_back.message.chat.id)

    if call_back.message.text == "Выбери месяц:":
        schedule_variations = [(True, True, False), (False, True, False)]
    else:
        schedule_variations = [(True, False, True), (False, False, True)]

    for personal, session, only_resit in schedule_variations:
        answers = func.create_session_answers(json_attestation, call_back.data,
                                              call_back.message.chat.id,
                                              is_full_place, personal,
                                              session, only_resit)
        if answers:
            break
    if not answers:
        answers.append("<i>Нет событий</i>")
    try:
        bot.edit_message_text(text=answers[0],
                              chat_id=call_back.message.chat.id,
                              message_id=bot_msg.message_id,
                              parse_mode="HTML")
    except ApiException:
        func.send_long_message(bot, answers[0], call_back.message.chat.id)
    finally:
        for answer in answers[1:]:
            func.send_long_message(bot, answer, call_back.message.chat.id)
