# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from tg_bot import bot, functions as func
from app.constants import emoji, max_inline_button_text_len, server_timedelta, \
    week_day_titles, week_day_number


# Choose message
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


# `lesson` callback
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


# Time callback
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


# Lesson callback
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


# `educator` callback
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


# Day callback
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


# Lesson (for educator) callback
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


# Educator callback
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
