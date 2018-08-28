# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re

import spbu
from flask import current_app
from telebot.apihelper import ApiException
from telebot.types import ReplyKeyboardMarkup, ReplyKeyboardRemove

from app import db, new_functions as nf
from app.constants import (
    ids, support_answer, main_menu_first_answer, reg_tt_g_link, reg_tt_e_link
)
from app.models import User
from tg_bot import bot
from tg_bot.keyboards import select_status_keyboard, main_keyboard


def try_auto_reg(o_id, is_edu, tg_id, bot_msg_id):
    """
    Registers user if it possible or sends error message

    :param o_id: an object id (educator or group)
    :type o_id: int
    :param is_edu: if the user is an educator
    :type is_edu: bool
    :param tg_id: the user's telegram chat id
    :type tg_id: int
    :param bot_msg_id: the bot's sent message id
    :type bot_msg_id: int
    :return:
    """
    try:
        user = nf.reg_user(
            o_id=o_id,
            is_edu=is_edu,
            tg_id=tg_id
        )
    except spbu.ApiException:
        bot.edit_message_text(
            text="Ошибка в ID!",
            chat_id=tg_id,
            message_id=bot_msg_id
        )
    except Exception:
        bot.edit_message_text(
            text="Неизвестная ошибка!",
            chat_id=tg_id,
            message_id=bot_msg_id
        )
    else:
        bot.edit_message_text(
            text="Готово!",
            chat_id=user.tg_id,
            message_id=bot_msg_id
        )
        bot.send_message(
            text=main_menu_first_answer,
            parse_mode="HTML",
            chat_id=user.tg_id,
            reply_markup=main_keyboard()
        )


@bot.message_handler(commands=["start"])
@bot.message_handler(
    func=lambda mess: mess.text.capitalize() == "Перезайти",
    content_types=["text"]
)
def start_handler(message):
    if current_app.config["BOT_NAME"] != "Spbu4UBot" \
            and message.chat.id not in ids.values():
        bot.reply_to(message, "Это тестовый бот. Используйте @Spbu4UBot")
    elif re.match(r"^/start[= ]([ge])(\d+)$", message.text):
        r_groups = re.match(r"^/start[= ]([ge])(\d+)$", message.text).groups()
        bot_msg = bot.send_message(
            chat_id=message.chat.id,
            text="Автрегистрация.."
        )
        try_auto_reg(
            o_id=int(r_groups[1]),
            is_edu=r_groups[0] == "e",
            tg_id=message.chat.id,
            bot_msg_id=bot_msg.message_id
        )
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


@bot.message_handler(
    func=lambda mess: re.search(reg_tt_e_link, mess.text),
    content_types=["text"]
)
@bot.message_handler(
    func=lambda mess: re.search(reg_tt_g_link, mess.text),
    content_types=["text"]
)
def exit_handler(message):
    bot_msg = bot.send_message(
        chat_id=message.chat.id,
        text="Автрегистрация.."
    )
    res = re.search(reg_tt_e_link, message.text)
    if res:
        is_edu = True
    else:
        res = re.search(reg_tt_g_link, message.text)
        is_edu = False
    try_auto_reg(
        o_id=int(res.groups()[1]),
        is_edu=is_edu,
        tg_id=message.chat.id,
        bot_msg_id=bot_msg.message_id
    )


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


@bot.message_handler(commands=["exit"])
@bot.message_handler(
    func=lambda mess: mess.text.capitalize() == "Завершить",
    content_types=["text"]
)
def exit_handler(message):
    bot.send_chat_action(message.chat.id, "typing")

    user = User.query.filter_by(tg_id=message.chat.id).first()
    if user:
        user.clear_all()
        db.session.delete(user)
        db.session.commit()

    bot.send_message(
        chat_id=message.chat.id,
        text="До встречи!",
        reply_markup=ReplyKeyboardRemove()
    )


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
