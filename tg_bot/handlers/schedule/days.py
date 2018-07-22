# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime, timedelta

from flask import g

import app.new_functions as nf
import telebot_login
import tg_bot.functions as func
from app.constants import server_timedelta, week_day_titles, emoji
from tg_bot import bot


# Today or tomorrow schedule message
@bot.message_handler(func=lambda mess: mess.text.title() == "Сегодня",
                     content_types=["text"])
@bot.message_handler(func=lambda mess: mess.text.title() == "Завтра",
                     content_types=["text"])
# Schedule for weekday title message
@bot.message_handler(func=lambda mess:
                     mess.text.title() in week_day_titles.keys(),
                     content_types=["text"])
@bot.message_handler(func=lambda mess:
                     mess.text.title() in week_day_titles.values(),
                     content_types=["text"])
# Schedule for date message
@bot.message_handler(func=lambda mess: nf.text_to_date(mess.text.lower()),
                     content_types=["text"])
@telebot_login.login_required
def day_schedule_handler(message):
    user = g.current_tbot_user

    bot.send_chat_action(message.chat.id, "typing")

    if message.text.title() == "Сегодня":
        date = datetime.today().date() + server_timedelta
    elif message.text.title() == "Завтра":
        date = datetime.today().date() + server_timedelta + timedelta(days=1)
    elif message.text.title() in week_day_titles.keys():
        date = nf.get_date_by_weekday_title(
            title=week_day_titles[message.text.title()]
        )
    elif message.text.title() in week_day_titles.values():
        date = nf.get_date_by_weekday_title(
            title=message.text.title()
        )
    else:
        date = nf.text_to_date(message.text.lower())

    answer = user.create_answer_for_date(date)

    nf.send_long_message(bot, answer, user.tg_id)


# Schedule for interval message
@bot.message_handler(func=lambda mess: nf.text_to_interval(mess.text.lower()),
                     content_types=["text"])
@telebot_login.login_required
def interval_schedule_handler(message):
    user = g.current_tbot_user

    bot.send_chat_action(user.tg_id, "typing")

    answers = user.create_answers_for_interval(
        *nf.text_to_interval(message.text.lower())
    )
    for answer in answers:
        nf.send_long_message(bot, answer, user.tg_id)


# TODO NEW FEATURE
# Current lesson message
@bot.message_handler(func=lambda mess: "Сейчас" in mess.text.title(),
                     content_types=["text"])
def current_lesson_handler(message):
    bot.send_chat_action(message.chat.id, "typing")

    today = datetime.today() + server_timedelta
    json_day = func.get_json_day_data(message.chat.id, today.date())
    full_place = func.is_full_place(message.chat.id)
    answer = func.create_schedule_answer(json_day, full_place, message.chat.id)

    if "Выходной" in answer:
        func.send_long_message(bot, answer, message.chat.id)
    else:
        lessons = answer.strip().split("\n\n")[1:]
        for lesson in lessons:
            times = []
            for st in lesson.split("\n")[0].split(" ")[-1].split(
                    emoji["en_dash"]):
                times.append(func.string_to_time(st))
            if times[0] <= today.time() <= times[1]:
                answer = "{0} <b>Пара:</b>\n{1}".format(emoji["books"], lesson)
                func.send_long_message(bot, answer, message.chat.id)
                return
            elif today.time() <= times[0] and today.time() <= times[1]:
                answer = "{0} <b>Перерыв</b>\n\nСледующая:\n{1}".format(
                    emoji["couch_and_lamp"], lesson
                )
                func.send_long_message(bot, answer, message.chat.id)
                return

    answer = "{0} Пары уже закончились".format(emoji["sleep"])
    func.send_long_message(bot, answer, message.chat.id)
