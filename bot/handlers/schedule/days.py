# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime, timedelta

import bot.functions as func
from bot import bot
from bot.constants import server_timedelta, week_day_titles


# Today schedule message
@bot.message_handler(func=lambda mess: mess.text.capitalize() == "Сегодня",
                     content_types=["text"])
def today_schedule_handler(message):
    bot.send_chat_action(message.chat.id, "typing")
    today_moscow_datetime = datetime.today() + server_timedelta
    today_moscow_date = today_moscow_datetime.date()
    json_day = func.get_json_day_data(message.chat.id, today_moscow_date)
    full_place = func.is_full_place(message.chat.id)
    answer = func.create_schedule_answer(json_day, full_place, message.chat.id)
    func.send_long_message(bot, answer, message.chat.id)


# Tomorrow schedule message
@bot.message_handler(func=lambda mess: mess.text.capitalize() == "Завтра",
                     content_types=["text"])
def tomorrow_schedule_handler(message):
    bot.send_chat_action(message.chat.id, "typing")
    tomorrow_moscow_datetime = datetime.today() + server_timedelta + \
        timedelta(days=1)
    tomorrow_moscow_date = tomorrow_moscow_datetime.date()
    json_day = func.get_json_day_data(message.chat.id, tomorrow_moscow_date)
    full_place = func.is_full_place(message.chat.id)
    answer = func.create_schedule_answer(json_day, full_place, message.chat.id)
    func.send_long_message(bot, answer, message.chat.id)


# Now lesson message
@bot.message_handler(func=lambda mess: mess.text.title() == "Сейчас",
                     content_types=["text"])
@bot.message_handler(func=lambda mess:
                     mess.text.capitalize() == "Что сейчас?",
                     content_types=["text"])
def now_lesson_handler(message):
    answer = "Наверно, какая-то пара #пасхалочка"
    func.send_long_message(bot, answer, message.chat.id)


# Schedule for date message
@bot.message_handler(func=lambda mess: func.text_to_date(mess.text.lower()),
                     content_types=["text"])
def schedule_for_day(message):
    bot.send_chat_action(message.chat.id, "typing")
    day = func.text_to_date(message.text.lower())
    json_week = func.get_json_week_data(message.chat.id, for_day=day)
    json_day = func.get_json_day_data(message.chat.id, day_date=day,
                                      json_week_data=json_week)
    full_place = func.is_full_place(message.chat.id)
    answer = func.create_schedule_answer(json_day, full_place,
                                         user_id=message.chat.id,
                                         personal=True)
    func.send_long_message(bot, answer, message.chat.id)


# Schedule for week title message
@bot.message_handler(func=lambda mess:
                     mess.text.title() in week_day_titles.keys(),
                     content_types=["text"])
@bot.message_handler(func=lambda mess:
                     mess.text.title() in week_day_titles.values(),
                     content_types=["text"])
def schedule_for_weekday(message):
    bot.send_chat_action(message.chat.id, "typing")
    message.text = message.text.title()
    if message.text in week_day_titles.values():
        week_day = message.text
    else:
        week_day = week_day_titles[message.text]

    day_date = func.get_day_date_by_weekday_title(week_day)
    json_day = func.get_json_day_data(message.chat.id, day_date)
    full_place = func.is_full_place(message.chat.id)
    answer = func.create_schedule_answer(json_day, full_place,
                                         message.chat.id)
    func.send_long_message(bot, answer, message.chat.id)
