# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from functools import wraps

from app.constants import access_denied_answer
from tg_bot import bot


def access_denied_message(func):
    @wraps(func)
    def wrapper(message):
        bot.reply_to(message, access_denied_answer)
    return wrapper


def access_denied_callback(func):
    @wraps(func)
    def wrapper(call_back):
        bot.edit_message_text(
            text=access_denied_answer,
            chat_id=call_back.message.chat.id,
            message_id=call_back.message.message_id,
            parse_mode="HTML"
        )
    return wrapper


def login_required_inline(func):
    @wraps(func)
    def wrapper(inline_query):
        bot.answer_inline_query(
            inline_query_id=inline_query.id,
            results=[],
            switch_pm_text=access_denied_answer,
            switch_pm_parameter="new_from_inline",
            cache_time=1,
            is_personal=True
        )
    return wrapper
