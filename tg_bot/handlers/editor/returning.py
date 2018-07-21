# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from math import ceil

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from tg_bot import bot, functions as func
from app.constants import max_inline_button_text_len


# Return message
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


# Choose `lesson` callback
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


# Return all lessons callback
@bot.callback_query_handler(func=lambda call_back:
                            call_back.data == "Вернуть всё")
def return_all_lessons(call_back):
    func.delete_all_hides(call_back.message.chat.id, hide_type=1)

    answer = "Все занятия возвращены"
    bot.edit_message_text(text=answer, chat_id=call_back.message.chat.id,
                          message_id=call_back.message.message_id)


# Choose lesson callback
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


# Choose `educator` callback
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


# Return all educators callback
@bot.callback_query_handler(func=lambda call_back:
                            call_back.data == "Вернуть всех")
def return_all_educators(call_back):
    func.delete_all_hides(call_back.message.chat.id, hide_type=2)

    answer = "Все преподаватели возвращены"
    bot.edit_message_text(text=answer, chat_id=call_back.message.chat.id,
                          message_id=call_back.message.message_id)


# Return educator callback
@bot.callback_query_handler(func=lambda call_back:
                            "Выбери связь, которую хочешь убрать:" in
                            call_back.message.text)
def return_educator_handler(call_back):
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


# Return everything callback
@bot.callback_query_handler(func=lambda call_back:
                            call_back.data == "Полный сброс")
def return_everything_handler(call_back):
    func.delete_all_hides(call_back.message.chat.id, hide_type=0)

    answer = "Все занятия и преподаватели возвращены"
    bot.edit_message_text(text=answer, chat_id=call_back.message.chat.id,
                          message_id=call_back.message.message_id)
