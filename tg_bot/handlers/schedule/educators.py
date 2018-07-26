# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from random import choice

import spbu
from flask import g
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ForceReply

import telebot_login
from app import new_functions as nf
from app.constants import (
    emoji, loading_text, ask_for_input_educator, max_inline_button_text_len
)
from app.models import Educator
from tg_bot import bot
from tg_bot.keyboards import schedule_keyboard, found_educators


# Educator search message
@bot.message_handler(
    func=lambda mess: mess.text == emoji["bust_in_silhouette"],
    content_types=["text"]
)
@telebot_login.login_required
def educator_schedule_handler(message):
    user = g.current_tbot_user

    bot.send_chat_action(user.tg_id, "typing")

    bot.send_message(user.tg_id, ask_for_input_educator,
                     reply_markup=ForceReply(), parse_mode="HTML")


# Educator name (Force reply) message
@bot.message_handler(
    func=lambda mess: nf.bot_waiting_for(mess, ask_for_input_educator),
    content_types=["text"]
)
@telebot_login.login_required
def write_educator_name_handler(message):
    user = g.current_tbot_user

    bot.send_chat_action(user.tg_id, "typing")

    name = message.text.strip(". ")
    if not nf.is_correct_educator_name(name):
        answer = "Недопустимые символы."
        bot.send_message(user.tg_id, answer,
                         reply_markup=schedule_keyboard())
        return

    try:
        educators_data = spbu.search_educator(name)
    except spbu.ApiException:
        answer = "Во время выполнения запроса произошла ошибка."
        bot.send_message(user.tg_id, answer,
                         reply_markup=schedule_keyboard())
        return

    if not educators_data["Educators"]:
        answer = "Никого не найдено."
        bot.send_message(user.tg_id, answer,
                         reply_markup=schedule_keyboard())
    elif len(educators_data["Educators"]) > 10:
        answer = "Слишком много преподавателей.\n" \
                 "Пожалуйста, <b>уточни</b>."
        bot.send_message(user.tg_id, answer, parse_mode="HTML")

        bot.send_message(user.tg_id, ask_for_input_educator,
                         reply_markup=ForceReply(), parse_mode="HTML")
    else:
        bot.send_message(
            user.tg_id, "Готово!", reply_markup=schedule_keyboard()
        )
        bot.send_message(
            chat_id=user.tg_id,
            text="{0} Найденные преподаватели:".format(emoji["mag_right"]),
            reply_markup=found_educators(educators_data),
            parse_mode="HTML"
        )


# Choose educator callback
@bot.callback_query_handler(
    func=lambda call_back:
        "Найденные преподаватели:" in call_back.message.text
)
@telebot_login.login_required_callback
def select_master_id_handler(call_back):
    user = g.current_tbot_user

    bot_msg = bot.edit_message_text(
        text="{0}\U00002026".format(choice(loading_text["schedule"])),
        chat_id=user.tg_id,
        message_id=call_back.message.message_id
    )
    answers = Educator(id=call_back.data).create_answers_for_term()
    bot.edit_message_text(text=answers[0],
                          chat_id=user.tg_id,
                          message_id=bot_msg.message_id,
                          parse_mode="HTML")
    for answer in answers[1:]:
        nf.send_long_message(bot, answer, user.tg_id)
