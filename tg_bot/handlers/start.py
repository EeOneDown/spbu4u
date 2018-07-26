# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re

from flask import current_app
from telebot.apihelper import ApiException
from telebot.types import ReplyKeyboardMarkup, ReplyKeyboardRemove

from app import db
from app.constants import ids, support_answer
from app.models import User
from tg_bot import bot
from tg_bot.keyboards import select_status_keyboard


# Start message
@bot.message_handler(commands=["start"])
@bot.message_handler(
    func=lambda mess: mess.text.capitalize() == "Перезайти",
    content_types=["text"]
)
def start_handler(message):
    if current_app.config["BOT_NAME"] != "Spbu4UBot" \
            and message.chat.id not in ids.values():
        bot.reply_to(message, "Это тестовый бот. Используйте @Spbu4UBot")
    elif re.match(r"^/start[= ][ge]\d+$", message.text):
        # TODO skip registration's steps and create/update user
        pass
    else:
        if message.text == "/start":
            bot.send_message(
                chat_id=message.chat.id,
                text="Приветствую!",
                reply_markup=ReplyKeyboardMarkup(
                    resize_keyboard=True,
                    one_time_keyboard=False
                ).row("Завершить", "Поддержка")
            )
        bot.send_message(
            chat_id=message.chat.id,
            text="Для начала выбери в качестве кого ты хочешь зайти:",
            reply_markup=select_status_keyboard(),
            parse_mode="HTML"
        )


# Support message
@bot.message_handler(commands=["support"])
@bot.message_handler(
    func=lambda mess: mess.text.capitalize() == "Поддержка",
    content_types=["text"]
)
def problem_text_handler(message):
    bot.send_chat_action(message.chat.id, "typing")

    bot.send_message(
        chat_id=message.chat.id,
        text=support_answer,
        disable_web_page_preview=True,
        parse_mode="HTML"
    )


# Exit message
@bot.message_handler(commands=["exit"])
@bot.message_handler(
    func=lambda mess: mess.text.capitalize() == "Завершить",
    content_types=["text"]
)
def exit_handler(message):
    bot.send_chat_action(message.chat.id, "typing")

    User.query.filter_by(telegram_id=message.chat.id).delete()
    db.session.commit()

    bot.send_message(
        chat_id=message.chat.id,
        text="До встречи!",
        reply_markup=ReplyKeyboardRemove()
    )


# Cancel callback
@bot.callback_query_handler(
    func=lambda call_back: call_back.data == "Отмена"
)
def cancel_handler(call_back):
    try:
        bot.edit_message_text(
            text="Отмена",
            chat_id=call_back.message.chat.id,
            message_id=call_back.message.message_id
        )
    except ApiException:
        pass
