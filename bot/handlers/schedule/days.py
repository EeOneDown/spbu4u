# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime, timedelta

import bot.functions as func
from bot import bot
from bot.constants import server_timedelta, week_day_titles, emoji


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


# Schedule for interval message
@bot.message_handler(func=lambda mess: func.text_to_interval(mess.text.lower()),
                     content_types=["text"])
def schedule_for_interval(message):
    bot.send_chat_action(message.chat.id, "typing")
    from_date, to_date = func.text_to_interval(message.text.lower())
    json_data = func.get_json_interval_data(message.chat.id,
                                            from_date=from_date,
                                            to_date=to_date + timedelta(days=1))
    is_send = False
    full_place = func.is_full_place(message.chat.id)
    if len(json_data["Days"]) > 10:
        answer = "{0} Превышен интервал в <b>10 дней</b>".format(
            emoji["warning"]
        )
        bot.send_message(text=answer, chat_id=message.chat.id,
                         parse_mode="HTML")
        return
    elif len(json_data["Days"]):
        for day_info in json_data["Days"]:
            answer = func.create_schedule_answer(day_info, full_place,
                                                 message.chat.id)
            if "Выходной" in answer:
                continue
            func.send_long_message(bot, answer, message.chat.id)
            is_send = True

    if not is_send or not len(json_data["Days"]):
        answer = "{0} С <i>{1}</i> по <i>{2}</i> занятий нет".format(
            emoji["sleep"], func.datetime_to_string(from_date),
            func.datetime_to_string(to_date)
        )
        bot.send_message(text=answer, chat_id=message.chat.id,
                         parse_mode="HTML")
