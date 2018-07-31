# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot import bot, functions as func
from bot.constants import emoji, all_stations


# Personalization message
@bot.message_handler(func=lambda mess: mess.text.title() == "Персонализация",
                     content_types=["text"])
def personalisation_handler(message):
    home_station = func.get_station_code(message.chat.id, is_home=True)
    univer_station = func.get_station_code(message.chat.id, is_home=False)

    home_station_title = func.get_key_by_value(all_stations, home_station)
    univer_station_title = func.get_key_by_value(all_stations, univer_station)

    answer = "Здесь ты можешь настроить <b>домашнюю</b> и " \
             "<b>Университетскую</b> станции для команд <i>Домой</i> и " \
             "<i>В Универ</i>\n\n" \
             "<b>Домашняя:</b> {0}\n<b>Университетская:</b> {1}".format(
                                    home_station_title, univer_station_title)

    inline_keyboard = InlineKeyboardMarkup(True)
    inline_keyboard.row(*[InlineKeyboardButton(
            text=name, callback_data=name) for name in ["Домашняя"]])
    inline_keyboard.row(*[InlineKeyboardButton(
            text=name, callback_data=name) for name in ["Университетская"]])
    bot.send_message(message.chat.id, answer,
                     reply_markup=inline_keyboard, parse_mode="HTML")


# Choose station type callback
@bot.callback_query_handler(func=lambda call_back:
                            call_back.data == "Домашняя")
@bot.callback_query_handler(func=lambda call_back:
                            call_back.data == "Университетская")
def home_station_handler(call_back):
    if call_back.data == "Домашняя":
        type_station = "домашнюю"
    else:
        type_station = "университетскую"
    answer = "Выбери {} станцию:".format(type_station)
    stations_keyboard = InlineKeyboardMarkup(True)
    for item in all_stations.items():
        stations_keyboard.row(*[InlineKeyboardButton(
            text=item[0], callback_data=all_stations[item[0]])])
    bot.edit_message_text(text=answer,
                          chat_id=call_back.message.chat.id,
                          message_id=call_back.message.message_id,
                          reply_markup=stations_keyboard)


# Choose station callback
@bot.callback_query_handler(func=lambda call_back:
                            call_back.message.text == "Выбери домашнюю "
                                                      "станцию:")
@bot.callback_query_handler(func=lambda call_back:
                            call_back.message.text == "Выбери университетскую "
                                                      "станцию:")
def change_home_station_handler(call_back):
    if "домашнюю" in call_back.message.text:
        type_station = "Домашняя"
        is_home = True
    else:
        type_station = "Университетская"
        is_home = False
    current_station = func.get_station_code(call_back.message.chat.id, is_home)
    current_another_station = func.get_station_code(call_back.message.chat.id,
                                                    not is_home)
    station_title = func.get_key_by_value(all_stations, call_back.data)
    answer = "{0} станция изменена на <b>{1}</b>\n".format(type_station,
                                                           station_title)
    func.change_station(call_back.message.chat.id,
                        call_back.data, is_home=is_home)
    if call_back.data == current_another_station:
        func.change_station(call_back.message.chat.id, current_station,
                            is_home=not is_home)
        inline_answer = "{0} Изменены обе станции!".format(emoji["warning"])
        bot.answer_callback_query(callback_query_id=call_back.id,
                                  text=inline_answer, show_alert=True)
    bot.edit_message_text(text=answer,
                          chat_id=call_back.message.chat.id,
                          message_id=call_back.message.message_id,
                          parse_mode="HTML")
