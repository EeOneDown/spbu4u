# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

import tg_bot.functions as func
from tg_bot import bot
from app.constants import emoji


# Schedule sending message
@bot.message_handler(func=lambda mess: mess.text == emoji["alarm_clock"],
                     content_types=["text"])
def sending_handler(message):
    bot.send_chat_action(message.chat.id, "typing")
    answer = "Здесь ты можешь <b>подписаться</b> на рассылку расписания на " + \
             "следующий день или <b>отписаться</b> от неё.\n" + \
             "Рассылка производится в 21:00"
    sending_keyboard = InlineKeyboardMarkup(True)
    if func.is_sending_on(message.chat.id):
        sending_keyboard.row(
            *[InlineKeyboardButton(text=name, callback_data="Отписаться")
              for name in [emoji["cross_mark"] + " Отписаться"]])
    else:
        sending_keyboard.row(
            *[InlineKeyboardButton(text=name, callback_data="Подписаться")
              for name in [emoji["check_mark"] + " Подписаться"]])
    bot.send_message(message.chat.id, answer, parse_mode="HTML",
                     reply_markup=sending_keyboard)


# Activate sending callback
@bot.callback_query_handler(func=lambda call_back:
                            call_back.data == "Подписаться")
def sending_on_handler(call_back):
    func.set_sending(call_back.message.chat.id, True)
    answer = "{0} Рассылка <b>активирована</b>\nЖди рассылку в 21:00" \
             "".format(emoji["mailbox_on"])
    bot.edit_message_text(text=answer,
                          chat_id=call_back.message.chat.id,
                          message_id=call_back.message.message_id,
                          parse_mode="HTML")


# Deactivate sending callback
@bot.callback_query_handler(func=lambda call_back:
                            call_back.data == "Отписаться")
def sending_off_handler(call_back):
    func.set_sending(call_back.message.chat.id, False)
    answer = "{0} Рассылка <b>отключена</b>".format(emoji["mailbox_off"])
    bot.edit_message_text(text=answer,
                          chat_id=call_back.message.chat.id,
                          message_id=call_back.message.message_id,
                          parse_mode="HTML")
