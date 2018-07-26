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
    def wrapper(call_back):
        user = User.query.filter_by(tg_id=call_back.message.chat.id).first()
        if user:
            g.current_tbot_user = user
            func(call_back)
        else:
            bot.edit_message_text(
                text=ask_register_answer,
                chat_id=call_back.message.chat.id,
                message_id=call_back.message.message_id,
                parse_mode="HTML"
            )
    return wrapper


def login_required_inline(func):
    @wraps(func)
    def wrapper(inline_query):
        user = User.query.filter_by(tg_id=inline_query.from_user.id).first()
        if user:
            g.current_tbot_user = user
            func(inline_query)
        else:
            bot.answer_inline_query(
                inline_query_id=inline_query.id,
                results=[],
                switch_pm_text=ask_register_answer,
                switch_pm_parameter="new_from_inline",
                cache_time=1,
                is_personal=True
            )
    return wrapper
