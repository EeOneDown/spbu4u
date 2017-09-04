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
from sql_updater import schedule_update
from constants import release_token, emoji, briefly_info_answer, my_id, \
    full_info_answer, webhook_url_base, webhook_url_path, week_day_number


bot = telebot.TeleBot(release_token, threaded=False)
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
@bot.message_handler(func=lambda mess: mess.text == "Сменить группу",
                     content_types=["text"])
def start_handler(message):
    answer = ""
    if message.text == "/start":
        answer += "Приветствую!\n"
    answer += "Укажи свое направление:"
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


@bot.message_handler(func=lambda mess:
                     func.get_step(mess.chat.id) == "select_division" and
                     mess.text != "/home" and mess.text != "Назад",
                     content_types=["text"])
def select_division_handler(message):
    reg_func.select_division(message)
    return


@bot.message_handler(func=lambda mess:
                     func.get_step(mess.chat.id) == "select_study_level" and
                     mess.text != "/home" and mess.text != "Назад",
                     content_types=["text"])
def select_study_level_handler(message):
    reg_func.select_study_level(message)
    return


@bot.message_handler(func=lambda mess: func.get_step(
    mess.chat.id) == "select_study_program_combination" and
                     mess.text != "/home" and mess.text != "Назад",
                     content_types=["text"])
def select_study_program_combination_handler(message):
    reg_func.select_study_program_combination(message)
    return


@bot.message_handler(func=lambda mess:
                     func.get_step(mess.chat.id) == "select_admission_year" and
                     mess.text != "/home" and mess.text != "Назад",
                     content_types=["text"])
def select_admission_year_handler(message):
    reg_func.select_admission_year(message)
    return


@bot.message_handler(func=lambda mess:
                     func.get_step(mess.chat.id) == "select_student_group" and
                     mess.text != "/home" and mess.text != "Назад",
                     content_types=["text"])
def select_student_group_handler(message):
    reg_func.select_student_group(message)
    return


@bot.message_handler(func=lambda mess:
                     func.get_step(mess.chat.id) == "confirm_choice" and
                     mess.text != "/home" and mess.text != "Назад",
                     content_types=["text"])
def confirm_choice_handler(message):
    reg_func.confirm_choice(message)
    return


@bot.message_handler(func=lambda mess: not func.is_user_exist(mess.chat.id),
                     content_types=["text"])
def not_exist_user_handler(message):
    answer = "Чтобы начать пользоваться сервисом, необходимо зарегистрироваться"
    answer += ".\nВоспользуйся коммандой /start"
    bot.send_message(message.chat.id, answer)


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
    settings_keyboard = telebot.types.ReplyKeyboardMarkup(True)
    settings_keyboard.row("Сменить группу", "Завершить")
    settings_keyboard.row("Назад")
    answer = "Настройки"
    bot.send_message(message.chat.id, answer, reply_markup=settings_keyboard)


@bot.message_handler(commands=["exit"])
@bot.message_handler(func=lambda mess: mess.text == "Завершить",
                     content_types=["text"])
def exit_handler(message):
    func.delete_user(message.chat.id, only_choice=False)
    remove_keyboard = telebot.types.ReplyKeyboardRemove(True)
    answer = "До встречи!"
    bot.send_message(message.chat.id, answer, reply_markup=remove_keyboard)


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
    today_moscow_datetime = datetime.today() + timedelta(hours=3)
    today_moscow_date = today_moscow_datetime.date()
    json_day = func.get_json_day_data(message.chat.id, today_moscow_date)
    full_place = func.is_full_place(message.chat.id)
    answer = func.create_schedule_answer(json_day, full_place)
    bot.send_message(message.chat.id, answer, parse_mode="HTML")


@bot.message_handler(func=lambda mess: mess.text == "Завтра")
def tomorrow_schedule_handler(message):
    tomorrow_moscow_datetime = datetime.today() + timedelta(days=1, hours=3)
    tomorrow_moscow_date = tomorrow_moscow_datetime.date()
    json_day = func.get_json_day_data(message.chat.id, tomorrow_moscow_date)
    full_place = func.is_full_place(message.chat.id)
    answer = func.create_schedule_answer(json_day, full_place)
    bot.send_message(message.chat.id, answer, parse_mode="HTML")


@bot.message_handler(func=lambda mess: mess.text == emoji["calendar"])
def calendar_handler(message):
    answer = "Выбери день:"
    week_day_calendar = telebot.types.InlineKeyboardMarkup()
    week_day_calendar.row(
        *[telebot.types.InlineKeyboardButton(text=name, callback_data=name) for
          name in week_day_number.keys()])
    week_day_calendar.row(
        *[telebot.types.InlineKeyboardButton(text=name, callback_data=name) for
          name in ["Вся неделя"]])
    bot.send_message(message.chat.id, answer, reply_markup=week_day_calendar)


@bot.message_handler(func=lambda mess: mess.text == emoji["alarm_clock"])
def sending_handler(message):
    answer = "Здесь ты можешь <b>подписаться</b> на рассылку расписания на " + \
             "следующий день или <b>отписаться</b> от неё.\n" + \
             "Рассылка производится в 21:00"
    sending_keyboard = telebot.types.InlineKeyboardMarkup(True)
    if func.is_sending_on(message.chat.id):
        sending_keyboard.row(
            *[telebot.types.InlineKeyboardButton(text=name,
                                                 callback_data="Отписаться")
              for name in [emoji["cross_mark"] + " Отписаться"]])
    else:
        sending_keyboard.row(
            *[telebot.types.InlineKeyboardButton(text=name,
                                                 callback_data="Подписаться")
              for name in [emoji["check_mark"] + " Подписаться"]])
    bot.send_message(message.chat.id, answer, parse_mode="HTML",
                     reply_markup=sending_keyboard)


@bot.message_handler(func=lambda mess: mess.text == emoji["suburban"])
def suburban_handler(message):
    answer = "Меню расписания электричек"
    suburban_keyboard = telebot.types.ReplyKeyboardMarkup(True, False)
    suburban_keyboard.row('Из Универа', 'В Универ')
    suburban_keyboard.row('Назад', 'Свой маршрут')
    answer += "\n\nДанные предоставлены сервисом "
    answer += "<a href = 'http://rasp.yandex.ru/'>Яндекс.Расписания</a>"
    bot.send_message(message.chat.id,
                     answer,
                     reply_markup=suburban_keyboard,
                     parse_mode='HTML',
                     disable_web_page_preview=True)


@bot.message_handler(func=lambda mess: mess.text == emoji["editor"])
def schedule_editor_handler(message):
    answer = "Редактор расписания"
    schedule_editor_keyboard = telebot.types.ReplyKeyboardMarkup(True, False)
    schedule_editor_keyboard.row("Скрыть занятие")
    schedule_editor_keyboard.row("Назад", "Адрес", "Вернуть")
    bot.send_message(message.chat.id,
                     answer,
                     reply_markup=schedule_editor_keyboard,
                     parse_mode='HTML')


@bot.message_handler(func=lambda mess: mess.text == "Адрес",
                     content_types=["text"])
def place_handler(message):
    answer = "В каком формате отображать адрес занятий?\nСейчас: "
    place_keyboard = telebot.types.InlineKeyboardMarkup(True)
    if func.is_full_place(message.chat.id):
        answer += "<b>Полностью</b> " + emoji["school"]
        place_keyboard.row(
            *[telebot.types.InlineKeyboardButton(text=name,
                                                 callback_data="Аудитория")
              for name in [emoji["door"] + " Только аудитория"]])
    else:
        answer += "<b>Только аудитория</b> " + emoji["door"]
        place_keyboard.row(
            *[telebot.types.InlineKeyboardButton(text=name,
                                                 callback_data="Полностью")
              for name in [emoji["school"] + " Полностью"]])
    bot.send_message(message.chat.id, answer, parse_mode="HTML",
                     reply_markup=place_keyboard)


@bot.message_handler(func=lambda mess: mess.text == "Скул",
                     content_types=["text"])
def schedule_update_handler(message):
    schedule_update()
    bot.reply_to(message, "Done")


@bot.message_handler(func=lambda mess: mess.text.split("\n\n")[0] == "Всем",
                     content_types=["text"])
def for_all_handler(message):
    answer = "\n\n".join(message.text.split("\n\n")[1:])
    users_id = func.select_all_users()
    for user_id in users_id:
        try:
            bot.send_message(user_id[0], answer, disable_notification=True)
        except Exception as err:
            answer_to_me = str(user_id[0]) + "\n" + str(err)
            bot.send_message(my_id, answer_to_me, disable_notification=True)
            continue


@bot.message_handler(func=lambda mess: True, content_types=["text"])
def other_text_handler(message):
    answer = "Некоторые функции сейчас недоступны.\nПодробнее - @Spbu4u_news"
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
    full_place = func.is_full_place(call_back.message.chat.id)
    answer = func.create_schedule_answer(json_day, full_place)
    bot.edit_message_text(text=answer,
                          chat_id=call_back.message.chat.id,
                          message_id=call_back.message.message_id,
                          parse_mode="HTML")


@bot.callback_query_handler(func=lambda call_back:
                            call_back.data == "Вся неделя")
def all_week_schedule_handler(call_back):
    user_id = call_back.message.chat.id
    iso_day_date = list((datetime.today() + timedelta(hours=3)).isocalendar())
    if iso_day_date[2] == 7:
        iso_day_date[1] += 1
    days = week_day_number.keys()
    json_week = func.get_json_week_data(user_id)
    for day in days:
        iso_day_date[2] = week_day_number[day]
        day_date = func.date_from_iso(iso_day_date)
        json_day = func.get_json_day_data(user_id, day_date, json_week)
        full_place = func.is_full_place(call_back.message.chat.id)
        answer = func.create_schedule_answer(json_day, full_place)
        if day == "Пн":
            bot.edit_message_text(text=answer,
                                  chat_id=user_id,
                                  message_id=call_back.message.message_id,
                                  parse_mode="HTML")
        else:
            bot.send_message(chat_id=call_back.message.chat.id,
                             text=answer,
                             parse_mode="HTML")


@bot.callback_query_handler(func=lambda call_back:
                            call_back.data == "Подписаться")
def sending_on_handler(call_back):
    func.set_sending(call_back.message.chat.id, True)
    answer = emoji["mailbox_on"]
    answer += " Рассылка <b>активирована</b>\nЖди рассылку в 21:00"
    bot.edit_message_text(text=answer,
                          chat_id=call_back.message.chat.id,
                          message_id=call_back.message.message_id,
                          parse_mode="HTML")


@bot.callback_query_handler(func=lambda call_back:
                            call_back.data == "Отписаться")
def sending_on_handler(call_back):
    func.set_sending(call_back.message.chat.id, False)
    answer = emoji["mailbox_off"]
    answer += " Рассылка <b>отключена</b>"
    bot.edit_message_text(text=answer,
                          chat_id=call_back.message.chat.id,
                          message_id=call_back.message.message_id,
                          parse_mode="HTML")


@bot.callback_query_handler(func=lambda call_back:
                            call_back.data == "Полностью")
def full_place_on_handler(call_back):
    func.set_full_place(call_back.message.chat.id, True)
    answer = "Теперь адрес отображается <b>полностью</b> "
    answer += emoji["school"]
    bot.edit_message_text(text=answer,
                          chat_id=call_back.message.chat.id,
                          message_id=call_back.message.message_id,
                          parse_mode="HTML")


@bot.callback_query_handler(func=lambda call_back:
                            call_back.data == "Аудитория")
def full_place_off_handler(call_back):
    func.set_full_place(call_back.message.chat.id, False)
    answer = "Теперь отображается <b>только аудитория</b> "
    answer += emoji["door"]
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
        try:
            bot.process_new_updates([update])
        except Exception as err:
            answer = "Кажется, произошла ошибка.\nМожешь сообщить разработчику "
            answer += "@EeOneDown"
            bot.reply_to(update.message, answer)
            bot.forward_message(my_id, update.message.chat.id,
                                update.message.message_id)
            bot.send_message(my_id, str(err), disable_notification=True)
        return "OK", 200
    else:
        flask.abort(403)


if __name__ == '__main__':
    '''
    use test_token for local testing
    or don't forget to reset webhook
    '''
    bot.remove_webhook()
    bot.polling(none_stop=True, interval=0)
