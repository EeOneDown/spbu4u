# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime, timedelta, time
from random import choice

from telebot.apihelper import ApiException
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot import bot, functions as func
from bot.constants import emoji, server_timedelta, all_stations, loading_text
from bot.yandex_timetable import get_yandex_timetable_data


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
