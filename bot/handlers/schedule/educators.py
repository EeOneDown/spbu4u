# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from random import choice

import spbu
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ForceReply

import bot.functions as func
from bot import bot
from bot.constants import emoji, loading_text
from bot.keyboards import schedule_keyboard


bot_name = "tt202_bot"

# Educator search message
@bot.message_handler(func=lambda mess: mess.text == emoji["bust_in_silhouette"],
                     content_types=["text"])
def educator_schedule_handler(message):
    bot.send_chat_action(message.chat.id, "typing")
    answer = "Введи Фамилию преподавателя: <i>(и И. О.)</i>"
    markup = ForceReply(False)
    bot.send_message(message.chat.id, answer, reply_markup=markup,
                     parse_mode="HTML")


# Educator name (Force reply) message
@bot.message_handler(
    func=lambda mess:
        mess.reply_to_message is not None and
        mess.reply_to_message.from_user.username == bot_name and
        "Введи Фамилию преподавателя:" in mess.reply_to_message.text,
    content_types=["text"])
def write_educator_name_handler(message):
    bot.send_chat_action(message.chat.id, "typing")
    answer = ""
    name = message.text.strip(". ")
    if not func.is_correct_educator_name(name):
        answer = "Недопустимые символы"
        bot.send_message(message.chat.id, answer,
                         reply_markup=schedule_keyboard)
        return

    try:
        educators_data = spbu.search_educator(name)
    except spbu.ApiException:
        answer = "Во время выполнения запроса произошла ошибка."
        bot.send_message(message.chat.id, answer,
                         reply_markup=schedule_keyboard)
        return

    if not educators_data["Educators"]:
        answer = "Никого не найдено"
        bot.send_message(message.chat.id, answer,
                         reply_markup=schedule_keyboard)
    elif len(educators_data["Educators"]) > 200:
        answer = "Слишком много преподавателей\n" \
                 "Пожалуйста, <b>уточни</b>"
        bot.send_message(message.chat.id, answer, parse_mode="HTML")
        answer = "Введи Фамилию преподавателя: <i>(и И. О.)</i>"
        markup = ForceReply(False)
        bot.send_message(message.chat.id, answer, reply_markup=markup,
                         parse_mode="HTML")
    else:
        bot.send_message(message.chat.id, "Готово!",
                         reply_markup=schedule_keyboard)

        educators_keyboard = InlineKeyboardMarkup(row_width=2)
        educators_keyboard.add(
            *[InlineKeyboardButton(text=educator["DisplayName"],
                                   callback_data=str(educator["Id"]))
              for educator in educators_data["Educators"]])
        educators_keyboard.row(InlineKeyboardButton(
            text="Отмена", callback_data="Отмена"))
        answer = "{0} Найденные преподаватели:\n\n".format(
            emoji["mag_right"]) + answer
        bot.send_message(message.chat.id, answer,
                         reply_markup=educators_keyboard, parse_mode="HTML")


# Choose educator callback
@bot.callback_query_handler(func=lambda call_back: "Найденные преподаватели:"
                                                   in call_back.message.text)
def select_master_id_handler(call_back):
    bot_msg = bot.edit_message_text(
        text="{0}\U00002026".format(choice(loading_text["schedule"])),
        chat_id=call_back.message.chat.id,
        message_id=call_back.message.message_id
    )
    answer = "{0} Расписание преподавателя: <b>{1}</b>\n\n{2} {3}"
    educator_schedule = spbu.get_educator_events(call_back.data)
    answer = answer.format(emoji["bust_in_silhouette"],
                           educator_schedule["EducatorLongDisplayText"],
                           emoji["calendar"],
                           educator_schedule["DateRangeDisplayText"])
    if not educator_schedule["HasEvents"]:
        answer += "\n\n<i>Нет событий</i>"
        bot.edit_message_text(text=answer,
                              chat_id=call_back.message.chat.id,
                              message_id=bot_msg.message_id,
                              parse_mode="HTML")
    else:
        bot.edit_message_text(text=answer,
                              chat_id=call_back.message.chat.id,
                              message_id=bot_msg.message_id,
                              parse_mode="HTML")
        days = [day for day in educator_schedule["EducatorEventsDays"]
                if day["DayStudyEventsCount"]]
        for day in days:
            answer = func.create_master_schedule_answer(day)
            func.send_long_message(bot, answer, call_back.message.chat.id)
