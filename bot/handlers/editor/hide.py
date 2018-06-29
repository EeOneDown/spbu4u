# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime

from telebot.apihelper import ApiException
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot import bot, functions as func
from app.constants import emoji, max_inline_button_text_len, server_timedelta, \
    subject_short_type, week_day_titles, week_day_number


# Hide message
@bot.message_handler(func=lambda mess:
                     mess.text.capitalize() == "Скрыть",
                     content_types=["text"])
def hide_lesson_handler(message):
    bot.send_chat_action(message.chat.id, "typing")
    answer = "Здесь ты можешь скрыть любое занятие\n" \
             "Выбери день, когда есть это занятие:"
    json_week_data = func.get_json_week_data(message.chat.id)
    days = json_week_data["Days"]
    days_keyboard = InlineKeyboardMarkup(True)
    for day in days:
        days_keyboard.row(
            *[InlineKeyboardButton(text=name, callback_data=name)
              for name in [day["DayString"].split(", ")[0].capitalize()]])
    days_keyboard.row(
        *[InlineKeyboardButton(text=name, callback_data=name)
          for name in ["Отмена"]])
    bot.send_message(message.chat.id, answer, reply_markup=days_keyboard)


# Weekday callback
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


# next_block callback
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


# prev_block callback
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


# Lesson callback
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


# Next callback
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


# Type callback
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
        if short_types[i] in all_chosen_types:
            short_types[i] = "{0} {1}".format(emoji["heavy_check_mark"],
                                              short_types[i])
    types_keyboard.add(
        *[InlineKeyboardButton(text=name, callback_data=name)
          for name in short_types])
    if is_special_type:
        if chosen_type in all_chosen_types:
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


# Day callback
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


# Time callback
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


# Educator callback
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
