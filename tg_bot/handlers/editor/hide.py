# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from flask import g

from tg_bot import bot, functions as func
from app.constants import (
    emoji, max_inline_button_text_len, subject_short_types, hide_answer,
    hide_lesson_answer, selected_lesson_info_answer, ask_to_select_types_answer
)
from app import new_functions as nf
import telebot_login
from tg_bot.keyboards import week_day_keyboard, events_keyboard, types_keyboard


# Hide message
@bot.message_handler(
    func=lambda mess: mess.text.capitalize() == "Скрыть",
    content_types=["text"]
)
@telebot_login.login_required_message
def hide_lesson_handler(message):
    user = g.current_tbot_user

    bot.send_chat_action(user.tg_id, "typing")

    bot.send_message(
        chat_id=user.tg_id,
        text=hide_answer,
        reply_markup=week_day_keyboard(for_editor=True)
    )


# Weekday callback
@bot.callback_query_handler(
    func=lambda call_back: call_back.message.text == hide_answer
)
@telebot_login.login_required_callback
def select_day_hide_lesson_handler(call_back):
    user = g.current_tbot_user

    bot_msg = bot.edit_message_text(
        text="Разбиваю занятия на пары\U00002026",
        chat_id=user.tg_id,
        message_id=call_back.message.message_id
    )
    answer = user.get_block_answer(
        for_date=nf.get_date_by_weekday_title(call_back.data),
        block_num=1
    )
    bot.edit_message_text(
        text=answer,
        chat_id=user.tg_id,
        message_id=bot_msg.message_id,
        reply_markup=events_keyboard(answer)
    )


# next_block callback
@bot.callback_query_handler(
    func=lambda call_back: call_back.data == "next_block"
)
# prev_block callback
@bot.callback_query_handler(
    func=lambda call_back: call_back.data == "prev_block"
)
@telebot_login.login_required_callback
def select_block_handler(call_back):
    user = g.current_tbot_user

    blocks_count, cur_block_num, for_date = nf.get_block_data_from_block_answer(
        call_back.message.text
    )
    if blocks_count == 1:
        bot.answer_callback_query(
            call_back.id, "Доступна только одна пара", cache_time=2
        )
        return

    is_next_block = call_back.data == "next_block"

    bot_msg = bot.edit_message_text(
        text="Смотрю {0} пару\U00002026".format(
            "следующую" if is_next_block else "предыдущую"
        ),
        chat_id=call_back.message.chat.id,
        message_id=call_back.message.message_id
    )
    answer = user.get_block_answer(
        for_date=for_date,
        block_num=cur_block_num + (1 if is_next_block else -1)
    )
    bot.edit_message_text(
        text=answer,
        chat_id=user.tg_id,
        message_id=bot_msg.message_id,
        reply_markup=events_keyboard(answer)
    )


# Lesson callback
@bot.callback_query_handler(
    func=lambda call_back: hide_lesson_answer in call_back.message.text
)
@telebot_login.login_required_callback
def select_lesson_handler(call_back):
    user = g.current_tbot_user

    event_data = nf.get_event_data_from_block_answer(
        text=call_back.message.text,
        idx=int(call_back.data)
    )
    answer = selected_lesson_info_answer.format(
        *event_data
    ) + ask_to_select_types_answer

    bot.edit_message_text(
        text=answer,
        chat_id=user.tg_id,
        message_id=call_back.message.message_id,
        parse_mode="HTML",
        reply_markup=types_keyboard(event_type=event_data[2])
    )


# Next callback
@bot.callback_query_handler(
    func=lambda call_back: call_back.data == "Далее"
)
@telebot_login.login_required_callback
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
@bot.callback_query_handler(
    func=lambda call_back: ask_to_select_types_answer in call_back.message.text
)
@telebot_login.login_required_callback
def select_types_handler(call_back):
    user = g.current_tbot_user

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
    short_types = [short_type for short_type in subject_short_types.values()]
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
            if short_type in subject_short_types.values():
                hide_event_types += func.get_key_by_value(subject_short_types,
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
