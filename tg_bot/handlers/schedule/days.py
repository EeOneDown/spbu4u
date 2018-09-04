# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import date, timedelta

from flask import g

import app.new_functions as nf
import telebot_login
from app.constants import (
    week_day_titles, max_answers_count, interval_exceeded_answer
)
from tg_bot import bot


# Today or tomorrow schedule message
@bot.message_handler(
    func=lambda mess: mess.text.title() == "Сегодня",
    content_types=["text"]
)
@bot.message_handler(
    func=lambda mess: mess.text.title() == "Завтра",
    content_types=["text"]
)
# Schedule for weekday title message
@bot.message_handler(
    func=lambda mess: mess.text.title() in week_day_titles.keys(),
    content_types=["text"]
)
@bot.message_handler(
    func=lambda mess: mess.text.title() in week_day_titles.values(),
    content_types=["text"]
)
# Schedule for date message
@bot.message_handler(
    func=lambda mess: nf.text_to_date(mess.text.lower()),
    content_types=["text"]
)
@telebot_login.login_required_message
@telebot_login.help_decorators.expected_failure_spbu_message
def day_schedule_handler(message):
    user = g.current_tbot_user

    bot.send_chat_action(message.chat.id, "typing")

    if message.text.title() == "Сегодня":
        for_date = date.today()
    elif message.text.title() == "Завтра":
        for_date = date.today() + timedelta(days=1)
    elif message.text.title() in week_day_titles.keys():
        for_date = nf.get_date_by_weekday_title(
            title=week_day_titles[message.text.title()]
        )
    elif message.text.title() in week_day_titles.values():
        for_date = nf.get_date_by_weekday_title(
            title=message.text.title()
        )
    else:
        for_date = nf.text_to_date(message.text.lower())

    answer = user.create_answer_for_date(for_date)

    nf.tgbot_send_long_message(bot, answer, user.tg_id)


# Schedule for interval message
@bot.message_handler(
    func=lambda mess: nf.text_to_interval(mess.text.lower()),
    content_types=["text"]
)
@telebot_login.login_required_message
@telebot_login.help_decorators.expected_failure_spbu_message
def interval_schedule_handler(message):
    user = g.current_tbot_user

    bot.send_chat_action(user.tg_id, "typing")

    answers = user.create_answers_for_interval(
        *nf.text_to_interval(message.text.lower())
    )
    if len(answers) > max_answers_count:
        answers = [interval_exceeded_answer]

    for answer in answers:
        nf.tgbot_send_long_message(bot, answer, user.tg_id)

