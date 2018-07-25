# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from flask import g
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

import telebot_login
from app import db
from app.constants import (
    emoji, sending_off_answer, sending_on_answer, sending_info_answer
)
from tg_bot import bot


# Schedule sending message
@bot.message_handler(
    func=lambda mess: mess.text == emoji["alarm_clock"],
    content_types=["text"]
)
@telebot_login.login_required
def sending_handler(message):
    user = g.current_tbot_user

    bot.send_chat_action(user.tg_id, "typing")

    sending_keyboard = InlineKeyboardMarkup()
    if user.is_subscribed:
        sending_keyboard.row(
            *[InlineKeyboardButton(text=name, callback_data="Отписаться")
              for name in [emoji["cross_mark"] + " Отписаться"]]
        )
    else:
        sending_keyboard.row(
            *[InlineKeyboardButton(text=name, callback_data="Подписаться")
              for name in [emoji["check_mark"] + " Подписаться"]]
        )
    bot.send_message(user.tg_id, sending_info_answer, parse_mode="HTML",
                     reply_markup=sending_keyboard)


# Subscribe/Unsubscribe for sending callback
@bot.callback_query_handler(
    func=lambda call_back: call_back.data == "Подписаться"
)
@bot.callback_query_handler(
    func=lambda call_back: call_back.data == "Отписаться"
)
@telebot_login.login_required_callback
def sending_subscribing_handler(call_back):
    user = g.current_tbot_user

    if call_back.data == "Отписаться":
        user.is_subscribed = False
        answer = sending_off_answer
    else:
        user.is_subscribed = True
        answer = sending_on_answer

    db.session.commit()

    bot.edit_message_text(text=answer,
                          chat_id=user.tg_id,
                          message_id=call_back.message.message_id,
                          parse_mode="HTML")
