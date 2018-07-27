# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from flask import g

import telebot_login
from app import db
from app.constants import place_editor_answer
from tg_bot import bot
from tg_bot.keyboards import place_keyboard


# Place message
@bot.message_handler(
    func=lambda mess: mess.text.title() == "Адрес",
    content_types=["text"]
)
@telebot_login.login_required_message
def place_handler(message):
    user = g.current_tbot_user

    bot.send_chat_action(user.tg_id, "typing")

    bot.send_message(
        chat_id=user.tg_id,
        text=place_editor_answer.format(
            "Полностью" if user.is_full_place else "Только аудитория"
        ),
        parse_mode="HTML",
        reply_markup=place_keyboard
    )


# Full place callback
@bot.callback_query_handler(
    func=lambda call_back: call_back.data == "Полностью"
)
# Classroom callback
@bot.callback_query_handler(
    func=lambda call_back: call_back.data == "Аудитория"
)
@telebot_login.login_required_callback
def full_place_on_handler(call_back):
    user = g.current_tbot_user

    user.is_full_place = call_back.data == "Полностью"

    db.session.commit()

    bot.edit_message_text(
        text=user.get_place_edited_answer(),
        chat_id=user.tg_id,
        message_id=call_back.message.message_id,
        parse_mode="HTML"
    )
