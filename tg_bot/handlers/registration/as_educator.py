# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import spbu
from telebot.types import ForceReply, ReplyKeyboardMarkup

from app import new_functions as nf
from app.constants import ask_to_input_educator_register
from tg_bot import bot
from tg_bot.keyboards import found_educators_keyboard


# Educator status callback
@bot.callback_query_handler(
    func=lambda call_back: call_back.data == "Преподаватель"
)
def input_educator_name_handler(call_back):
    bot.edit_message_text(
        text=call_back.data,
        chat_id=call_back.message.chat.id,
        message_id=call_back.message.message_id
    )
    bot.send_message(
        chat_id=call_back.message.chat.id,
        text=ask_to_input_educator_register,
        reply_markup=ForceReply(),
        parse_mode="HTML"
    )


# Educator search for register message
@bot.message_handler(
    func=lambda mess: nf.bot_waiting_for(
        msg=mess,
        waiting_bot_text=ask_to_input_educator_register
    ),
    content_types=["text"]
)
def select_educator(message):
    bot.send_chat_action(message.chat.id, "typing")

    name = message.text.strip(". ")
    if not nf.is_correct_educator_name(name):
        error_answer = "Недопустимые символы!"
        is_error = True
    else:
        data = spbu.search_educator(name)

        if not data["Educators"] or len(data["Educators"]) > 10:
            if data["Educators"]:
                error_answer = "Слишком много преподавателей!"
            else:
                error_answer = "Никого не найдено!"
            is_error = True
        else:
            is_error = False
            error_answer = ""

            bot.send_message(
                chat_id=message.chat.id,
                text="Готово!",
                reply_markup=ReplyKeyboardMarkup(
                    resize_keyboard=True,
                    one_time_keyboard=False
                ).row("Завершить", "Поддержка")
            )
            bot.send_message(
                chat_id=message.chat.id,
                text="Выбери преподавателя:",
                reply_markup=found_educators_keyboard(data)
            )
    if is_error:
        bot.send_message(
            chat_id=message.chat.id,
            text=error_answer
        )
        bot.send_message(
            chat_id=message.chat.id,
            text=ask_to_input_educator_register,
            reply_markup=ForceReply()
        )
