# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime
from math import ceil

from telebot.apihelper import ApiException
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot import bot, functions as func
from bot.constants import emoji, max_inline_button_text_len, server_timedelta, \
    subject_short_type, week_day_titles, week_day_number


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


@bot.message_handler(func=lambda mess:
                     mess.text.capitalize() == "Выбрать",
                     content_types=["text"])
def choose_educator_handler(message):
    bot.send_chat_action(message.chat.id, "typing")
    answer = "Здесь ты можешь выбрать для отображения занятие или " \
             "преподавателя:"
    inline_keyboard = InlineKeyboardMarkup(True)
    inline_keyboard.row(
        *[InlineKeyboardButton(text=name, callback_data=name)
          for name in ["Преподавателя", "Занятие"]])
    bot.send_message(message.chat.id, answer, reply_markup=inline_keyboard)


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


@bot.message_handler(func=lambda mess: mess.text.title() == "Вернуть",
                     content_types=["text"])
def chose_to_return(message):
    bot.send_chat_action(message.chat.id, "typing")
    answer = "Выбери, что ты хочешь вернуть:"
    inline_keyboard = InlineKeyboardMarkup(True)
    inline_keyboard.row(
        *[InlineKeyboardButton(text=name, callback_data=name)
          for name in ["Преподавателей", "Занятия"]])
    inline_keyboard.row(
        *[InlineKeyboardButton(text=name, callback_data=name)
          for name in ["Полный сброс"]])
    bot.send_message(message.chat.id, answer, reply_markup=inline_keyboard)


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
