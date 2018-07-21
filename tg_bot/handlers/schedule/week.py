# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime
from random import choice

from telebot.apihelper import ApiException
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

import tg_bot.functions as func
from tg_bot import bot
from app.constants import server_timedelta, emoji, week_day_number, \
    week_day_titles, loading_text


# Week schedule message
@bot.message_handler(func=lambda mess: mess.text.capitalize() == "Неделя",
                     content_types=["text"])
def calendar_handler(message):
    bot.send_chat_action(message.chat.id, "typing")
    answer = "Выбери день:"
    week_day_calendar = InlineKeyboardMarkup()
    week_day_calendar.row(
        *[InlineKeyboardButton(text=name, callback_data=name) for
          name in week_day_number.keys()])
    week_day_calendar.row(
        *[InlineKeyboardButton(text=name, callback_data=name) for
          name in ["Вся неделя"]])
    bot.send_message(message.chat.id, answer, reply_markup=week_day_calendar)


# Week schedule callback
@bot.callback_query_handler(func=lambda call_back:
                            call_back.data in week_day_number.keys() or
                            call_back.data == "Вся неделя")
def select_week_day_schedule_handler(call_back):
    day = ""
    if call_back.data == "Вся неделя":
        day += "Неделя"
    else:
        day += [item[0] for item in week_day_titles.items() if
                item[1] == call_back.data][0]
    answer = "Расписание на: <i>{0}</i>\n".format(day)
    week_type_keyboard = InlineKeyboardMarkup()
    week_type_keyboard.row(
        *[InlineKeyboardButton(text=name, callback_data=name) for
          name in ["Текущее", "Следующее"]]
    )
    bot.edit_message_text(text=answer,
                          chat_id=call_back.message.chat.id,
                          message_id=call_back.message.message_id,
                          parse_mode="HTML",
                          reply_markup=week_type_keyboard)


# All week schedule callback
@bot.callback_query_handler(func=lambda call_back:
                            "Расписание на: Неделя" in call_back.message.text)
def all_week_schedule_handler(call_back):
    user_id = call_back.message.chat.id
    bot_msg = bot.edit_message_text(
        text="{0}\U00002026".format(choice(loading_text["schedule"])),
        chat_id=call_back.message.chat.id,
        message_id=call_back.message.message_id
    )
    if call_back.data == "Текущее":
        json_week = func.get_json_week_data(user_id)
    else:
        json_week = func.get_json_week_data(user_id, next_week=True)
    inline_answer = json_week["WeekDisplayText"]
    bot.answer_callback_query(call_back.id, inline_answer, cache_time=1)
    is_send = False
    if len(json_week["Days"]):
        for day in json_week["Days"]:
            full_place = func.is_full_place(call_back.message.chat.id)
            answer = func.create_schedule_answer(day, full_place,
                                                 call_back.message.chat.id)
            if "Выходной" in answer:
                continue
            if json_week["Days"].index(day) == 0 or not is_send:
                try:
                    bot.edit_message_text(text=answer,
                                          chat_id=user_id,
                                          message_id=bot_msg.message_id,
                                          parse_mode="HTML")
                except ApiException:
                    func.send_long_message(bot, answer, user_id)
            else:
                func.send_long_message(bot, answer, user_id)
            is_send = True
    if not is_send or not len(json_week["Days"]):
        answer = "{0} Выходная неделя".format(emoji["sleep"])
        bot.edit_message_text(text=answer,
                              chat_id=user_id,
                              message_id=bot_msg.message_id)


# Week type callback
@bot.callback_query_handler(func=lambda call_back:
                            call_back.data == "Текущее" or
                            call_back.data == "Следующее")
def week_day_schedule_handler(call_back):
    bot_msg = bot.edit_message_text(
        text="{0}\U00002026".format(choice(loading_text["schedule"])),
        chat_id=call_back.message.chat.id,
        message_id=call_back.message.message_id
    )
    is_next_week = False
    iso_day_date = list((datetime.today() + server_timedelta).isocalendar())
    if iso_day_date[2] == 7:
        iso_day_date[1] += 1
    if call_back.data == "Следующее":
        iso_day_date[1] += 1
        is_next_week = True
    iso_day_date[2] = week_day_number[
        week_day_titles[call_back.message.text.split(": ")[-1]]]
    day_date = func.date_from_iso(iso_day_date)
    json_day = func.get_json_day_data(call_back.message.chat.id, day_date,
                                      next_week=is_next_week)
    full_place = func.is_full_place(call_back.message.chat.id)
    answer = func.create_schedule_answer(json_day, full_place,
                                         call_back.message.chat.id)
    try:
        bot.edit_message_text(text=answer,
                              chat_id=call_back.message.chat.id,
                              message_id=bot_msg.message_id,
                              parse_mode="HTML")
    except ApiException:
        func.send_long_message(bot, answer, call_back.message.chat.id)
