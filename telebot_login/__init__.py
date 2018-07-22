# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from functools import wraps

from flask import g

from app.constants import ask_register_answer
from app.models import User
from tg_bot import bot


def login_required(func):
    @wraps(func)
    def wrapper(message):
        user = User.query.filter_by(tg_id=message.chat.id).first()
        if user:
            g.current_tbot_user = user
            func(message)
        else:
            bot.reply_to(message, ask_register_answer)
    return wrapper


def login_required_callback(func):
    @wraps(func)
    def wrapped(call_back):
        user = User.query.filter_by(tg_id=call_back.message.chat.id).first()
        if user:
            g.current_tbot_user = user
            func(call_back)
        else:
            bot.edit_message_text(text=ask_register_answer,
                                  chat_id=call_back.message.chat.id,
                                  message_id=call_back.message.message_id,
                                  parse_mode="HTML")
    return wrapped
