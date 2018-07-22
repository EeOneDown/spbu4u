# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from random import choice

from flask import g
from telebot.apihelper import ApiException
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

import telebot_login
import tg_bot.functions as func
from app import new_functions as nf
from app.constants import week_day_number, week_day_titles, loading_text
from tg_bot import bot


# Week schedule message
@bot.message_handler(func=lambda mess: mess.text.capitalize() == "Неделя",
                     content_types=["text"])
@telebot_login.login_required
def calendar_handler(message):
    user = g.current_tbot_user

    bot.send_chat_action(user.tg_id, "typing")

    answer = "Выбери день:"

    week_day_calendar = InlineKeyboardMarkup()
    week_day_calendar.row(
        *[InlineKeyboardButton(text=name, callback_data=name) for
          name in week_day_number.keys()])
    week_day_calendar.row(
        *[InlineKeyboardButton(text=name, callback_data=name) for
          name in ["Вся неделя"]])

    bot.send_message(user.tg_id, answer, reply_markup=week_day_calendar)


# Week schedule callback
@bot.callback_query_handler(func=lambda call_back:
                            call_back.data in week_day_number.keys() or
                            call_back.data == "Вся неделя")
@telebot_login.login_required_callback
def select_week_day_schedule_handler(call_back):
    user = g.current_tbot_user

    if call_back.data == "Вся неделя":
        day = "Неделя"
    else:
        day = nf.get_key_by_value(week_day_titles, call_back.data)

    answer = "Расписание на: <i>{0}</i>\n".format(day)

    week_type_keyboard = InlineKeyboardMarkup()
    week_type_keyboard.row(
        *[InlineKeyboardButton(text=name, callback_data=name) for
          name in ["Текущее", "Следующее"]]
    )

    bot.edit_message_text(text=answer,
                          chat_id=user.tg_id,
                          message_id=call_back.message.message_id,
                          parse_mode="HTML",
                          reply_markup=week_type_keyboard)


# All week schedule callback
@bot.callback_query_handler(func=lambda call_back:
                            "Расписание на: Неделя" in call_back.message.text)
@telebot_login.login_required_callback
def all_week_schedule_handler(call_back):
    user = g.current_tbot_user

    bot_msg = bot.edit_message_text(
        text="{0}\U00002026".format(choice(loading_text["schedule"])),
        chat_id=user.tg_id,
        message_id=call_back.message.message_id
    )
    answers = user.create_answers_for_interval(
        from_date=nf.get_work_monday(
            is_next_week=call_back.data == "Следующее"
        )
    )
    try:
        bot.edit_message_text(text=answers[0],
                              chat_id=user.tg_id,
                              message_id=bot_msg.message_id,
                              parse_mode="HTML")
    except ApiException:
        func.send_long_message(bot, answers[0], user.tg_id)
    for answer in answers[1:]:
        func.send_long_message(bot, answer, user.tg_id)


# Week type callback
@bot.callback_query_handler(func=lambda call_back:
                            call_back.data == "Текущее")
@bot.callback_query_handler(func=lambda call_back:
                            call_back.data == "Следующее")
@telebot_login.login_required_callback
def week_day_schedule_handler(call_back):
    user = g.current_tbot_user

    bot_msg = bot.edit_message_text(
        text="{0}\U00002026".format(choice(loading_text["schedule"])),
        chat_id=user.tg_id,
        message_id=call_back.message.message_id
    )
    answer = user.create_answer_for_date(
        nf.get_date_by_weekday_title(
            title=call_back.message.text.split(": ")[-1],
            is_next_week=call_back.data == "Следующее"
        )
    )
    try:
        bot.edit_message_text(text=answer,
                              chat_id=user.tg_id,
                              message_id=bot_msg.message_id,
                              parse_mode="HTML")
    except ApiException:
        func.send_long_message(bot, answer, user.tg_id)
