from functools import wraps

from flask import g

from app.constants import (
    ask_to_register_answer, student_required_answer, educator_required_answer
)
from app.models import User
from tg_bot import bot


def login_required_message(func):
    @wraps(func)
    def wrapper(message):
        user = User.query.filter_by(tg_id=message.chat.id).first()
        if user:
            g.current_tbot_user = user
            func(message)
        else:
            bot.reply_to(message, ask_to_register_answer)
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
                text=ask_to_register_answer,
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
                switch_pm_text=ask_to_register_answer,
                switch_pm_parameter="new_from_inline",
                cache_time=1,
                is_personal=True
            )
    return wrapper


def student_required_message(func):
    @wraps(func)
    def wrapper(message):
        if not g.current_tbot_user.is_educator:
            func(message)
        else:
            bot.reply_to(message, student_required_answer)
    return wrapper


def student_required_callback(func):
    @wraps(func)
    def wrapper(call_back):
        if not g.current_tbot_user.is_educator:
            func(call_back)
        else:
            bot.edit_message_text(
                text=student_required_answer,
                chat_id=g.current_tbot_user.tg_id,
                message_id=call_back.message.message_id,
                parse_mode="HTML"
            )
    return wrapper


def student_required_inline(func):
    @wraps(func)
    def wrapper(inline_query):
        if not g.current_tbot_user.is_educator:
            func(inline_query)
        else:
            bot.answer_inline_query(
                inline_query_id=inline_query.id,
                results=[],
                switch_pm_text=student_required_answer,
                switch_pm_parameter="educator_from_inline",
                cache_time=10,
                is_personal=True
            )
    return wrapper


def educator_required_message(func):
    @wraps(func)
    def wrapper(message):
        if g.current_tbot_user.is_educator:
            func(message)
        else:
            bot.reply_to(message, educator_required_answer)
    return wrapper


def educator_required_callback(func):
    @wraps(func)
    def wrapper(call_back):
        if g.current_tbot_user.is_educator:
            func(call_back)
        else:
            bot.edit_message_text(
                text=educator_required_answer,
                chat_id=g.current_tbot_user.tg_id,
                message_id=call_back.message.message_id,
                parse_mode="HTML"
            )
    return wrapper


def educator_required_inline(func):
    @wraps(func)
    def wrapper(inline_query):
        if g.current_tbot_user.is_educator:
            func(inline_query)
        else:
            bot.answer_inline_query(
                inline_query_id=inline_query.id,
                results=[],
                switch_pm_text=educator_required_answer,
                switch_pm_parameter="student_from_inline",
                cache_time=10,
                is_personal=True
            )
    return wrapper


from telebot_login import help_decorators
