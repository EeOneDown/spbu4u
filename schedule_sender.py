# -*- coding: utf-8 -*-
import json
import sqlite3
from datetime import datetime, timedelta
from functions import get_json_day_data, create_schedule_answer
from flask_app import bot


def schedule_sender():
    sql_con = sqlite3.connect("Bot_db")
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
        answer = create_schedule_answer(json_day)
        if "Выходной" in answer:
            continue
        bot.send_message(user_id, answer, parse_mode="HTML")


if __name__ == '__main__':
    schedule_sender()
