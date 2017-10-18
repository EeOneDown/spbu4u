#!/home/EeOneDown/myvenv/bin/python3.6
# -*- coding: utf-8 -*-
import json
import sqlite3
import telebot
from datetime import datetime, timedelta
from functions import get_json_day_data, create_schedule_answer, is_full_place
from constants import release_token
from sql_updater import schedule_update


def schedule_sender():
    bot = telebot.TeleBot(release_token)
    db_path = "spbu4u/Bot_db"
    sql_con = sqlite3.connect(db_path)
    cursor = sql_con.cursor()
    cursor.execute("""SELECT user_data.id, groups_data.json_week_data
                      FROM user_data
                        JOIN groups_data
                          ON (user_data.group_id = groups_data.id
                              AND groups_data.alias = user_data.alias
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
            bot.send_message(user_id, answer, parse_mode="HTML")
        except Exception as err:
            print(err)
            continue


if __name__ == '__main__':
    schedule_update("spbu4u/Bot_db")
    schedule_sender()
