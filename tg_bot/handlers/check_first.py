# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from json import dumps

import spbu
from telebot.types import ReplyKeyboardMarkup, ReplyKeyboardRemove

import tg_bot.functions as func
import tg_bot.registration_functions as reg_func
from app import db
from app.constants import ids, emoji
from app.models import User
from tg_bot import bot
from tg_bot.keyboards import main_keyboard
from flask import current_app


# Start message
@bot.message_handler(commands=["start"])
@bot.message_handler(func=lambda mess:
                     mess.text.capitalize() == "Сменить группу",
                     content_types=["text"])
def start_handler(message):
    answer = ""

    if current_app.config["BOT_NAME"] != "Spbu4UBot" \
            and message.chat.id not in ids.values():
        answer = "Это тестовый бот. Используйте @Spbu4UBot"
        bot.send_message(message.chat.id, answer)
        return

    if message.text == "/start":
        answer = "Приветствую!\n"
    elif message.text.split()[1].isdecimal():
        answer = "Приветствую!\nДобавляю тебя в группу..."
        bot_msg = bot.send_message(message.chat.id, answer)
        try:
            group_id = int(message.text.split()[1])
        except ValueError:
            answer = "Ошибка в id группы."
            bot.edit_message_text(answer, message.chat.id,
                                  bot_msg.message_id)
            message.text = "/start"
            start_handler(message)
            return

        try:
            res = spbu.get_group_events(group_id)
        except spbu.ApiException:
            answer = "Ошибка в id группы."
            bot.edit_message_text(answer, message.chat.id, bot_msg.message_id)
            message.text = "/start"
            start_handler(message)
            return

        group_title = res["StudentGroupDisplayName"][7:]
        func.add_new_user(message.chat.id, group_id, group_title)
        answer = "Готово!\nГруппа <b>{0}</b>".format(group_title)
        bot.edit_message_text(answer, message.chat.id, bot_msg.message_id,
                              parse_mode="HTML")
        answer = "Главное меню\n\n" \
                 "{0} - информация о боте\n" \
                 "{1} - оценить бота\n" \
                 "{2} - настройки\n" \
                 "{3} - электрички\n" \
                 "{4} - <b>редактор расписания</b>\n" \
                 "@Spbu4u_news - новости бота".format(emoji["info"],
                                                      emoji["star"],
                                                      emoji["settings"],
                                                      emoji["suburban"],
                                                      emoji["editor"])
        bot.send_message(chat_id=message.chat.id, text=answer,
                         reply_markup=main_keyboard,
                         parse_mode="HTML")
        return
    answer += "Загружаю список направлений..."
    bot_msg = bot.send_message(message.chat.id, answer)
    bot.send_chat_action(message.chat.id, "typing")
    answer = "Укажи свое направление:"
    divisions = spbu.get_study_divisions()
    division_names = [division["Name"] for division in divisions]
    divisions_keyboard = ReplyKeyboardMarkup(True, False)
    for division_name in division_names:
        divisions_keyboard.row(division_name)
    divisions_keyboard.row("Поддержка", "Завершить")
    data = dumps(divisions)

    sql_con = func.get_connection()
    cursor = sql_con.cursor()
    cursor.execute("""DELETE FROM user_choice WHERE user_id = %s""",
                   (message.chat.id, ))
    sql_con.commit()
    cursor.execute("""INSERT INTO user_choice (user_id, divisions_json)
                      VALUES (%s, %s)""", (message.chat.id, data))
    sql_con.commit()
    cursor.close()
    sql_con.close()
    bot.edit_message_text(text="Готово!", chat_id=message.chat.id,
                          message_id=bot_msg.message_id)
    bot.send_message(message.chat.id, answer, reply_markup=divisions_keyboard)
    reg_func.set_next_step(message.chat.id, "select_division")


# Support message
@bot.message_handler(func=lambda mess: mess.text.capitalize() == "Поддержка",
                     content_types=["text"])
def problem_text_handler(message):
    bot.send_chat_action(message.chat.id, "typing")
    answer = "Если возникла проблема, то:\n" \
             "1. Возможно, информация по этому поводу есть в нашем канале" \
             " - @Spbu4u_news;\n" \
             "2. Ты всегда можешь связаться с " \
             "<a href='https://t.me/eeonedown'>разработчиком</a>."
    bot.send_message(message.chat.id, answer,
                     disable_web_page_preview=True,
                     parse_mode="HTML")


# Exit message
@bot.message_handler(commands=["exit"])
@bot.message_handler(func=lambda mess: mess.text.capitalize() == "Завершить",
                     content_types=["text"])
def exit_handler(message):
    bot.send_chat_action(message.chat.id, "typing")
    User.query.filter_by(telegram_id=message.chat.id).delete()
    db.session.commit()
    remove_keyboard = ReplyKeyboardRemove(True)
    answer = "До встречи!"
    bot.send_message(message.chat.id, answer, reply_markup=remove_keyboard)
