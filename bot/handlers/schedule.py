# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime, timedelta
from random import choice

import spbu
from telebot.apihelper import ApiException
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ForceReply

import bot.functions as func
from bot import bot
from bot.bots_constants import bot_name
from bot.constants import server_timedelta, emoji, week_day_number, \
    week_day_titles, loading_text
from bot.handlers.check_first import start_handler
from bot.keyboards import schedule_keyboard


# Today schedule message
@bot.message_handler(func=lambda mess: mess.text.capitalize() == "Сегодня",
                     content_types=["text"])
def today_schedule_handler(message):
    bot.send_chat_action(message.chat.id, "typing")
    today_moscow_datetime = datetime.today() + server_timedelta
    today_moscow_date = today_moscow_datetime.date()
    json_day = func.get_json_day_data(message.chat.id, today_moscow_date)
    full_place = func.is_full_place(message.chat.id)
    answer = func.create_schedule_answer(json_day, full_place, message.chat.id)
    func.send_long_message(bot, answer, message.chat.id)


# Tomorrow schedule message
@bot.message_handler(func=lambda mess: mess.text.capitalize() == "Завтра",
                     content_types=["text"])
def tomorrow_schedule_handler(message):
    bot.send_chat_action(message.chat.id, "typing")
    tomorrow_moscow_datetime = datetime.today() + server_timedelta + \
        timedelta(days=1)
    tomorrow_moscow_date = tomorrow_moscow_datetime.date()
    json_day = func.get_json_day_data(message.chat.id, tomorrow_moscow_date)
    full_place = func.is_full_place(message.chat.id)
    answer = func.create_schedule_answer(json_day, full_place, message.chat.id)
    func.send_long_message(bot, answer, message.chat.id)


# Week schedule message
@bot.message_handler(func=lambda mess: mess.text.capitalize() == "Неделя",
                     content_types=["text"])
def calendar_handler(message):
    bot.send_chat_action(message.chat.id, "typing")
    answer = "Выбери день:"
    week_day_calendar = InlineKeyboardMarkup()
    week_day_calendar.row(
        *[InlineKeyboardButton(text=name, callback_data=name) for
          name in week_day_number.keys()])
    week_day_calendar.row(
        *[InlineKeyboardButton(text=name, callback_data=name) for
          name in ["Вся неделя"]])
    bot.send_message(message.chat.id, answer, reply_markup=week_day_calendar)


# Schedule sending message
@bot.message_handler(func=lambda mess: mess.text == emoji["alarm_clock"],
                     content_types=["text"])
def sending_handler(message):
    bot.send_chat_action(message.chat.id, "typing")
    answer = "Здесь ты можешь <b>подписаться</b> на рассылку расписания на " + \
             "следующий день или <b>отписаться</b> от неё.\n" + \
             "Рассылка производится в 21:00"
    sending_keyboard = InlineKeyboardMarkup(True)
    if func.is_sending_on(message.chat.id):
        sending_keyboard.row(
            *[InlineKeyboardButton(text=name, callback_data="Отписаться")
              for name in [emoji["cross_mark"] + " Отписаться"]])
    else:
        sending_keyboard.row(
            *[InlineKeyboardButton(text=name, callback_data="Подписаться")
              for name in [emoji["check_mark"] + " Подписаться"]])
    bot.send_message(message.chat.id, answer, parse_mode="HTML",
                     reply_markup=sending_keyboard)


# Week schedule callback
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


# All week schedule callback
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


# Week type callback
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


# Activate sending callback
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


# Deactivate sending callback
@bot.callback_query_handler(func=lambda call_back:
                            call_back.data == "Отписаться")
def sending_off_handler(call_back):
    func.set_sending(call_back.message.chat.id, False)
    answer = "{0} Рассылка <b>отключена</b>".format(emoji["mailbox_off"])
    bot.edit_message_text(text=answer,
                          chat_id=call_back.message.chat.id,
                          message_id=call_back.message.message_id,
                          parse_mode="HTML")


# Groups templates message
@bot.message_handler(func=lambda mess:
                     mess.text == emoji["arrows_counterclockwise"],
                     content_types=["text"])
def group_templates_handler(message):
    bot.send_chat_action(message.chat.id, "typing")
    answer = ""
    groups = func.get_templates(message.chat.id)
    group_title = func.get_current_group(message.chat.id)[1]
    answer += "Текущая группа: <b>{0}</b>\n".format(group_title)
    last_row = ["Отмена", "Сохранить"]
    inline_keyboard = InlineKeyboardMarkup(row_width=2)
    if len(groups) == 0:
        answer += "Нет шаблонов групп, но ты можешь сохранить текущую\n"
    else:
        answer += "Выбери группу:"
        inline_keyboard.add(
            *[InlineKeyboardButton(
                text=name, callback_data=str(groups[name]))
                for name in groups.keys()]
        )
        if group_title in groups.keys():
            last_row = ["Отмена", "Удалить"]
    inline_keyboard.row(
        *[InlineKeyboardButton(text=name, callback_data=name)
            for name in last_row]
    )
    inline_keyboard.row(
        *[InlineKeyboardButton(text=name, callback_data=name)
          for name in ["Сменить группу"]]
    )
    bot.send_message(message.chat.id, answer, reply_markup=inline_keyboard,
                     parse_mode="HTML")


# Educator search message
@bot.message_handler(func=lambda mess: mess.text == emoji["bust_in_silhouette"],
                     content_types=["text"])
def educator_schedule_handler(message):
    bot.send_chat_action(message.chat.id, "typing")
    answer = "Введи Фамилию преподавателя: <i>(и И. О.)</i>"
    markup = ForceReply(False)
    bot.send_message(message.chat.id, answer, reply_markup=markup,
                     parse_mode="HTML")


# Educator name (Force reply) message
@bot.message_handler(
    func=lambda mess:
        mess.reply_to_message is not None and
        mess.reply_to_message.from_user.username == bot_name and
        "Введи Фамилию преподавателя:" in mess.reply_to_message.text,
    content_types=["text"])
def write_educator_name_handler(message):
    bot.send_chat_action(message.chat.id, "typing")
    answer = ""
    name = message.text.strip(". ")
    if not func.is_correct_educator_name(name):
        answer = "Недопустимые символы"
        bot.send_message(message.chat.id, answer,
                         reply_markup=schedule_keyboard)
        return

    try:
        educators_data = spbu.search_educator(name)
    except spbu.ApiException:
        answer = "Во время выполнения запроса произошла ошибка."
        bot.send_message(message.chat.id, answer,
                         reply_markup=schedule_keyboard)
        return

    if not educators_data["Educators"]:
        answer = "Никого не найдено"
        bot.send_message(message.chat.id, answer,
                         reply_markup=schedule_keyboard)
    elif len(educators_data["Educators"]) > 200:
        answer = "Слишком много преподавателей\n" \
                 "Пожалуйста, <b>уточни</b>"
        bot.send_message(message.chat.id, answer, parse_mode="HTML")
        answer = "Введи Фамилию преподавателя: <i>(и И. О.)</i>"
        markup = ForceReply(False)
        bot.send_message(message.chat.id, answer, reply_markup=markup,
                         parse_mode="HTML")
    else:
        bot.send_message(message.chat.id, "Готово!",
                         reply_markup=schedule_keyboard)

        educators_keyboard = InlineKeyboardMarkup(row_width=2)
        educators_keyboard.add(
            *[InlineKeyboardButton(text=educator["DisplayName"],
                                   callback_data=str(educator["Id"]))
              for educator in educators_data["Educators"]])
        educators_keyboard.row(InlineKeyboardButton(
            text="Отмена", callback_data="Отмена"))
        answer = "{0} Найденные преподаватели:\n\n".format(
            emoji["mag_right"]) + answer
        bot.send_message(message.chat.id, answer,
                         reply_markup=educators_keyboard, parse_mode="HTML")


# Now lesson message
@bot.message_handler(func=lambda mess: mess.text.title() == "Сейчас",
                     content_types=["text"])
@bot.message_handler(func=lambda mess:
                     mess.text.capitalize() == "Что сейчас?",
                     content_types=["text"])
def now_lesson_handler(message):
    answer = "Наверно, какая-то пара #пасхалочка"
    func.send_long_message(bot, answer, message.chat.id)


# Schedule for date message
@bot.message_handler(func=lambda mess: func.text_to_date(mess.text.lower()),
                     content_types=["text"])
def schedule_for_day(message):
    bot.send_chat_action(message.chat.id, "typing")
    day = func.text_to_date(message.text.lower())
    json_week = func.get_json_week_data(message.chat.id, for_day=day)
    json_day = func.get_json_day_data(message.chat.id, day_date=day,
                                      json_week_data=json_week)
    full_place = func.is_full_place(message.chat.id)
    answer = func.create_schedule_answer(json_day, full_place,
                                         user_id=message.chat.id,
                                         personal=True)
    func.send_long_message(bot, answer, message.chat.id)


# Schedule for week title message
@bot.message_handler(func=lambda mess:
                     mess.text.title() in week_day_titles.keys(),
                     content_types=["text"])
@bot.message_handler(func=lambda mess:
                     mess.text.title() in week_day_titles.values(),
                     content_types=["text"])
def schedule_for_weekday(message):
    bot.send_chat_action(message.chat.id, "typing")
    message.text = message.text.title()
    if message.text in week_day_titles.values():
        week_day = message.text
    else:
        week_day = week_day_titles[message.text]

    day_date = func.get_day_date_by_weekday_title(week_day)
    json_day = func.get_json_day_data(message.chat.id, day_date)
    full_place = func.is_full_place(message.chat.id)
    answer = func.create_schedule_answer(json_day, full_place,
                                         message.chat.id)
    func.send_long_message(bot, answer, message.chat.id)


# Save group callback
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


# Delete group callback
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


# Change group callback
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


# Choose group callback
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


# Choose educator callback
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
