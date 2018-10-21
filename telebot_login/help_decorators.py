from functools import wraps

import spbu
from flask import g
from requests import ConnectTimeout, ReadTimeout

from app.constants import (
    access_denied_answer, read_timeout_answer, connect_timeout_answer,
    spbu_api_exception_answer
)
from tg_bot import bot
from tg_bot.keyboards import link_button


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


def access_denied_inline(func):
    @wraps(func)
    def wrapper(inline_query):
        bot.answer_inline_query(
            inline_query_id=inline_query.id,
            results=[],
            switch_pm_text=access_denied_answer,
            switch_pm_parameter="access_denied_inline",
            cache_time=1,
            is_personal=True
        )
    return wrapper


def expected_failure_spbu_message(func):
    @wraps(func)
    def wrapper(message):
        was_error, answer = False, "None"
        try:
            func(message)
        except ConnectTimeout:
            was_error, answer = True, connect_timeout_answer
        except ReadTimeout:
            was_error, answer = True, read_timeout_answer
        except spbu.ApiException:
            was_error, answer = True, spbu_api_exception_answer
        finally:
            if was_error:
                if g.current_tbot_user:
                    link = g.current_tbot_user.get_current_tt_link()
                else:
                    link = None
                bot.send_message(
                    chat_id=message.chat.id,
                    text=answer,
                    reply_markup=link_button(link=link),
                    parse_mode="HTML"
                )
    return wrapper


def expected_failure_spbu_callback(func):
    @wraps(func)
    def wrapper(call_back):
        was_error, answer = False, "None"
        try:
            func(call_back)
        except ConnectTimeout:
            was_error, answer = True, connect_timeout_answer
        except ReadTimeout:
            was_error, answer = True, read_timeout_answer
        except spbu.ApiException:
            was_error, answer = True, spbu_api_exception_answer
        finally:
            if was_error:
                if g.current_tbot_user:
                    link = g.current_tbot_user.get_current_tt_link()
                else:
                    link = None
                bot.edit_message_text(
                    text=connect_timeout_answer,
                    chat_id=call_back.message.chat.id,
                    message_id=call_back.message.message_id,
                    parse_mode="HTML",
                    reply_markup=link_button(link=link)
                )
    return wrapper


def expected_failure_spbu_inline(func):
    @wraps(func)
    def wrapper(inline_query):
        try:
            func(inline_query)
        except ConnectTimeout:
            pass
        except ReadTimeout:
            pass
        except spbu.ApiException:
            pass
    return wrapper
