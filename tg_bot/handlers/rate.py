# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from flask import g
from telebot.apihelper import ApiException
from telebot.types import ForceReply

import telebot_login
from app import db, new_functions as nf
from app.constants import emoji, ids, ask_to_feedback, rate_answers
from tg_bot import bot
from tg_bot.keyboards import main_keyboard, rate_keyboard


# Feedback text message
@bot.message_handler(
    func=lambda mess: nf.bot_waiting_for(mess, ask_to_feedback),
    content_types=["text"]
)
@telebot_login.login_required_message
def users_callback_handler(message):
    user = g.current_tbot_user

    bot.send_chat_action(message.chat.id, "typing")

    bot.forward_message(
        chat_id=ids["my"],
        from_chat_id=user.tg_id,
        message_id=message.message_id
    )
    bot.send_message(
        chat_id=user.tg_id,
        answer="Записал",
        reply_markup=main_keyboard(),
        reply_to_message_id=message.message_id
    )


# Statistics callback
@bot.callback_query_handler(
    func=lambda call_back: call_back.data == "Статистика"
)
@telebot_login.login_required_callback
def statistics_handler(call_back):
    user = g.current_tbot_user

    rates = user.get_rates()

    if len(rates):
        answer = "Пока что нет оценок."
    else:
        avg_rate = sum([r * rates[r] for r in rates]) / sum(rates.values())
        stars = emoji["star"] * int(round(avg_rate))
        answer = "Средняя оценка: {0}\n{1} ({2})".format(
            round(avg_rate, 1), stars, sum(rates.values())
        )
    if user.tg_id in ids.values():
        admin_statistics = user.get_admin_statistics()
        admin_answer = (
            "Количество пользователей: {0}\n" 
            "Количество групп: {1}\n" 
            "Количество преподавателей: {2}\n"
            "Количество пользователей с активной рассылкой: {3}"
        ).format(*admin_statistics)
        bot.send_message(
            chat_id=user.tg_id,
            answer=admin_answer
        )
    try:
        bot.edit_message_text(text=answer,
                              chat_id=call_back.message.chat.id,
                              message_id=call_back.message.message_id,
                              parse_mode="HTML")
    except ApiException:
        pass


# Feedback callback
@bot.callback_query_handler(
    func=lambda call_back: call_back.data == "Связь"
)
@telebot_login.login_required_callback
def feedback_handler(call_back):
    user = g.current_tbot_user

    bot.edit_message_text(
        chat_id=user.tg_id,
        text="Обратная связь",
        message_id=call_back.message.message_id
    )
    bot.send_message(
        chat_id=user.tg_id,
        answer=ask_to_feedback,
        reply_markup=ForceReply()
    )


# Rate mark callback
@bot.callback_query_handler(
    func=lambda call_back: call_back.data in ["1", "2", "3", "4", "5"]
)
@telebot_login.login_required_callback
def set_rate_handler(call_back):
    user = g.current_tbot_user

    user.rate = int(call_back.data)

    db.session.commit()

    try:
        bot.edit_message_text(
            chat_id=user.tg_id,
            text=rate_answers[user.rate],
            message_id=call_back.message.message_id,
            parse_mode="HTML",
            reply_markup=rate_keyboard(user.rate),
            disable_web_page_preview=True
        )
    except ApiException:
        pass
