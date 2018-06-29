# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

import bot.functions as func
from bot import bot
from app.constants import emoji
from bot.handlers.check_first import start_handler


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
