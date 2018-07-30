# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from flask import g
from telebot.types import InlineQueryResultArticle, InputTextMessageContent

import telebot_login
from app import new_functions as nf
from app.constants import week_day_titles
from tg_bot import bot


@bot.inline_handler(
    func=lambda query: query.query.title() in week_day_titles.values()
)
@telebot_login.login_required_inline
def inline_query_weekday_schedule_handler(inline_query):
    user = g.current_tbot_user

    for_date = nf.get_date_by_weekday_title(inline_query.query.title())

    answer = user.create_answer_for_date(for_date)

    r = InlineQueryResultArticle(
        id="{0}_{1}".format(user.id, for_date),
        title=answer.split("\n\n")[0],
        input_message_content=InputTextMessageContent(
            answer, parse_mode="HTML"
        ),
        description=user.get_current_status_title()
    )
    bot.answer_inline_query(inline_query.id, [r], cache_time=1,
                            is_personal=True)


@bot.inline_handler(func=lambda query: True)
@telebot_login.login_required_inline
def inline_query_other_text_handler(inline_query):
    user = g.current_tbot_user

    bot.answer_inline_query(user.tg_id, [], cache_time=1, is_personal=True)
