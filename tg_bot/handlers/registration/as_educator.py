# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import spbu
from telebot.types import ForceReply, ReplyKeyboardMarkup

from app import db, new_functions as nf
from app.constants import (
    ask_for_input_educator_register, main_menu_first_answer
)
from app.models import User, Educator
from tg_bot import bot
from tg_bot.keyboards import found_educators_keyboard, main_keyboard


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
            text=ask_for_input_educator_register,
            reply_markup=ForceReply()
        )


# Educator choose message
@bot.callback_query_handler(
    func=lambda call_back: call_back.message.text == "Выбери преподавателя:"
)
def register_student_handler(call_back):
    bot_msg = bot.edit_message_text(
        text="Почти готово! Запоминаю твой выбор\U00002026",
        chat_id=call_back.message.chat.id,
        message_id=call_back.message.message_id
    )
    educator = Educator.query.get(call_back.data)
    if not educator:
        educator = Educator(
            id=call_back.data,
            title=spbu.get_educator_events(
                educator_id=call_back.data
            )["EducatorLongDisplayText"]
        )
        db.session.add(educator)

    user = User.query.filter_by(tg_id=call_back.message.chat.id).first()
    if not user:
        user = User(
            tg_id=call_back.message.chat.id,
            is_educator=True,
            current_group_id=0,
            current_educator_id=call_back.data
        )
    else:
        user.current_group_id = 0,
        user.current_educator_id = call_back.data
    db.session.add(user)

    db.session.commit()

    bot.edit_message_text(
        text=main_menu_first_answer,
        chat_id=call_back.message.chat.id,
        message_id=bot_msg.message_id,
        reply_markup=main_keyboard()
    )
