# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime

from telebot.types import InlineQueryResultArticle, InputTextMessageContent

import app.bot.functions as func
from app.bot import bot
from app.bot.constants import week_day_titles, week_day_number, server_timedelta


@bot.inline_handler(func=lambda query:
                    not func.is_user_exist(query.from_user.id))
def inline_query_not_exist_user(inline_query):
    text = "Необходимо зарегистрироваться в группу"
    bot.answer_inline_query(inline_query.id, [], switch_pm_text=text,
                            switch_pm_parameter="new_from_inline",
                            cache_time=1, is_personal=True)


@bot.inline_handler(func=lambda query:
                    query.query.title() in week_day_titles.values())
def inline_query_weekday_schedule_handler(inline_query):
    user_id = inline_query.from_user.id
    week_day = inline_query.query.title()

    day_date = func.get_day_date_by_weekday_title(week_day)
    json_day = func.get_json_day_data(user_id, day_date)
    full_place = func.is_full_place(user_id)
    answer = func.create_schedule_answer(json_day, full_place, user_id)

    group_info = func.get_current_group(user_id)

    week_num = (datetime.today() + server_timedelta).isocalendar()[1]

    r = InlineQueryResultArticle(
        id="{0}_{1}_{2}_{3}".format(user_id, group_info[0], week_num,
                                    week_day_number[week_day]),
        title=answer.split("\n\n")[0],
        input_message_content=InputTextMessageContent(
            answer, parse_mode="HTML"
        ),
        description=group_info[1]
    )
    bot.answer_inline_query(inline_query.id, [r], cache_time=1,
                            is_personal=True)


@bot.inline_handler(func=lambda query: True)
def inline_query_other_text_handler(inline_query):
    bot.answer_inline_query(inline_query.id, [], cache_time=1, is_personal=True)
