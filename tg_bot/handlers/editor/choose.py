# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from flask import g

from tg_bot import bot, functions as func
from tg_bot.keyboards import (
    choose_keyboard, selectable_blocks_keyboard, block_lessons_keyboard
)
from app.constants import (
    emoji, max_inline_button_text_len, server_timedelta, week_day_titles,
    week_day_number, choose_answer, ask_to_select_block_answer,
    no_blocks_answer, ask_to_select_block_lesson_answer, no_edu_days_answer,
    ask_to_select_day_answer
)
import telebot_login
from app import db


@bot.message_handler(
    func=lambda mess: mess.text.capitalize() == "Выбрать",
    content_types=["text"]
)
@telebot_login.login_required_message
@telebot_login.student_required_message
def choose_educator_handler(message):
    user = g.current_tbot_user

    bot.send_message(
        chat_id=user.tg_id,
        text=choose_answer,
        reply_markup=choose_keyboard()
    )


@bot.callback_query_handler(
    func=lambda call_back: call_back.data == "Занятие"
)
@telebot_login.login_required_callback
@telebot_login.student_required_callback
def editor_choose_lesson_handler(call_back):
    user = g.current_tbot_user

    blocks = user.get_selectable_blocks()

    bot.edit_message_text(
        text=ask_to_select_block_answer if len(blocks) else no_blocks_answer,
        chat_id=user.tg_id,
        message_id=call_back.message.message_id,
        reply_markup=selectable_blocks_keyboard(blocks.keys())
    )


@bot.callback_query_handler(
    func=lambda call_back: ask_to_select_block_answer in call_back.message.text
)
@telebot_login.login_required_callback
@telebot_login.student_required_callback
def select_block_choose_lesson_handler(call_back):
    user = g.current_tbot_user

    bot.edit_message_text(
        chat_id=call_back.message.chat.id,
        text="{0} {1}".format(emoji["calendar"], call_back.data),
        message_id=call_back.message.message_id
    )
    block = user.get_selectable_blocks()[call_back.data]

    bot.send_message(
        chat_id=user.tg_id,
        text=user.parse_selectable_block(block),
        reply_markup=block_lessons_keyboard(block),
        parse_mode="HTML"
    )


@bot.callback_query_handler(
    func=lambda call_back:
        ask_to_select_block_lesson_answer in call_back.message.text
)
@telebot_login.login_required_callback
@telebot_login.student_required_callback
def lesson_chosen_handler(call_back):
    user = g.current_tbot_user

    answer = user.hide_block_lessons(
        text=call_back.message.text,
        chosen_idx=int(call_back.data)
    )
    db.session.commit()

    bot.edit_message_text(
        text=answer,
        chat_id=user.tg_id,
        message_id=call_back.message.message_id,
        parse_mode="HTML"
    )


"""
    Дальше не работает!
"""


@bot.callback_query_handler(
    func=lambda call_back: call_back.data == "Преподавателя"
)
@telebot_login.login_required_callback
@telebot_login.student_required_callback
@telebot_login.educator_required_callback   # Убрать
def editor_choose_educator_handler(call_back):
    user = g.current_tbot_user

    answer = ask_to_select_day_answer
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
        answer = no_edu_days_answer

    bot.edit_message_text(
        text=answer,
        chat_id=user.tg_id,
        message_id=call_back.message.message_id,
        reply_markup=days_keyboard
    )


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
