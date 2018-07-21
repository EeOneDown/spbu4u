# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime, timedelta, time
from random import choice

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from tg_bot import bot, functions as func
from app.constants import emoji, server_timedelta, all_stations, loading_text
from tg_bot.yandex_timetable import get_yandex_timetable_data


# Fast trail messages
@bot.message_handler(func=lambda mess: mess.text.title() == "В Универ",
                     content_types=["text"])
@bot.message_handler(func=lambda mess: mess.text.title() == "Домой",
                     content_types=["text"])
def to_university_handler(message):
    bot.send_chat_action(message.chat.id, "typing")

    if message.text.title() == "В Универ":
        from_station = func.get_station_code(message.chat.id, is_home=True)
        to_station = func.get_station_code(message.chat.id, is_home=False)
    else:
        from_station = func.get_station_code(message.chat.id, is_home=False)
        to_station = func.get_station_code(message.chat.id, is_home=True)

    server_datetime = datetime.today() + server_timedelta
    data = get_yandex_timetable_data(from_station, to_station, server_datetime)
    answer = data["answer"]

    update_keyboard = InlineKeyboardMarkup(True)
    if data["is_OK"]:
        if data["is_tomorrow"]:
            bot.send_message(message.chat.id, emoji["warning"] +
                             " На сегодня нет электричек")
            update_keyboard.row(*[InlineKeyboardButton(
                text=name, callback_data=name)
                for name in ["Все на завтра"]])
        else:
            update_keyboard.row(*[InlineKeyboardButton(
                text=name, callback_data=name)
                for name in ["Оставшиеся", "Обновить"]])

    bot.send_message(message.chat.id,
                     answer,
                     reply_markup=update_keyboard,
                     parse_mode='HTML',
                     disable_web_page_preview=True)


# Trail message
@bot.message_handler(func=lambda mess: mess.text.title() == "Маршрут",
                     content_types=["text"])
def own_trail_handler(message):
    answer = "Выбери начальную станцию:"
    start_station_keyboard = InlineKeyboardMarkup(True)
    for station_title in all_stations.keys():
        start_station_keyboard.row(*[InlineKeyboardButton(
            text=name, callback_data=name) for name in [station_title]])
    start_station_keyboard.row(*[InlineKeyboardButton(
            text=name, callback_data=name) for name in ["Домой", "В Универ"]])
    bot.send_message(message.chat.id, answer,
                     reply_markup=start_station_keyboard)


# personal trails callbacks
@bot.callback_query_handler(func=lambda call_back: call_back.data == "Домой")
@bot.callback_query_handler(func=lambda call_back: call_back.data == "В Универ")
def to_home_or_univer_handler(call_back):
    user_id = call_back.message.chat.id
    if call_back.data == "В Универ":
        from_station = func.get_station_code(user_id, is_home=True)
        to_station = func.get_station_code(user_id, is_home=False)
    else:
        from_station = func.get_station_code(user_id, is_home=False)
        to_station = func.get_station_code(user_id, is_home=True)

    from_station_title = func.get_key_by_value(all_stations, from_station)
    to_station_title = func.get_key_by_value(all_stations, to_station)

    answer = "Начальная: <b>{0}</b>\nКончная: <b>{1}</b>\nВыбери день:".format(
        from_station_title, to_station_title)
    day_keyboard = InlineKeyboardMarkup(True)
    day_keyboard.row(*[InlineKeyboardButton(
        text=name, callback_data=name) for name in ["Сегодня", "Завтра"]])
    bot.edit_message_text(text=answer,
                          chat_id=call_back.message.chat.id,
                          message_id=call_back.message.message_id,
                          reply_markup=day_keyboard,
                          parse_mode="HTML")


# From station callback
@bot.callback_query_handler(func=lambda call_back:
                            call_back.message.text == "Выбери начальную "
                                                      "станцию:")
def start_station_handler(call_back):
    answer = "Начальная: <b>{0}</b>\nВыбери конечную станцию:".format(
        call_back.data)
    end_station_keyboard = InlineKeyboardMarkup(True)
    for station_title in all_stations.keys():
        if station_title == call_back.data:
            continue
        end_station_keyboard.row(*[InlineKeyboardButton(
            text=name, callback_data=name) for name in [station_title]])
    end_station_keyboard.row(*[InlineKeyboardButton(
            text=name, callback_data=name) for name in ["Изменить начальную"]])
    bot.edit_message_text(text=answer,
                          chat_id=call_back.message.chat.id,
                          message_id=call_back.message.message_id,
                          reply_markup=end_station_keyboard,
                          parse_mode="HTML")


# Change start station callback
@bot.callback_query_handler(func=lambda call_back:
                            call_back.data == "Изменить начальную")
def change_start_station_handler(call_back):
    answer = "Выбери начальную станцию:"
    start_station_keyboard = InlineKeyboardMarkup(True)
    for station_title in all_stations.keys():
        start_station_keyboard.row(*[InlineKeyboardButton(
            text=name, callback_data=name) for name in [station_title]])
    bot.edit_message_text(text=answer,
                          chat_id=call_back.message.chat.id,
                          message_id=call_back.message.message_id,
                          reply_markup=start_station_keyboard)


# To station callback
@bot.callback_query_handler(func=lambda call_back: "Выбери конечную станцию:"
                                                   in call_back.message.text)
def end_station_handler(call_back):
    from_station_title = call_back.message.text.split("\n")[0].split(": ")[-1]
    to_station_title = call_back.data
    answer = "Начальная: <b>{0}</b>\nКончная: <b>{1}</b>\nВыбери день:".format(
        from_station_title, to_station_title)
    day_keyboard = InlineKeyboardMarkup(True)
    day_keyboard.row(*[InlineKeyboardButton(
        text=name, callback_data=name) for name in ["Сегодня", "Завтра"]])
    bot.edit_message_text(text=answer,
                          chat_id=call_back.message.chat.id,
                          message_id=call_back.message.message_id,
                          reply_markup=day_keyboard,
                          parse_mode="HTML")


# Day callback
@bot.callback_query_handler(func=lambda call_back: "Выбери день:"
                                                   in call_back.message.text)
def build_trail_handler(call_back):
    bot_msg = bot.edit_message_text(
        text="{0}\U00002026".format(choice(loading_text["ya_timetable"])),
        chat_id=call_back.message.chat.id,
        message_id=call_back.message.message_id
    )
    from_station_title = call_back.message.text.split("\n")[0].split(": ")[-1]
    to_station_title = call_back.message.text.split("\n")[1].split(": ")[-1]
    from_station = all_stations[from_station_title]
    to_station = all_stations[to_station_title]

    if call_back.data == "Завтра":
        server_datetime = datetime.combine(
            (datetime.today() + timedelta(days=1)).date(), time())
        limit = 7
    else:
        server_datetime = datetime.today() + server_timedelta
        limit = 3

    data = get_yandex_timetable_data(from_station, to_station, server_datetime,
                                     limit)
    answer = data["answer"]

    update_keyboard = InlineKeyboardMarkup(True)
    if data["is_OK"]:
        if call_back.data == "Завтра" or data["is_tomorrow"]:
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

    bot.edit_message_text(text=answer,
                          chat_id=call_back.message.chat.id,
                          message_id=bot_msg.message_id,
                          reply_markup=update_keyboard,
                          parse_mode="HTML")
