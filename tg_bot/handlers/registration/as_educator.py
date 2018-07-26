# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from telebot.types import ForceReply

from app.constants import ask_for_input_educator_register
from app import new_functions as nf
from tg_bot import bot


# Educator status callback
@bot.callback_query_handler(
    func=lambda call_back: call_back.data == "Преподаватель"
)
def input_educator_name_handler(call_back):
    bot.edit_message_text(
        text="",
        chat_id=call_back.message.chat.id,
        message_id=call_back.message.message_id
    )
    bot.send_message(chat_id=call_back.message.chat.id,
                     text=ask_for_input_educator_register,
                     reply_markup=ForceReply(),
                     parse_mode="HTML")


# Educator search for register message
@bot.message_handler(
    func=lambda mess: nf.bot_waiting_for(
        msg=mess,
        waiting_bot_text=ask_for_input_educator_register
    ),
    content_types=["text"]
)
def select_educator(message):
    pass
