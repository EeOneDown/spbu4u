# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from tg_bot import bot, functions as func


# Place message
@bot.message_handler(func=lambda mess: mess.text.title() == "Адрес",
                     content_types=["text"])
def place_handler(message):
    bot.send_chat_action(message.chat.id, "typing")
    answer = "Здесь ты можешь выбрать отображаемый формат адреса\nСейчас: "
    place_keyboard = InlineKeyboardMarkup(True)
    if func.is_full_place(message.chat.id):
        answer += "<b>Полностью</b>"
        place_keyboard.row(
            *[InlineKeyboardButton(text=name, callback_data="Аудитория")
              for name in ["Только аудитория"]])
    else:
        answer += "<b>Только аудитория</b>"
        place_keyboard.row(
            *[InlineKeyboardButton(text=name, callback_data="Полностью")
              for name in ["Полностью"]])
    bot.send_message(message.chat.id, answer, parse_mode="HTML",
                     reply_markup=place_keyboard)


# Full place callback
@bot.callback_query_handler(func=lambda call_back:
                            call_back.data == "Полностью")
def full_place_on_handler(call_back):
    func.set_full_place(call_back.message.chat.id, True)
    answer = "Теперь адрес отображается <b>полностью</b>"
    bot.edit_message_text(text=answer,
                          chat_id=call_back.message.chat.id,
                          message_id=call_back.message.message_id,
                          parse_mode="HTML")


# Classroom callback
@bot.callback_query_handler(func=lambda call_back:
                            call_back.data == "Аудитория")
def full_place_off_handler(call_back):
    func.set_full_place(call_back.message.chat.id, False)
    answer = "Теперь отображается <b>только аудитория</b>"
    bot.edit_message_text(text=answer,
                          chat_id=call_back.message.chat.id,
                          message_id=call_back.message.message_id,
                          parse_mode="HTML")
