# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from functools import wraps
from requests import ConnectTimeout, ReadTimeout
import spbu

from app.constants import (
    access_denied_answer, read_timeout_answer, connect_timeout_answer,
    spbu_api_exception_answer
)
from tg_bot import bot
from tg_bot.keyboards import check_spbu_status


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


def expected_failure_spbu_message(func):
    @wraps(func)
    def wrapper(message):
        try:
            func(message)
        except ConnectTimeout:
            bot.send_message(
                chat_id=message.chat.id,
                text=connect_timeout_answer,
                reply_markup=check_spbu_status()
            )
        except ReadTimeout:
            bot.send_message(
                chat_id=message.chat.id,
                text=read_timeout_answer,
                reply_markup=check_spbu_status()
            )
        except spbu.ApiException:
            bot.send_message(
                chat_id=message.chat.id,
                text=spbu_api_exception_answer,
                reply_markup=check_spbu_status()
            )
    return wrapper


def expected_failure_spbu_callback(func):
    @wraps(func)
    def wrapper(call_back):
        try:
            func(call_back)
        except ConnectTimeout:
            bot.edit_message_text(
                text=connect_timeout_answer,
                chat_id=call_back.message.chat.id,
                message_id=call_back.message.message_id,
                parse_mode="HTML",
                reply_markup=check_spbu_status()
            )
        except ReadTimeout:
            bot.edit_message_text(
                text=read_timeout_answer,
                chat_id=call_back.message.chat.id,
                message_id=call_back.message.message_id,
                parse_mode="HTML",
                reply_markup=check_spbu_status()
            )
        except spbu.ApiException:
            bot.edit_message_text(
                text=spbu_api_exception_answer,
                chat_id=call_back.message.chat.id,
                message_id=call_back.message.message_id,
                parse_mode="HTML",
                reply_markup=check_spbu_status()
            )
    return wrapper


def expected_failure_spbu_inline(func):
    @wraps(func)
    def wrapper(inline_query):
        try:
            func(inline_query)
        except Exception:
            pass
    return wrapper
