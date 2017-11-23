#!/home/EeOneDown/myvenv/bin/python3.6
# -*- coding: utf-8 -*-
import json
import sqlite3
from datetime import datetime, timedelta
from time import sleep, localtime

import telebot

from constants import release_token
from functions import get_json_day_data, create_schedule_answer, \
    is_full_place, send_long_message
from sql_updater import schedule_update


def schedule_sender():
    bot = telebot.TeleBot(release_token)
    db_path = "spbu4u/Bot.db"
    sql_con = sqlite3.connect(db_path)
    cursor = sql_con.cursor()
    cursor.execute("""SELECT user_data.id, groups_data.json_week_data
                      FROM user_data
                        JOIN groups_data
                          ON (user_data.group_id = groups_data.id
                              AND sending = 1)""")
    data = cursor.fetchall()
    cursor.close()
    sql_con.close()

    tomorrow_moscow_datetime = datetime.today() + timedelta(days=1, hours=3)
    tomorrow_moscow_date = tomorrow_moscow_datetime.date()
    for user_data in data:
        user_id, json_week = user_data[0], json.loads(user_data[1])
        json_day = get_json_day_data(user_id, tomorrow_moscow_date, json_week)
        full_place = is_full_place(user_id, db_path=db_path)
        answer = create_schedule_answer(json_day, full_place, user_id,
                                        db_path=db_path)
        if "Выходной" in answer:
            continue
        print(user_id, answer)
        try:
            answer = "Расписание на завтра:\n\n" + answer
            send_long_message(bot, answer, user_id)
        except Exception as err:
            print(err)
            continue


if __name__ == '__main__':
    schedule_update("spbu4u/Bot.db")
    schedule_sender()
    if datetime.today().weekday() == 5:
        loc_time = localtime()
        sleep((59 - loc_time.tm_min) * 60 + (23 - loc_time.tm_hour) * 3600)
        schedule_update("spbu4u/Bot.db")
