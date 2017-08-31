# -*- coding: utf-8 -*-
import telebot
import requests
import sqlite3
import logging
import json
import time
from datetime import datetime, timedelta
import flask
from flask_sslify import SSLify
import registration_functions as reg_func
import functions as func
from constants import test_token, emoji, briefly_info_answer, \
    full_info_answer, webhook_url_base, webhook_url_path, week_day_number


bot = telebot.TeleBot(test_token, threaded=False)
app = flask.Flask(__name__)
sslify = SSLify(app)

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

main_keyboard = telebot.types.ReplyKeyboardMarkup(True)
if time.localtime().tm_mon in [12, 1, 5, 6]:
    main_keyboard.row("СЕССИЯ", "Расписание")
else:
    main_keyboard.row("Расписание")
main_keyboard.row(emoji["info"], emoji["star"], emoji["settings"],
                  emoji["suburban"], emoji["editor"])


@bot.message_handler(commands=["start"])
def start_handler(message):
    answer = "Приветствую!\nУкажи свое направление:"
    divisions = requests.get(
        "https://timetable.spbu.ru/api/v1/divisions").json()
    division_names = [division["Name"] for division in divisions]
    divisions_keyboard = telebot.types.ReplyKeyboardMarkup(True, False)
    for division_name in division_names:
        divisions_keyboard.row(division_name)
    data = json.dumps(divisions)

    sql_con = sqlite3.connect("Bot_db")
    cursor = sql_con.cursor()
    cursor.execute("""DELETE FROM user_choice WHERE user_id = ?""",
                   (message.chat.id, ))
    sql_con.commit()
    cursor.execute("""INSERT INTO user_choice (user_id, divisions_json)
                      VALUES (?, ?)""", (message.chat.id, data))
    sql_con.commit()
    cursor.close()
    sql_con.close()
    bot.send_message(message.chat.id, answer,
                     reply_markup=divisions_keyboard)
    func.set_next_step(message.chat.id, "select_division")


@bot.message_handler(commands=["help"])
@bot.message_handler(func=lambda mess: mess.text == emoji["info"],
                     content_types=["text"])
def help_handler(message):
    inline_full_info_keyboard = telebot.types.InlineKeyboardMarkup()
    inline_full_info_keyboard.row(
        *[telebot.types.InlineKeyboardButton(text=name, callback_data=name) for
          name in ["Полное ИНФО"]])
    answer = briefly_info_answer
    bot.send_message(message.chat.id, answer,
                     parse_mode="Markdown",
                     reply_markup=inline_full_info_keyboard,
                     disable_web_page_preview=True)


@bot.message_handler(commands=["home"])
@bot.message_handler(func=lambda mess: mess.text == "Назад",
                     content_types=["text"])
def home_handler(message):
    func.delete_user(message.chat.id, only_choice=True)
    answer = "Главное меню"
    bot.send_message(message.chat.id, answer, reply_markup=main_keyboard)


@bot.message_handler(commands=["settings"])
@bot.message_handler(func=lambda mess: mess.text == emoji["settings"],
                     content_types=["text"])
def settings_handler(message):
    func.delete_user(message.chat.id, only_choice=True)
    answer = "Главное меню"
    bot.send_message(message.chat.id, answer, reply_markup=main_keyboard)


@bot.message_handler(func=lambda mess: mess.text == "Расписание",
                     content_types=["text"])
def schedule_handler(message):
    answer = "Меню расписания"
    schedule_keyboard = telebot.types.ReplyKeyboardMarkup(True)
    schedule_keyboard.row("Сегодня", "Завтра", emoji["calendar"])
    schedule_keyboard.row("Назад", emoji["alarm_clock"])
    bot.send_message(message.chat.id, answer, reply_markup=schedule_keyboard)


@bot.message_handler(func=lambda mess: mess.text == "Сегодня")
def today_schedule_handler(message):
    today_moscow_date = datetime.today().date() + timedelta(hours=3)
    json_day = func.get_json_day_data(message.chat.id, today_moscow_date)
    answer = func.get_schedule(json_day)
    bot.send_message(message.chat.id, answer, parse_mode="HTML")


@bot.message_handler(func=lambda mess: mess.text == "Завтра")
def tomorrow_schedule_handler(message):
    tomorrow_moscow_date = datetime.today().date() + timedelta(days=1, hours=3)
    json_day = func.get_json_day_data(message.chat.id, tomorrow_moscow_date)
    answer = func.get_schedule(json_day)
    bot.send_message(message.chat.id, answer, parse_mode="HTML")


@bot.message_handler(func=lambda mess: mess.text == emoji["calendar"])
def calendar_handler(message):
    answer = "Выбери день:"
    week_day_calendar = telebot.types.InlineKeyboardMarkup()
    week_day_calendar.row(
        *[telebot.types.InlineKeyboardButton(text=name, callback_data=name) for
          name in week_day_number.keys()])
    bot.send_message(message.chat.id, answer, reply_markup=week_day_calendar)


@bot.message_handler(func=lambda mess:
                     func.get_step(mess.chat.id) == "select_division",
                     content_types=["text"])
def select_division_handler(message):
    reg_func.select_division(message)
    return


@bot.message_handler(func=lambda mess:
                     func.get_step(mess.chat.id) == "select_study_level",
                     content_types=["text"])
def select_study_level_handler(message):
    reg_func.select_study_level(message)
    return


@bot.message_handler(func=lambda mess: func.get_step(
    mess.chat.id) == "select_study_program_combination",
                     content_types=["text"])
def select_study_program_combination_handler(message):
    reg_func.select_study_program_combination(message)
    return


@bot.message_handler(func=lambda mess:
                     func.get_step(mess.chat.id) == "select_admission_year",
                     content_types=["text"])
def select_admission_year_handler(message):
    reg_func.select_admission_year(message)
    return


@bot.message_handler(func=lambda mess:
                     func.get_step(mess.chat.id) == "select_student_group",
                     content_types=["text"])
def select_student_group_handler(message):
    reg_func.select_student_group(message)
    return


@bot.message_handler(func=lambda mess:
                     func.get_step(mess.chat.id) == "confirm_choice",
                     content_types=["text"])
def confirm_choice_handler(message):
    reg_func.confirm_choice(message)
    return


@bot.message_handler(func=lambda mess: True, content_types=["text"])
def other_text_handler(message):
    answer = "Некоторые функии сейчас недоступны.\n Подробнее - @Spbu4u_news"
    bot.send_message(message.chat.id, answer)


@bot.callback_query_handler(func=lambda call_back:
                            call_back.data == "Полное ИНФО")
def show_full_info(call_back):
    inline_keyboard = telebot.types.InlineKeyboardMarkup()
    inline_keyboard.row(
        *[telebot.types.InlineKeyboardButton(text=name, callback_data=name) for
          name in ["Краткое ИНФО"]])
    answer = full_info_answer
    bot.edit_message_text(text=answer,
                          chat_id=call_back.message.chat.id,
                          message_id=call_back.message.message_id,
                          parse_mode="Markdown",
                          disable_web_page_preview=True,
                          reply_markup=inline_keyboard)


@bot.callback_query_handler(func=lambda call_back:
                            call_back.data == "Краткое ИНФО")
def show_briefly_info(call_back):
    inline_keyboard = telebot.types.InlineKeyboardMarkup()
    inline_keyboard.row(
        *[telebot.types.InlineKeyboardButton(text=name, callback_data=name) for
          name in ["Полное ИНФО"]])
    answer = briefly_info_answer
    bot.edit_message_text(text=answer,
                          chat_id=call_back.message.chat.id,
                          message_id=call_back.message.message_id,
                          parse_mode="Markdown",
                          disable_web_page_preview=True,
                          reply_markup=inline_keyboard)


@bot.callback_query_handler(func=lambda call_back:
                            call_back.data in week_day_number.keys())
def week_day_schedule_handler(call_back):
    iso_day_date = list((datetime.today() + timedelta(hours=3)).isocalendar())
    if iso_day_date[2] == 7:
        iso_day_date[1] += 1
    iso_day_date[2] = week_day_number[call_back.data]
    day_date = func.date_from_iso(iso_day_date)
    json_day = func.get_json_day_data(call_back.message.chat.id, day_date)
    answer = func.get_schedule(json_day)
    bot.edit_message_text(text=answer,
                          chat_id=call_back.message.chat.id,
                          message_id=call_back.message.message_id,
                          parse_mode="HTML")


@app.route("/reset_webhook", methods=["GET", "HEAD"])
def reset_webhook():
    bot.remove_webhook()
    bot.set_webhook(url=webhook_url_base + webhook_url_path)
    return "OK", 200


@app.route("/", methods=["GET", "HEAD"])
def main_page():
    page = "<a href='https://t.me/Spbu4UBot'>@SPbU4U</a>"
    return page, 200


@app.route(webhook_url_path, methods=["POST"])
def webhook():
    if flask.request.headers.get("content-type") == "application/json":
        json_string = flask.request.get_data().decode("utf-8")
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "OK", 200
    else:
        flask.abort(403)


if __name__ == '__main__':
    bot.remove_webhook()
    bot.polling(none_stop=True, interval=0)
