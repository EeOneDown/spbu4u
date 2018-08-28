# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from flask import g

import telebot_login
from app import db, new_functions as nf
from app.constants import (
    hide_answer, hide_lesson_answer, selected_lesson_answer,
    selected_lesson_info_answer, ask_to_select_types_answer, how_to_hide_answer
)
from app.models import Lesson
from tg_bot import bot
from tg_bot.keyboards import (
    week_day_keyboard, events_keyboard, types_keyboard, hide_keyboard
)


# Hide message
@bot.message_handler(
    func=lambda mess: mess.text.capitalize() == "Скрыть",
    content_types=["text"]
)
@telebot_login.login_required_message
@telebot_login.student_required_message
def hide_lesson_handler(message):
    user = g.current_tbot_user

    bot.send_chat_action(user.tg_id, "typing")

    bot.send_message(
        chat_id=user.tg_id,
        text=hide_answer,
        reply_markup=week_day_keyboard(for_editor=True)
    )


# Weekday callback
@bot.callback_query_handler(
    func=lambda call_back: call_back.message.text == hide_answer
)
@telebot_login.login_required_callback
@telebot_login.student_required_callback
def select_day_hide_lesson_handler(call_back):
    user = g.current_tbot_user

    bot_msg = bot.edit_message_text(
        text="Разбиваю занятия на пары\U00002026",
        chat_id=user.tg_id,
        message_id=call_back.message.message_id
    )
    answer = user.get_block_answer(
        for_date=nf.get_date_by_weekday_title(call_back.data),
        block_num=1
    )
    bot.edit_message_text(
        text=answer,
        chat_id=user.tg_id,
        message_id=bot_msg.message_id,
        reply_markup=events_keyboard(answer),
        parse_mode="HTML"
    )


# next_block callback
@bot.callback_query_handler(
    func=lambda call_back: call_back.data == "next_block"
)
# prev_block callback
@bot.callback_query_handler(
    func=lambda call_back: call_back.data == "prev_block"
)
@telebot_login.login_required_callback
@telebot_login.student_required_callback
def select_block_handler(call_back):
    user = g.current_tbot_user

    # read bl as block
    bl_cnt, cur_bl_n, for_date = nf.get_block_data_from_block_answer(
        call_back.message.text
    )
    if bl_cnt == 1:
        bot.answer_callback_query(
            call_back.id, "Доступна только одна пара", cache_time=2
        )
        return

    is_next_block = call_back.data == "next_block"

    bot_msg = bot.edit_message_text(
        text="Смотрю {0} пару\U00002026".format(
            "следующую" if is_next_block else "предыдущую"
        ),
        chat_id=call_back.message.chat.id,
        message_id=call_back.message.message_id
    )
    answer = user.get_block_answer(
        for_date=for_date,
        block_num=cur_bl_n + (1 if is_next_block else -1) % bl_cnt or bl_cnt
    )
    bot.edit_message_text(
        text=answer,
        chat_id=user.tg_id,
        message_id=bot_msg.message_id,
        reply_markup=events_keyboard(answer),
        parse_mode="HTML"
    )


# Lesson callback
@bot.callback_query_handler(
    func=lambda call_back: hide_lesson_answer in call_back.message.text
)
@telebot_login.login_required_callback
@telebot_login.student_required_callback
def select_lesson_handler(call_back):
    user = g.current_tbot_user

    event_data = nf.get_event_data_from_block_answer(
        text=call_back.message.text,
        idx=int(call_back.data)
    )
    bot.edit_message_text(
        text="\n\n".join([
            selected_lesson_answer,
            selected_lesson_info_answer.format(*event_data),
            ask_to_select_types_answer
        ]),
        chat_id=user.tg_id,
        message_id=call_back.message.message_id,
        parse_mode="HTML",
        reply_markup=types_keyboard(types=event_data[2], add=True)
    )


# Next callback
@bot.callback_query_handler(
    func=lambda call_back: call_back.data == "Далее"
)
@telebot_login.login_required_callback
@telebot_login.student_required_callback
def types_selected_handler(call_back):
    user = g.current_tbot_user

    bot.edit_message_text(
        text="\n\n".join([
            selected_lesson_answer,
            call_back.message.text.split("\n\n")[1],
            how_to_hide_answer
        ]),
        chat_id=user.tg_id,
        message_id=call_back.message.message_id,
        parse_mode="HTML",
        reply_markup=hide_keyboard()
    )


# Type callback
@bot.callback_query_handler(
    func=lambda call_back: ask_to_select_types_answer in call_back.message.text
)
@telebot_login.login_required_callback
@telebot_login.student_required_callback
def select_types_handler(call_back):
    user = g.current_tbot_user

    answer = nf.update_types_answer(
        text=call_back.message.text,
        new_type=call_back.data
    )
    bot.edit_message_text(
        text=answer,
        chat_id=user.tg_id,
        message_id=call_back.message.message_id,
        parse_mode="HTML",
        reply_markup=types_keyboard(
            types=answer.split("\n\n")[1].split("\n")[-1][6:].split("; ")
        )
    )


@bot.callback_query_handler(
    func=lambda callback: how_to_hide_answer in callback.message.text
)
@telebot_login.login_required_callback
@telebot_login.student_required_callback
def hide_lesson(call_back):
    user = g.current_tbot_user

    lesson = Lesson.add_or_get(
        **nf.get_lesson_data(
            data=call_back.message.text.split("\n\n")[1].split("\n"),
            hide_type=call_back.data
        )
    )
    if lesson not in user.hidden_lessons.all():
        user.hidden_lessons.append(lesson)

    db.session.commit()

    bot.edit_message_text(
        text="Занятие скрыто",
        chat_id=user.tg_id,
        message_id=call_back.message.message_id,
        parse_mode="HTML"
    )
