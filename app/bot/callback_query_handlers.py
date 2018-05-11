# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime, time
from math import ceil
from random import choice

import spbu
from telebot.apihelper import ApiException
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ForceReply

import app.bot.functions as func
from app.bot import bot
from app.bot.constants import *
from app.bot.keyboards import *
from app.bot.message_handlers import start_handler
from app.bot.yandex_timetable import get_yandex_timetable_data


@bot.callback_query_handler(func=lambda call_back:
                            not func.is_user_exist(call_back.message.chat.id))
def not_exist_user_callback_handler(call_back):
    answer = "Чтобы пользоваться сервисом, необходимо " \
             "зарегистрироваться.\nВоспользуйся коммандой /start"
    bot.edit_message_text(text=answer,
                          chat_id=call_back.message.chat.id,
                          message_id=call_back.message.message_id,
                          parse_mode="HTML")


@bot.callback_query_handler(func=lambda call_back:
                            call_back.data == "Благодарности")
def show_full_info(call_back):
    answer = special_thanks
    bot.edit_message_text(text=answer,
                          chat_id=call_back.message.chat.id,
                          message_id=call_back.message.message_id,
                          parse_mode="HTML",
                          disable_web_page_preview=True)
    inline_answer = "И тебе :)"
    bot.answer_callback_query(call_back.id, inline_answer, cache_time=1)


@bot.callback_query_handler(func=lambda call_back:
                            call_back.data in week_day_number.keys() or
                            call_back.data == "Вся неделя")
def select_week_day_schedule_handler(call_back):
    day = ""
    if call_back.data == "Вся неделя":
        day += "Неделя"
    else:
        day += [item[0] for item in week_day_titles.items() if
                item[1] == call_back.data][0]
    answer = "Расписание на: <i>{0}</i>\n".format(day)
    week_type_keyboard = InlineKeyboardMarkup()
    week_type_keyboard.row(
        *[InlineKeyboardButton(text=name, callback_data=name) for
          name in ["Текущее", "Следующее"]]
    )
    bot.edit_message_text(text=answer,
                          chat_id=call_back.message.chat.id,
                          message_id=call_back.message.message_id,
                          parse_mode="HTML",
                          reply_markup=week_type_keyboard)


@bot.callback_query_handler(func=lambda call_back:
                            "Расписание на: Неделя" in call_back.message.text)
def all_week_schedule_handler(call_back):
    user_id = call_back.message.chat.id
    bot_msg = bot.edit_message_text(
        text="{0}\U00002026".format(choice(loading_text["schedule"])),
        chat_id=call_back.message.chat.id,
        message_id=call_back.message.message_id
    )
    if call_back.data == "Текущее":
        json_week = func.get_json_week_data(user_id)
    else:
        json_week = func.get_json_week_data(user_id, next_week=True)
    inline_answer = json_week["WeekDisplayText"]
    bot.answer_callback_query(call_back.id, inline_answer, cache_time=1)
    is_send = False
    if len(json_week["Days"]):
        for day in json_week["Days"]:
            full_place = func.is_full_place(call_back.message.chat.id)
            answer = func.create_schedule_answer(day, full_place,
                                                 call_back.message.chat.id)
            if "Выходной" in answer:
                continue
            if json_week["Days"].index(day) == 0 or not is_send:
                try:
                    bot.edit_message_text(text=answer,
                                          chat_id=user_id,
                                          message_id=bot_msg.message_id,
                                          parse_mode="HTML")
                except ApiException:
                    func.send_long_message(bot, answer, user_id)
            else:
                func.send_long_message(bot, answer, user_id)
            is_send = True
    if not is_send or not len(json_week["Days"]):
        answer = "{0} Выходная неделя".format(emoji["sleep"])
        bot.edit_message_text(text=answer,
                              chat_id=user_id,
                              message_id=bot_msg.message_id)


@bot.callback_query_handler(func=lambda call_back:
                            call_back.data == "Текущее" or
                            call_back.data == "Следующее")
def week_day_schedule_handler(call_back):
    bot_msg = bot.edit_message_text(
        text="{0}\U00002026".format(choice(loading_text["schedule"])),
        chat_id=call_back.message.chat.id,
        message_id=call_back.message.message_id
    )
    is_next_week = False
    iso_day_date = list((datetime.today() + server_timedelta).isocalendar())
    if iso_day_date[2] == 7:
        iso_day_date[1] += 1
    if call_back.data == "Следующее":
        iso_day_date[1] += 1
        is_next_week = True
    iso_day_date[2] = week_day_number[
        week_day_titles[call_back.message.text.split(": ")[-1]]]
    day_date = func.date_from_iso(iso_day_date)
    json_day = func.get_json_day_data(call_back.message.chat.id, day_date,
                                      next_week=is_next_week)
    full_place = func.is_full_place(call_back.message.chat.id)
    answer = func.create_schedule_answer(json_day, full_place,
                                         call_back.message.chat.id)
    try:
        bot.edit_message_text(text=answer,
                              chat_id=call_back.message.chat.id,
                              message_id=bot_msg.message_id,
                              parse_mode="HTML")
    except ApiException:
        func.send_long_message(bot, answer, call_back.message.chat.id)


@bot.callback_query_handler(func=lambda call_back:
                            call_back.data == "Подписаться")
def sending_on_handler(call_back):
    func.set_sending(call_back.message.chat.id, True)
    answer = "{0} Рассылка <b>активирована</b>\nЖди рассылку в 21:00" \
             "".format(emoji["mailbox_on"])
    bot.edit_message_text(text=answer,
                          chat_id=call_back.message.chat.id,
                          message_id=call_back.message.message_id,
                          parse_mode="HTML")


@bot.callback_query_handler(func=lambda call_back:
                            call_back.data == "Отписаться")
def sending_off_handler(call_back):
    func.set_sending(call_back.message.chat.id, False)
    answer = "{0} Рассылка <b>отключена</b>".format(emoji["mailbox_off"])
    bot.edit_message_text(text=answer,
                          chat_id=call_back.message.chat.id,
                          message_id=call_back.message.message_id,
                          parse_mode="HTML")


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


@bot.callback_query_handler(func=lambda call_back:
                            call_back.data == "Полностью")
def full_place_on_handler(call_back):
    func.set_full_place(call_back.message.chat.id, True)
    answer = "Теперь адрес отображается <b>полностью</b>"
    bot.edit_message_text(text=answer,
                          chat_id=call_back.message.chat.id,
                          message_id=call_back.message.message_id,
                          parse_mode="HTML")


@bot.callback_query_handler(func=lambda call_back:
                            call_back.data == "Аудитория")
def full_place_off_handler(call_back):
    func.set_full_place(call_back.message.chat.id, False)
    answer = "Теперь отображается <b>только аудитория</b>"
    bot.edit_message_text(text=answer,
                          chat_id=call_back.message.chat.id,
                          message_id=call_back.message.message_id,
                          parse_mode="HTML")


@bot.callback_query_handler(func=lambda call_back:
                            call_back.data == "Отмена")
def cancel_handler(call_back):
    answer = "Отмена"
    try:
        bot.edit_message_text(text=answer, chat_id=call_back.message.chat.id,
                              message_id=call_back.message.message_id)
    except ApiException:
        pass


@bot.callback_query_handler(func=lambda call_back: call_back.data == "Занятие")
def editor_choose_lesson_handler(call_back):
    answer = "Выбери пару с большим количеством занятий:"
    selective_blocks = func.get_selective_blocks(call_back.message.chat.id)
    blocks_keyboard = InlineKeyboardMarkup(True)
    for key in selective_blocks:
        blocks_keyboard.row(
            *[InlineKeyboardButton(text=name, callback_data=name)
              for name in [key]]
        )
    if len(blocks_keyboard.to_dic()["inline_keyboard"]):
        blocks_keyboard.row(
            *[InlineKeyboardButton(text=name, callback_data=name)
              for name in ["Отмена"]])
    else:
        answer = "Нет пар с большим количеством занятий"
    bot.edit_message_text(text=answer,
                          chat_id=call_back.message.chat.id,
                          message_id=call_back.message.message_id,
                          reply_markup=blocks_keyboard)


@bot.callback_query_handler(func=lambda call_back:
                            "Выбери пару с большим количеством занятий:" in
                            call_back.message.text)
def select_block_choose_lesson_handler(call_back):
    bot.edit_message_text(chat_id=call_back.message.chat.id,
                          text="{0} {1}".format(emoji["calendar"],
                                                call_back.data),
                          message_id=call_back.message.message_id)

    selective_blocks = func.get_selective_blocks(call_back.message.chat.id)

    answer, lessons = func.create_selective_block_answer(
        call_back.message.chat.id, selective_blocks[call_back.data],
        call_back.data.lower()
    )

    inline_keyboard = InlineKeyboardMarkup()
    for lesson in lessons:
        inline_keyboard.row(
            *[InlineKeyboardButton(text=name, callback_data=name)
              for name in [lesson]]
        )
    inline_keyboard.row(
        *[InlineKeyboardButton(text=name, callback_data=name)
          for name in ["Отмена"]]
        )

    answer = "Вот список занятий, проходящих в данное время:\n\n" \
             "{0}" \
             "Выбери занятие, которое хочешь оставить:".format(answer)

    bot.send_message(chat_id=call_back.message.chat.id,
                     text=answer,
                     reply_markup=inline_keyboard,
                     parse_mode="HTML")


@bot.callback_query_handler(func=lambda call_back:
                            "Выбери занятие, которое хочешь оставить:" in
                            call_back.message.text)
def lesson_chosen_handler(call_back):
    bot_message_text = call_back.message.text.replace(
        " {0}".format(emoji["cross_mark"]), "")
    lessons = bot_message_text.split("\n\n")[1:-1]
    chosen_lesson_number = int(call_back.data.split(". ")[0]) - 1
    chosen_lesson_name = " - ".join(
        lessons[chosen_lesson_number].split("\n")[0].split(" - ")[1:]
    )
    chosen_lesson_educators = ""

    for num, lesson in enumerate(lessons):
        if num == chosen_lesson_number:
            continue

        hide_event_name = " - ".join(lesson.split("\n")[0].split(" - ")[1:])
        hide_event_types = "all"
        hide_day = "all"
        hide_time = "all"
        hide_educators = ""
        if hide_event_name == chosen_lesson_name:
            if not chosen_lesson_educators:
                for place_edu in lessons[chosen_lesson_number].split("\n")[1:]:
                    pos = place_edu.find("(")
                    if pos != -1:
                        chosen_lesson_educators += place_edu[pos + 1:-1] + "; "
                chosen_lesson_educators = "(" + chosen_lesson_educators.strip(
                    "; ") + ")"

            for place_edu in lesson.split("\n")[1:]:
                pos = place_edu.find("(")
                if pos != -1:
                    hide_educators += place_edu[pos + 1:-1] + "; "
            hide_educators = hide_educators.strip("; ")
        else:
            hide_educators = "all"

        func.insert_skip(hide_event_name, hide_event_types, hide_day, hide_time,
                         hide_educators, call_back.message.chat.id)
    answer = "Выбрано занятие <b>{0}</b> <i>{1}</i>".format(
        chosen_lesson_name, chosen_lesson_educators
    )
    bot.edit_message_text(text=answer, chat_id=call_back.message.chat.id,
                          message_id=call_back.message.message_id,
                          parse_mode="HTML")


@bot.callback_query_handler(func=lambda call_back:
                            call_back.data == "Преподавателя")
def editor_choose_educator_handler(call_back):
    answer = "Выбери день, в котором есть занятие с большим количеством " \
             "преподавателей:"
    json_week_data = func.get_json_week_data(call_back.message.chat.id)
    days = json_week_data["Days"]
    days_keyboard = InlineKeyboardMarkup(True)
    for day in days:
        data = datetime.strptime(day["Day"], "%Y-%m-%dT%H:%M:%S").date()
        answer_data = func.get_lessons_with_educators(call_back.message.chat.id,
                                                      data)
        if answer_data["is_empty"]:
            continue
        days_keyboard.row(
            *[InlineKeyboardButton(text=name, callback_data=name)
              for name in [day["DayString"].split(", ")[0].capitalize()]])
    if len(days_keyboard.to_dic()["inline_keyboard"]):
        days_keyboard.row(
            *[InlineKeyboardButton(text=name, callback_data=name)
              for name in ["Отмена"]])
    else:
        answer = "Нет занятий с большим количеством преподавателей"
    bot.edit_message_text(text=answer, chat_id=call_back.message.chat.id,
                          message_id=call_back.message.message_id,
                          reply_markup=days_keyboard)


@bot.callback_query_handler(func=lambda call_back:
                            "Выбери день, в котором есть занятие с большим " in
                            call_back.message.text)
def select_day_choose_educator_handler(call_back):
    iso_day_date = list((datetime.today() + server_timedelta).isocalendar())
    if iso_day_date[2] == 7:
        iso_day_date[1] += 1
    iso_day_date[2] = week_day_number[week_day_titles[call_back.data]]
    day_date = func.date_from_iso(iso_day_date)

    answer_data = func.get_lessons_with_educators(call_back.message.chat.id,
                                                  day_date)
    day_string = answer_data["date"]
    bot.edit_message_text(chat_id=call_back.message.chat.id,
                          text="{0} {1}".format(emoji["calendar"], day_string),
                          message_id=call_back.message.message_id)
    answer = "Вот список подходящих занятий:\n\n"
    answer += answer_data["answer"]
    inline_keyboard = InlineKeyboardMarkup()
    if not answer_data["is_empty"]:
        for event in answer_data["answer"].split("\n\n"):
            button_text = "{0}".format(event.split("\n")[0].strip(" {0}".format(
                emoji["cross_mark"]))[3:-4])
            inline_keyboard.row(
                *[InlineKeyboardButton(
                    text=name, callback_data=name[:max_inline_button_text_len]
                ) for name in [button_text]]
            )
        inline_keyboard.row(
            InlineKeyboardButton(text="Отмена", callback_data="Отмена"))
        answer += "\n\nВыбери необходиое занятие:"
    bot.send_message(text=answer, chat_id=call_back.message.chat.id,
                     parse_mode="HTML", reply_markup=inline_keyboard)


@bot.callback_query_handler(func=lambda call_back: "Выбери необходиое занятие:"
                                                   in call_back.message.text)
def select_educator_handler(call_back):
    message_text_data = call_back.message.text.split("\n\n")[1:-1]
    chosen_event_number = int(call_back.data.split(". ")[0]) - 1
    chosen_event = ". ".join(
        message_text_data[chosen_event_number].split(". ")[1:])
    chosen_event_data = chosen_event.split("\n")
    available_educators = []
    for place_edu in chosen_event_data[1:]:
        if "(" not in place_edu:
            continue

        place_edu = place_edu.strip(" {0}".format(emoji["heavy_check_mark"]))
        available_educators.append(place_edu.split("(")[1][:-1])

    inline_keyboard = InlineKeyboardMarkup(row_width=1)
    inline_keyboard.add(
        *[InlineKeyboardButton(
            text=name, callback_data=name[:max_inline_button_text_len]
        ) for name in available_educators]
    )
    inline_keyboard.row(
        InlineKeyboardButton(text="Отмена", callback_data="Отмена"))
    answer = "Выбранное занятие:\n<b>{0}</b>\n\nВыбери преподавателя, " \
             "которого оставить:".format(
                chosen_event_data[0].strip(" {0}".format(emoji["cross_mark"])))
    bot.edit_message_text(text=answer,
                          chat_id=call_back.message.chat.id,
                          message_id=call_back.message.message_id,
                          parse_mode="HTML",
                          reply_markup=inline_keyboard)


@bot.callback_query_handler(func=lambda call_back:
                            "Выбери преподавателя, которого оставить:" in
                            call_back.message.text)
def educator_chosen_handler(call_back):
    event_name = call_back.message.text.split("\n")[1]
    chosen_educators = call_back.data
    func.insert_skip(event_name=event_name, types="all", event_day="all",
                     event_time="all", educators=chosen_educators,
                     user_id=call_back.message.chat.id, is_choose_educator=True)
    answer = "<b>Добавлена связь</b> занятия и преподавателя: {0} - {1}" \
             "".format(event_name, chosen_educators)
    bot.edit_message_text(text=answer,
                          chat_id=call_back.message.chat.id,
                          message_id=call_back.message.message_id,
                          parse_mode="HTML")


@bot.callback_query_handler(func=lambda call_back:
                            "Выбери день, когда есть это занятие:" in
                            call_back.message.text)
def select_day_hide_lesson_handler(call_back):
    iso_day_date = list((datetime.today() + server_timedelta).isocalendar())
    if iso_day_date[2] == 7:
        iso_day_date[1] += 1
    iso_day_date[2] = week_day_number[week_day_titles[call_back.data]]
    day_date = func.date_from_iso(iso_day_date)

    blocks = func.get_blocks(call_back.message.chat.id, day_date)
    answer = "{0} {1}\n".format(emoji["calendar"], blocks[0])
    bot.edit_message_text(text=answer,
                          chat_id=call_back.message.chat.id,
                          message_id=call_back.message.message_id)
    first_block = blocks[1][0]
    day_string = blocks[0].split(", ")[0]
    answer = "<b>1 из {0}</b> <i>({1})</i>\n\n{2}".format(len(blocks[1]),
                                                          day_string,
                                                          first_block)
    events_keyboard = InlineKeyboardMarkup(True)
    events = [event.split("\n")[0] for event in first_block.split("\n\n")[1:-1]]
    for event in events:
        event_name = event.strip(" {0}".format(emoji["cross_mark"]))[
                     3:-4].split(" - ")
        button_text = "{0} - {1}".format(event_name[0],
                                         event_name[1].split(". ")[-1])
        events_keyboard.row(
            *[InlineKeyboardButton(
                text=name, callback_data=name[:max_inline_button_text_len]
            ) for name in [button_text]]
        )
    events_keyboard.row(
        *[InlineKeyboardButton(text=emoji[name], callback_data=name)
          for name in ["prev_block", "Отмена", "next_block"]]
    )
    bot.send_message(chat_id=call_back.message.chat.id, text=answer,
                     reply_markup=events_keyboard, parse_mode="HTML")


@bot.callback_query_handler(func=lambda call_back:
                            call_back.data == "next_block")
def next_block_handler(call_back):
    data = func.get_current_block(call_back.message.text,
                                  call_back.message.chat.id)
    answer, events = data[0], data[1]
    events_keyboard = InlineKeyboardMarkup(True)
    for event in events:
        event_name = event.strip(" {0}".format(emoji["cross_mark"]))[
                     3:-4].split(" - ")
        button_text = "{0} - {1}".format(event_name[0],
                                         event_name[1].split(". ")[-1])
        events_keyboard.row(
            *[InlineKeyboardButton(
                text=name, callback_data=name[:max_inline_button_text_len]
            ) for name in [button_text]]
        )
    events_keyboard.row(
        *[InlineKeyboardButton(text=emoji[name], callback_data=name)
          for name in ["prev_block", "Отмена", "next_block"]]
    )
    try:
        bot.edit_message_text(text=answer, chat_id=call_back.message.chat.id,
                              message_id=call_back.message.message_id,
                              parse_mode="HTML", reply_markup=events_keyboard)
    except ApiException:
        pass


@bot.callback_query_handler(func=lambda call_back:
                            call_back.data == "prev_block")
def prev_block_handler(call_back):
    data = func.get_current_block(call_back.message.text,
                                  call_back.message.chat.id,
                                  is_prev=True)
    answer, events = data[0], data[1]
    events_keyboard = InlineKeyboardMarkup(True)
    for event in events:
        event_name = event.strip(" {0}".format(emoji["cross_mark"]))[
                     3:-4].split(" - ")
        button_text = "{0} - {1}".format(event_name[0],
                                         event_name[1].split(". ")[-1])
        events_keyboard.row(
            *[InlineKeyboardButton(
                text=name, callback_data=name[:max_inline_button_text_len]
            ) for name in [button_text]]
        )
    events_keyboard.row(
        *[InlineKeyboardButton(text=emoji[name], callback_data=name)
          for name in ["prev_block", "Отмена", "next_block"]]
    )
    try:
        bot.edit_message_text(text=answer, chat_id=call_back.message.chat.id,
                              message_id=call_back.message.message_id,
                              parse_mode="HTML", reply_markup=events_keyboard)
    except ApiException:
        pass


@bot.callback_query_handler(func=lambda call_back:
                            "Выбери занятие:" in call_back.message.text)
def lesson_selected_handler(call_back):
    message_text_data = call_back.message.text.split("\n\n")
    answer = "{0} ({1})\n\nВыбранное занятие: \n".format(
        message_text_data[1], message_text_data[0].split(" ")[-1][1:-1])
    events = message_text_data[2:-1]
    chosen_event = ". ".join(
        events[int(call_back.data.split(". ")[0]) - 1].split(". ")[1:])
    event_title = chosen_event.split("\n")[0].strip(" {0}".format(
        emoji["cross_mark"]))
    event_type = event_title.split(" - ")[0]
    event_title = " - ".join(event_title.split(" - ")[1:])
    answer += "<b>{0}</b>\n{1}\n\nТипы: <b>Любой тип</b>\n\n".format(
        event_title, "\n".join(chosen_event.split("\n")[1:]))
    answer += "Укажи типы занятия, которые скрывать: "
    types_keyboard = InlineKeyboardMarkup(row_width=3)
    short_types = list(subject_short_type.values())
    if event_type in short_types:
        is_special_type = False
    else:
        is_special_type = True
    types_keyboard.add(
        *[InlineKeyboardButton(text=name, callback_data=name)
          for name in short_types])
    if is_special_type:
        types_keyboard.row(
            *[InlineKeyboardButton(
                text=name, callback_data=name[:max_inline_button_text_len]
            ) for name in [event_type]]
        )
    types_keyboard.row(
        *[InlineKeyboardButton(text=name, callback_data=name)
          for name in ["Отмена", "Далее"]])
    bot.edit_message_text(text=answer,
                          chat_id=call_back.message.chat.id,
                          message_id=call_back.message.message_id,
                          parse_mode="HTML",
                          reply_markup=types_keyboard)


@bot.callback_query_handler(func=lambda call_back:
                            call_back.data == "Далее")
def types_selected_handler(call_back):
    message_text_data = call_back.message.text.split("\n\n")
    answer = "{0}\n\n{1}\n<b>{2}</b>\n{3}\n\nТипы: <b>{4}</b>\n\n".format(
        message_text_data[0], message_text_data[1].split("\n")[0],
        message_text_data[1].split("\n")[1],
        "\n".join(message_text_data[1].split("\n")[2:]),
        message_text_data[2].split(": ")[1]
    )
    days_keyboard = InlineKeyboardMarkup(True)
    day_title = message_text_data[0].split(" ")[-1][1:-1]
    if day_title == "Понедельник" or day_title == "Вторник" or \
                    day_title == "Четверг":
        day_title += "и"
    else:
        day_title = day_title[:-1] + "ы"
    days_keyboard.row(
        *[InlineKeyboardButton(text=name, callback_data=name)
          for name in ["Все {0}".format(day_title.lower())]])
    days_keyboard.row(
        *[InlineKeyboardButton(text=name, callback_data=name)
          for name in ["Отмена", "Все дни"]])
    answer += "Выбери дни для скрытия занятия:"
    bot.edit_message_text(text=answer,
                          chat_id=call_back.message.chat.id,
                          message_id=call_back.message.message_id,
                          parse_mode="HTML",
                          reply_markup=days_keyboard)


@bot.callback_query_handler(func=lambda call_back:
                            "Укажи типы занятия, которые скрывать:" in
                            call_back.message.text)
def select_types_handler(call_back):
    message_text_data = call_back.message.text.split("\n\n")
    answer = "{0}\n\n{1}\n<b>{2}</b>\n{3}\n\n".format(
        message_text_data[0], message_text_data[1].split("\n")[0],
        message_text_data[1].split("\n")[1],
        "\n".join(message_text_data[1].split("\n")[2:]))
    all_chosen_types = message_text_data[2].split(": ")[1].split("; ")
    chosen_type = call_back.data.strip("{0} ".format(emoji["heavy_check_mark"]))
    if chosen_type in all_chosen_types:
        all_chosen_types.remove(chosen_type)
        if len(all_chosen_types) == 0:
            all_chosen_types.append("Любой тип")
    else:
        if "Любой тип" in all_chosen_types:
            all_chosen_types.remove("Любой тип")
        all_chosen_types.append(chosen_type)
    answer += "Типы: <b>{0}</b>\n\nУкажи типы занятия, которые " \
              "скрывать:".format("; ".join(all_chosen_types))
    types_keyboard = InlineKeyboardMarkup(row_width=3)
    short_types = [short_type for short_type in subject_short_type.values()]
    is_special_type = chosen_type not in short_types
    for i in range(len(short_types)):
        if short_types[i] in types:
            short_types[i] = "{0} {1}".format(emoji["heavy_check_mark"],
                                              short_types[i])
    types_keyboard.add(
        *[InlineKeyboardButton(text=name, callback_data=name)
          for name in short_types])
    if is_special_type:
        if chosen_type in types:
            chosen_type = "{0} {1}".format(emoji["heavy_check_mark"],
                                           chosen_type)
        types_keyboard.row(
            *[InlineKeyboardButton(
                text=name, callback_data=name[:max_inline_button_text_len]
            ) for name in [chosen_type]]
        )
    types_keyboard.row(
        *[InlineKeyboardButton(text=name, callback_data=name)
          for name in ["Отмена", "Далее"]])
    bot.edit_message_text(text=answer,
                          chat_id=call_back.message.chat.id,
                          message_id=call_back.message.message_id,
                          parse_mode="HTML",
                          reply_markup=types_keyboard)


@bot.callback_query_handler(func=lambda call_back:
                            "Выбери дни для скрытия занятия:" in
                            call_back.message.text)
def select_time_handler(call_back):
    message_text_data = call_back.message.text.split("\n\n")
    answer = "{0}\n\n{1}\n<b>{2}</b>\n{3}\n\nТипы: <b>{4}</b>\n\n".format(
        message_text_data[0], message_text_data[1].split("\n")[0],
        message_text_data[1].split("\n")[1],
        "\n".join(message_text_data[1].split("\n")[2:]),
        message_text_data[2].split(": ")[1]
    )
    times_keyboard = InlineKeyboardMarkup(True)
    lesson_time = message_text_data[0].split(" ")[1]
    times_keyboard.row(
        *[InlineKeyboardButton(text=name, callback_data=name)
          for name in [lesson_time]])
    times_keyboard.row(
        *[InlineKeyboardButton(text=name, callback_data=name) for
          name in ["Отмена", "Любое время"]])
    answer += "День: <b>{0}</b>\n\nВыбери время, в которе скрывать:".format(
        call_back.data)
    bot.edit_message_text(text=answer,
                          chat_id=call_back.message.chat.id,
                          message_id=call_back.message.message_id,
                          parse_mode="HTML",
                          reply_markup=times_keyboard)


@bot.callback_query_handler(func=lambda call_back:
                            "Выбери время, в которе скрывать:" in
                            call_back.message.text)
def select_place_educator_handler(call_back):
    message_text_data = call_back.message.text.split("\n\n")
    answer = "{0}\n\n{1}\n<b>{2}</b>\n{3}\n\nТипы: <b>{4}</b>\n\n" \
             "Дни: <b>{5}</b>\n\nВремя: <b>{6}</b>\n\n" \
             "Выбери, у каких преподавателей скрывать занятие:".format(
                      message_text_data[0], message_text_data[1].split("\n")[0],
                      message_text_data[1].split("\n")[1],
                      "\n".join(message_text_data[1].split("\n")[2:]),
                      message_text_data[2].split(": ")[1],
                      message_text_data[3].split(": ")[1],
                      call_back.data)
    place_educator_keyboard = InlineKeyboardMarkup(True)
    place_educator_keyboard.row(
        *[InlineKeyboardButton(text=name, callback_data=name) for
          name in ["Данные преподаватели"]]
    )
    place_educator_keyboard.row(
        *[InlineKeyboardButton(text=name, callback_data=name) for
          name in ["Отмена", "Любые"]]
    )
    bot.edit_message_text(text=answer,
                          chat_id=call_back.message.chat.id,
                          message_id=call_back.message.message_id,
                          parse_mode="HTML",
                          reply_markup=place_educator_keyboard)


@bot.callback_query_handler(func=lambda call_back:
                            "Выбери, у каких преподавателей скрывать занятие:"
                            in call_back.message.text)
def confirm_hide_lesson_handler(call_back):
    message_text_data = call_back.message.text.split("\n\n")
    hide_event_name = message_text_data[1].split("\n")[1]

    hide_event_types = message_text_data[2].split(": ")[1]
    if hide_event_types == "Любой тип":
        hide_event_types = "all"
    else:
        chosen_types = hide_event_types.split("; ")
        hide_event_types = ""
        for short_type in chosen_types:
            if short_type in subject_short_type.values():
                hide_event_types += func.get_key_by_value(subject_short_type,
                                                          short_type)
            else:
                hide_event_types += short_type.lower()
            hide_event_types += "; "
    hide_event_types = hide_event_types.strip("; ")

    hide_day = message_text_data[3].split(": ")[1]
    if hide_day == "Все дни":
        hide_day = "all"
    else:
        hide_day = hide_day.split(" ")[1]
        if hide_day[-1] == "и":
            hide_day = hide_day[:-1]
        else:
            hide_day = "{0}а".format(hide_day[:-1])

    hide_time = message_text_data[4].split(": ")[1]
    if hide_time == "Любое время":
        hide_time = "all"

    hide_educators = ""
    for place_edu in message_text_data[1].split("\n")[2:]:
        pos = place_edu.find("(")
        if pos != -1:
            hide_educators += place_edu[pos + 1:-1] + "; "
    hide_educators = hide_educators.strip("; ")
    if call_back.data == "Любые" or hide_educators == "":
        hide_educators = "all"

    func.insert_skip(hide_event_name, hide_event_types, hide_day, hide_time,
                     hide_educators, call_back.message.chat.id)
    answer = "<b>Занятие скрыто:</b>\n{0}".format(hide_event_name)
    bot.edit_message_text(text=answer,
                          chat_id=call_back.message.chat.id,
                          message_id=call_back.message.message_id,
                          parse_mode="HTML")


@bot.callback_query_handler(func=lambda call_back:
                            call_back.data == "Занятия")
def return_lesson(call_back):
    data = func.get_hide_lessons_data(call_back.message.chat.id)
    ids_keyboard = InlineKeyboardMarkup(row_width=5)
    if len(data):
        answer = "Вот список скрытых тобой занятий:\n\n"
        for lesson in data:
            answer += "<b>id: {0}</b>\n".format(lesson[0])
            if lesson[1] != "all":
                answer += "<b>Название</b>: {0}\n".format(lesson[1])

            if lesson[2] != "all":
                answer += "<b>Типы</b>: {0}\n".format(lesson[2])

            if lesson[3] != "all":
                answer += "<b>Дни</b>: {0}\n".format(lesson[3])

            if lesson[4] != "all":
                answer += "<b>Время</b>: {0}\n".format(lesson[4])

            if lesson[5] != "all":
                answer += "<b>Преподаватели</b>: {0}\n".format(lesson[5])

            answer += "\n"

            ids_keyboard.row(
                *[InlineKeyboardButton(
                    text=name, callback_data=name[:max_inline_button_text_len]
                ) for name in ["{0} - {1}".format(lesson[0], lesson[1])]]
            )
        ids_keyboard.row(
            *[InlineKeyboardButton(text=name, callback_data=name)
              for name in ["Отмена", "Вернуть всё"]]
        )
        answer += "Выбери то, которое хочешь вернуть:"
    else:
        answer = "Скрытых занятий нет"
    if len(answer) >= 3000:
        answers = answer.split("\n\n")
        for answer in answers[:-1]:
            bot.send_message(call_back.message.chat.id, answer,
                             parse_mode="HTML")
        answer = answers[-1]
        lesson_ids = [lesson[0] for lesson in data]

        if len(lesson_ids) < 31:
            ids_keyboard = InlineKeyboardMarkup(row_width=5)
            ids_keyboard.add(
                *[InlineKeyboardButton(text=name, callback_data=name)
                  for name in lesson_ids]
            )
            bot.send_message(call_back.message.chat.id, answer,
                             reply_markup=ids_keyboard, parse_mode="HTML")
        else:

            inline_answer = "Их слишком много..."
            bot.answer_callback_query(call_back.id, inline_answer, cache_time=1)
            for i in range(int(ceil(len(lesson_ids) / 30))):
                ids_keyboard = InlineKeyboardMarkup(row_width=5)
                ids_keyboard.add(
                    *[InlineKeyboardButton(text=name, callback_data=name)
                      for name in lesson_ids[:30]]
                )
                bot.send_message(call_back.message.chat.id, answer,
                                 reply_markup=ids_keyboard, parse_mode="HTML")
                lesson_ids = lesson_ids[30:]
            ids_keyboard = InlineKeyboardMarkup(row_width=5)
            ids_keyboard.row(*[InlineKeyboardButton(
                                                         text=name,
                                                         callback_data=name)
                               for name in ["Вернуть всё"]])
            bot.send_message(call_back.message.chat.id, answer,
                             reply_markup=ids_keyboard, parse_mode="HTML")
    else:
        bot.edit_message_text(text=answer, chat_id=call_back.message.chat.id,
                              message_id=call_back.message.message_id,
                              parse_mode="HTML", reply_markup=ids_keyboard)


@bot.callback_query_handler(func=lambda call_back:
                            call_back.data == "Вернуть всё")
def return_all_lessons(call_back):
    func.delete_all_hides(call_back.message.chat.id, hide_type=1)

    answer = "Все занятия возвращены"
    bot.edit_message_text(text=answer, chat_id=call_back.message.chat.id,
                          message_id=call_back.message.message_id)


@bot.callback_query_handler(func=lambda call_back:
                            "Выбери то, которое хочешь вернуть:" in
                            call_back.message.text)
def return_lesson_handler(call_back):
    lesson_id = call_back.data.split(" - ")[0]
    events = call_back.message.text.split("\n\n")[1:-1]
    lesson_title = ""
    for event in events:
        if event.split("\n")[0].split(": ")[1] == lesson_id:
            lesson_title = event.split("\n")[1].split(": ")[1]
            break
    sql_con = func.get_connection()
    cursor = sql_con.cursor()
    cursor.execute("""DELETE FROM skips 
                      WHERE user_id = %s
                        AND lesson_id = %s""",
                   (call_back.message.chat.id, lesson_id))
    sql_con.commit()
    cursor.close()
    sql_con.close()
    answer = "<b>Занятие возвращено:</b>\n{0}".format(lesson_title)
    bot.edit_message_text(text=answer, chat_id=call_back.message.chat.id,
                          message_id=call_back.message.message_id,
                          parse_mode="HTML")


@bot.callback_query_handler(func=lambda call_back:
                            call_back.data == "Преподавателей")
def return_educator(call_back):
    data = func.get_hide_lessons_data(call_back.message.chat.id,
                                      is_educator=True)
    ids_keyboard = InlineKeyboardMarkup(True)
    if len(data):
        answer = "Вот список занятий с выбранными преподавателями:\n\n"
        for lesson in data:
            answer += "<b>id: {0}</b>\n<b>Название</b>: {1}\n" \
                      "<b>Преподаватель</b>: {2}\n\n".format(
                                    lesson[0], lesson[1], lesson[5])
            ids_keyboard.row(
                *[InlineKeyboardButton(
                    text=name, callback_data=name[:max_inline_button_text_len]
                ) for name in ["{0} - {1}".format(lesson[0], lesson[1])]]
            )
        ids_keyboard.row(
            *[InlineKeyboardButton(text=name, callback_data=name)
              for name in ["Отмена", "Вернуть всех"]]
        )
        answer += "Выбери связь, которую хочешь убрать:"
    else:
        answer = "Скрытых преподавателей нет"
    if len(answer) >= 3000:
        answers = answer.split("\n\n")
        for answer in answers[:-1]:
            bot.send_message(call_back.message.chat.id, answer,
                             parse_mode="HTML")
        answer = answers[-1]
        bot.send_message(call_back.message.chat.id, answer,
                         reply_markup=ids_keyboard, parse_mode="HTML")
    else:
        bot.edit_message_text(text=answer, chat_id=call_back.message.chat.id,
                              message_id=call_back.message.message_id,
                              parse_mode="HTML", reply_markup=ids_keyboard)


@bot.callback_query_handler(func=lambda call_back:
                            call_back.data == "Вернуть всех")
def return_all_educators(call_back):
    func.delete_all_hides(call_back.message.chat.id, hide_type=2)

    answer = "Все преподаватели возвращены"
    bot.edit_message_text(text=answer, chat_id=call_back.message.chat.id,
                          message_id=call_back.message.message_id)


@bot.callback_query_handler(func=lambda call_back:
                            "Выбери связь, которую хочешь убрать:" in
                            call_back.message.text)
def return_lesson_handler(call_back):
    lesson_id = call_back.data.split(" - ")[0]
    events = call_back.message.text.split("\n\n")[1:-1]
    lesson_title = educator = ""
    for event in events:
        if event.split("\n")[0].split(": ")[1] == lesson_id:
            lesson_title = event.split("\n")[1].split(": ")[1]
            educator = event.split("\n")[2].split(": ")[1]
            break
    sql_con = func.get_connection()
    cursor = sql_con.cursor()
    cursor.execute("""DELETE FROM user_educators 
                      WHERE user_id = %s
                        AND lesson_id = %s""",
                   (call_back.message.chat.id, lesson_id))
    sql_con.commit()
    cursor.close()
    sql_con.close()
    answer = "<b>Связь убрана</b>\n{0} - {1}".format(
        lesson_title, educator)
    bot.edit_message_text(text=answer, chat_id=call_back.message.chat.id,
                          message_id=call_back.message.message_id,
                          parse_mode="HTML")


@bot.callback_query_handler(func=lambda call_back:
                            call_back.data == "Полный сброс")
def return_everything_handler(call_back):
    func.delete_all_hides(call_back.message.chat.id, hide_type=0)

    answer = "Все занятия и преподаватели возвращены"
    bot.edit_message_text(text=answer, chat_id=call_back.message.chat.id,
                          message_id=call_back.message.message_id)


@bot.callback_query_handler(func=lambda call_back:
                            call_back.data == "Статистика")
def statistics_handler(call_back):
    data = func.get_rate_statistics()
    if data is None:
        answer = "Пока что нет оценок."
    else:
        rate = emoji["star"] * int(round(data[0]))
        answer = "Средняя оценка: {0}\n{1} ({2})".format(
                                            round(data[0], 1), rate, data[1])
    if call_back.message.chat.id in ids.values():
        admin_data = func.get_statistics_for_admin()
        admin_answer = "\n\nКолличество пользователей: {0}\n" \
                       "Колличество групп: {1}\nКолличество пользователей с " \
                       "активной рассылкой: {2}".format(
                                    admin_data["count_of_users"],
                                    admin_data["count_of_groups"],
                                    admin_data["count_of_sending"])
        bot.send_message(call_back.message.chat.id, admin_answer)
    try:
        bot.edit_message_text(text=answer,
                              chat_id=call_back.message.chat.id,
                              message_id=call_back.message.message_id,
                              parse_mode="HTML")
    except ApiException:
        pass


@bot.callback_query_handler(func=lambda call_back:
                            call_back.data == "Связь")
def feedback_handler(call_back):
    markup = ForceReply(False)
    try:
        bot.edit_message_text(text="Обратная связь",
                              chat_id=call_back.message.chat.id,
                              message_id=call_back.message.message_id)
    except ApiException:
        pass
    finally:
        answer = "Напиши мне что-нибудь:"
        bot.send_message(call_back.message.chat.id, answer,
                         reply_markup=markup)


@bot.callback_query_handler(func=lambda call_back:
                            call_back.data == "Сохранить")
def save_current_group_handler(call_back):
    user_id = call_back.message.chat.id
    group_data = func.get_current_group(user_id)
    func.save_group(group_data[0], user_id)
    answer = "Группа <b>{0}</b> сохранена".format(group_data[1])
    bot.edit_message_text(text=answer,
                          chat_id=user_id,
                          message_id=call_back.message.message_id,
                          parse_mode="HTML")


@bot.callback_query_handler(func=lambda call_back:
                            call_back.data == "Удалить")
def delete_current_group_handler(call_back):
    user_id = call_back.message.chat.id
    group_data = func.get_current_group(user_id)
    func.delete_group(group_data[0], user_id)
    answer = "Группа <b>{0}</b> удалена".format(group_data[1])
    bot.edit_message_text(text=answer,
                          chat_id=user_id,
                          message_id=call_back.message.message_id,
                          parse_mode="HTML")


@bot.callback_query_handler(func=lambda call_back:
                            call_back.data == "Сменить группу")
def change_group_handler(call_back):
    answer = "{0}\nДля отмены используй /home".format(call_back.data)
    bot.edit_message_text(text=answer,
                          chat_id=call_back.message.chat.id,
                          message_id=call_back.message.message_id,
                          parse_mode="HTML")
    call_back.message.text = call_back.data
    start_handler(call_back.message)
    return


@bot.callback_query_handler(func=lambda call_back:
                            "Выбери группу:" in call_back.message.text)
def change_template_group_handler(call_back):
    answer = "Группа успешно изменена на <b>{0}</b>"
    chosen_group_id = int(call_back.data)
    sql_con = func.get_connection()
    cursor = sql_con.cursor()
    cursor.execute("""SELECT title
                      FROM groups_data
                      WHERE id = %s""", (chosen_group_id, ))
    group_title = cursor.fetchone()[0]
    cursor.execute("""UPDATE user_data 
                      SET group_id = %s
                      WHERE id = %s""",
                   (chosen_group_id, call_back.message.chat.id))
    sql_con.commit()
    cursor.close()
    sql_con.close()
    bot.edit_message_text(text=answer.format(group_title),
                          chat_id=call_back.message.chat.id,
                          message_id=call_back.message.message_id,
                          parse_mode="HTML")


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


@bot.callback_query_handler(func=lambda call_back:
                            "Выбери месяц" in call_back.message.text)
def select_months_att_handler(call_back):
    bot_msg = bot.edit_message_text(
        text="{0}\U00002026".format(choice(loading_text["schedule"])),
        chat_id=call_back.message.chat.id,
        message_id=call_back.message.message_id
    )
    json_attestation = func.get_json_attestation(call_back.message.chat.id)
    answer = ""
    is_full_place = func.is_full_place(call_back.message.chat.id)

    if call_back.message.text == "Выбери месяц:":
        schedule_variations = [(True, True), (False, True)]
    else:
        schedule_variations = [(True, False), (False, False)]

    for personal, only_exams in schedule_variations:
        answer += func.create_session_answer(json_attestation, call_back.data,
                                             call_back.message.chat.id,
                                             is_full_place, personal,
                                             only_exams)
        if answer:
            break
    if not answer:
        answer += "<i>Нет событий</i>"
    try:
        bot.edit_message_text(text=answer,
                              chat_id=call_back.message.chat.id,
                              message_id=bot_msg.message_id,
                              parse_mode="HTML")
    except ApiException:
        func.send_long_message(bot, answer, call_back.message.chat.id, "\n\n\n")


@bot.callback_query_handler(func=lambda call_back:
                            call_back.data in ["1", "2", "3", "4", "5"])
def set_rate_handler(call_back):
    rate = call_back.data
    answer = ""
    func.set_rate(call_back.message.chat.id, rate)
    if rate == "5":
        answer += "{0} Пятёрка! Супер! Спасибо большое!".format(emoji["smile"])
    elif rate == "4":
        answer += "{0} Стабильная четверочка. Спасибо!".format(emoji["halo"])
    elif rate == "3":
        answer += "{0} Удовлетворительно? Ничего... тоже оценка. " \
                  "Буду стараться лучше.".format(emoji["cold_sweat"])
    elif rate == "2":
        answer += "{0} Двойка? Быть может, я могу что-то исправить? " \
                  "Сделать лучше?\n\nОпиши проблему " \
                  "<a href='https://t.me/eeonedown'>разработчику</a>, " \
                  "и вместе мы ее решим!".format(emoji["disappointed"])
    elif rate == "1":
        answer += "{0} Единица? Быть может, я могу что-то исправить? " \
                  "Сделать лучше?\n\nОпиши проблему " \
                  "<a href='https://t.me/eeonedown'>разработчику</a>, " \
                  "и вместе мы ее решим!".format(emoji["disappointed"])
    user_rate = func.get_user_rate(call_back.message.chat.id)
    rate_keyboard = InlineKeyboardMarkup(row_width=5)
    rate_keyboard.add(*[InlineKeyboardButton(
        text=emoji["star2"] if user_rate < count_of_stars else emoji["star"],
        callback_data=str(count_of_stars))
        for count_of_stars in (1, 2, 3, 4, 5)])
    rate_keyboard.add(
        *[InlineKeyboardButton(text=name, callback_data=name)
          for name in ["Связь", "Статистика"]])
    try:
        bot.edit_message_text(text=answer,
                              chat_id=call_back.message.chat.id,
                              message_id=call_back.message.message_id,
                              parse_mode="HTML",
                              reply_markup=rate_keyboard,
                              disable_web_page_preview=True)
    except ApiException:
        pass
