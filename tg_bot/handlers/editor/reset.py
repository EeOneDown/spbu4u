# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from flask import g

import telebot_login
from app import db
from app.constants import (
    ask_to_reset_answer, reset_all_lessons_answer, ask_to_select_lesson_answer,
    reset_lesson_answer, full_reset_answer, reset_all_educators_answer,
    ask_to_select_edu_answer, reset_educator_answer
)
from tg_bot import bot
from tg_bot.keyboards import (
    reset_keyboard, hidden_lessons_keyboard, chosen_educators_keyboard
)


# Return message
@bot.message_handler(
    func=lambda mess: mess.text.title() == "Вернуть",
    content_types=["text"]
)
@telebot_login.login_required_message
@telebot_login.student_required_message
def chose_to_return(message):
    user = g.current_tbot_user

    bot.send_message(
        chat_id=user.tg_id,
        text=ask_to_reset_answer,
        reply_markup=reset_keyboard()
    )


# Choose `lesson` callback
@bot.callback_query_handler(
    func=lambda call_back: call_back.data == "Занятия"
)
# Choose `educator` callback
@bot.callback_query_handler(
    func=lambda call_back: call_back.data == "Преподавателей"
)
@telebot_login.login_required_callback
@telebot_login.student_required_callback
def return_lesson(call_back):
    user = g.current_tbot_user

    if call_back.data == "Занятия":
        answer = user.create_lessons_reset_answer()
        keyboard = hidden_lessons_keyboard(answer)
    else:
        answer = user.create_educators_reset_answer()
        keyboard = chosen_educators_keyboard(answer)

    bot.edit_message_text(
        text=answer,
        chat_id=user.tg_id,
        message_id=call_back.message.message_id,
        parse_mode="HTML",
        reply_markup=keyboard
    )


# Return all lessons callback
@bot.callback_query_handler(
    func=lambda call_back: call_back.data == "Вернуть всё"
)
# Return all educators callback
@bot.callback_query_handler(
    func=lambda call_back: call_back.data == "Вернуть всех"
)
# Return everything callback
@bot.callback_query_handler(
    func=lambda call_back: call_back.data == "Полный сброс"
)
@telebot_login.login_required_callback
@telebot_login.student_required_callback
def return_all_lessons(call_back):
    user = g.current_tbot_user

    if call_back.data == "Вернуть всё":
        user.clear_hidden_lessons()
        answer = reset_all_lessons_answer
    elif call_back.data == "Вернуть всех":
        user.clear_chosen_educators()
        answer = reset_all_educators_answer
    else:
        user.clear_hidden_lessons()
        user.clear_chosen_educators()
        answer = full_reset_answer

    db.session.commit()

    bot.edit_message_text(
        text=answer,
        chat_id=user.tg_id,
        message_id=call_back.message.message_id
    )


# Choose lesson callback
@bot.callback_query_handler(
    func=lambda call_back: ask_to_select_lesson_answer in call_back.message.text
)
# Return educator callback
@bot.callback_query_handler(
    func=lambda call_back: ask_to_select_edu_answer in call_back.message.text
)
@telebot_login.login_required_callback
@telebot_login.student_required_callback
def return_lesson_handler(call_back):
    user = g.current_tbot_user

    if ask_to_select_lesson_answer in call_back.message.text:
        sql_request = user.hidden_lessons
        answer = reset_lesson_answer
    else:
        sql_request = user.chosen_educators
        answer = reset_educator_answer

    lesson = sql_request.filter_by(id=int(call_back.data)).first()

    sql_request.remove(lesson)

    db.session.commit()

    bot.edit_message_text(
        text=answer.format(call_back.data),
        chat_id=user.tg_id,
        message_id=call_back.message.message_id,
        parse_mode="HTML"
    )
