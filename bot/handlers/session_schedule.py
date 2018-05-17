# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from random import choice

from telebot.apihelper import ApiException
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot import bot, functions as func
from bot.constants import loading_text


@bot.message_handler(func=lambda mess: mess.text.capitalize() == "Сессия",
                     content_types=["text"])
@bot.message_handler(func=lambda mess: mess.text.capitalize() == "Допса",
                     content_types=["text"])
def attestation_handler(message):
    bot.send_chat_action(message.chat.id, "typing")
    month = func.get_available_months(message.chat.id)
    if len(month) == 0:
        bot.send_message(message.chat.id, "<i>Нет событий</i>",
                         parse_mode="HTML")
        return
    inline_keyboard = InlineKeyboardMarkup()
    for key in month.keys():
        inline_keyboard.row(
            *[InlineKeyboardButton(text=month[key], callback_data=str(key))]
        )
    if message.text == "Сессия":
        answer = "Выбери месяц:"
    else:
        answer = "Выбери месяц для Допсы:"
    bot.send_message(message.chat.id, answer, reply_markup=inline_keyboard)


@bot.callback_query_handler(func=lambda call_back:
                            "Выбери месяц" in call_back.message.text)
def select_months_att_handler(call_back):
    bot_msg = bot.edit_message_text(
        text="{0}\U00002026".format(choice(loading_text["schedule"])),
        chat_id=call_back.message.chat.id,
        message_id=call_back.message.message_id
    )
    json_attestation = func.get_json_attestation(call_back.message.chat.id)
    answers = []
    is_full_place = func.is_full_place(call_back.message.chat.id)

    if call_back.message.text == "Выбери месяц:":
        schedule_variations = [(True, True), (False, True)]
    else:
        schedule_variations = [(True, False), (False, False)]

    for personal, only_exams in schedule_variations:
        answers += func.create_session_answers(json_attestation, call_back.data,
                                               call_back.message.chat.id,
                                               is_full_place, personal,
                                               only_exams)
        if answers:
            break
    if not answers:
        answers.append("<i>Нет событий</i>")
    try:
        bot.edit_message_text(text=answers[0],
                              chat_id=call_back.message.chat.id,
                              message_id=bot_msg.message_id,
                              parse_mode="HTML")
    except ApiException:
        func.send_long_message(bot, answers[0], call_back.message.chat.id)
    finally:
        for answer in answers[1:]:
            func.send_long_message(bot, answer, call_back.message.chat.id)
