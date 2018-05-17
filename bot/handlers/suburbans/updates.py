# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime, timedelta, time

from telebot.apihelper import ApiException
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot import bot
from bot.constants import emoji, server_timedelta, all_stations
from bot.yandex_timetable import get_yandex_timetable_data


# Update callback
@bot.callback_query_handler(func=lambda call_back:
                            call_back.data == "Обновить")
def update_yandex_handler(call_back):
    from_to_stations = call_back.message.text.split("\n\n")[0].split(" => ")
    from_station_title = from_to_stations[0]
    to_station_title = from_to_stations[1]
    from_station = all_stations[from_station_title]
    to_station = all_stations[to_station_title]

    server_datetime = datetime.today() + server_timedelta
    data = get_yandex_timetable_data(from_station, to_station, server_datetime)
    answer = data["answer"]

    update_keyboard = InlineKeyboardMarkup(True)
    if data["is_OK"]:
        if data["is_tomorrow"]:
            inline_answer = emoji["warning"] + " На сегодня нет электричек"
            bot.answer_callback_query(call_back.id, inline_answer,
                                      show_alert=True)
            update_keyboard.row(*[InlineKeyboardButton(
                text=name, callback_data=name) for name in ["Все на завтра"]])
        else:
            update_keyboard.row(*[InlineKeyboardButton(
                text=name, callback_data=name)
                for name in ["Оставшиеся", "Обновить"]])

    try:
        bot.edit_message_text(text=answer,
                              chat_id=call_back.message.chat.id,
                              message_id=call_back.message.message_id,
                              parse_mode="HTML",
                              reply_markup=update_keyboard)
    except ApiException:
        pass
    finally:
        inline_answer = emoji["check_mark"] + " Обновлено"
        bot.answer_callback_query(call_back.id, inline_answer, cache_time=1)


# Remaining callback
@bot.callback_query_handler(func=lambda call_back:
                            call_back.data == "Оставшиеся")
def more_suburbans_handler(call_back):
    from_to_stations = call_back.message.text.split("\n\n")[0].split(" => ")
    from_station_title = from_to_stations[0]
    to_station_title = from_to_stations[1]
    from_station = all_stations[from_station_title]
    to_station = all_stations[to_station_title]
    server_datetime = datetime.today() + server_timedelta
    data = get_yandex_timetable_data(from_station, to_station, server_datetime,
                                     limit=100)
    answer = data["answer"]

    update_keyboard = InlineKeyboardMarkup(True)
    if data["is_OK"]:
        if data["is_tomorrow"]:
            inline_answer = emoji["warning"] + " На сегодня нет электричек"
            bot.answer_callback_query(call_back.id, inline_answer,
                                      show_alert=True)
            update_keyboard.row(*[InlineKeyboardButton(
                text=name, callback_data=name) for name in ["Все на завтра"]])
        else:
            update_keyboard.row(*[InlineKeyboardButton(
                text=name, callback_data=name)
                for name in ["Ближайшие", "Обновить"]])

    try:
        bot.edit_message_text(text=answer,
                              chat_id=call_back.message.chat.id,
                              message_id=call_back.message.message_id,
                              parse_mode="HTML",
                              reply_markup=update_keyboard)
    except ApiException:
        pass


# Closest callback
@bot.callback_query_handler(func=lambda call_back:
                            call_back.data == "Ближайшие")
def less_suburbans_handler(call_back):
    from_to_stations = call_back.message.text.split("\n\n")[0].split(" => ")
    from_station_title = from_to_stations[0]
    to_station_title = from_to_stations[1]
    from_station = all_stations[from_station_title]
    to_station = all_stations[to_station_title]
    server_datetime = datetime.today() + server_timedelta
    data = get_yandex_timetable_data(from_station, to_station, server_datetime)
    answer = data["answer"]

    update_keyboard = InlineKeyboardMarkup(True)
    if data["is_OK"]:
        if data["is_tomorrow"]:
            inline_answer = emoji["warning"] + " На сегодня нет электричек"
            bot.answer_callback_query(call_back.id, inline_answer,
                                      show_alert=True)
            update_keyboard.row(*[InlineKeyboardButton(
                text=name, callback_data=name) for name in ["Все на завтра"]])
        else:
            update_keyboard.row(*[InlineKeyboardButton(
                text=name, callback_data=name)
                for name in ["Оставшиеся", "Обновить"]])

    try:
        bot.edit_message_text(text=answer,
                              chat_id=call_back.message.chat.id,
                              message_id=call_back.message.message_id,
                              parse_mode="HTML",
                              reply_markup=update_keyboard)
    except ApiException:
        pass


# All for tomorrow callback
@bot.callback_query_handler(func=lambda call_back:
                            call_back.data == "Все на завтра")
def all_tomorrow_suburbans_handler(call_back):
    from_to_stations = call_back.message.text.split("\n\n")[0].split(" => ")
    from_station_title = from_to_stations[0]
    to_station_title = from_to_stations[1]
    from_station = all_stations[from_station_title]
    to_station = all_stations[to_station_title]

    server_datetime = datetime.combine(
        (datetime.today() + timedelta(days=1)).date(), time())

    data = get_yandex_timetable_data(from_station, to_station, server_datetime,
                                     limit=100)
    answer = data["answer"]

    update_keyboard = InlineKeyboardMarkup(True)
    if data["is_OK"]:
        update_keyboard.row(*[InlineKeyboardButton(
            text=name, callback_data=name) for name in ["Самые ранние"]])

    try:
        bot.edit_message_text(text=answer,
                              chat_id=call_back.message.chat.id,
                              message_id=call_back.message.message_id,
                              parse_mode="HTML",
                              reply_markup=update_keyboard)
    except ApiException:
        pass


# Earliest for tomorrow callback
@bot.callback_query_handler(func=lambda call_back:
                            call_back.data == "Самые ранние")
def early_tomorrow_suburbans_handler(call_back):
    from_to_stations = call_back.message.text.split("\n\n")[0].split(" => ")
    from_station_title = from_to_stations[0]
    to_station_title = from_to_stations[1]
    from_station = all_stations[from_station_title]
    to_station = all_stations[to_station_title]

    server_datetime = datetime.combine(
        (datetime.today() + timedelta(days=1)).date(), time())

    data = get_yandex_timetable_data(from_station, to_station, server_datetime,
                                     limit=5)
    answer = data["answer"]

    update_keyboard = InlineKeyboardMarkup(True)
    if data["is_OK"]:
        update_keyboard.row(*[InlineKeyboardButton(
            text=name, callback_data=name) for name in ["Все на завтра"]])

    try:
        bot.edit_message_text(text=answer,
                              chat_id=call_back.message.chat.id,
                              message_id=call_back.message.message_id,
                              parse_mode="HTML",
                              reply_markup=update_keyboard)
    except ApiException:
        pass
