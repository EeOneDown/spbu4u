# -*- coding: utf-8 -*-
import json
import sqlite3
import requests


def schedule_update():
    sql_con = sqlite3.connect("Bot_db")
    cursor = sql_con.cursor()
    cursor.execute("""SELECT id, alias FROM groups_data""")
    groups = cursor.fetchall()
    for group in groups:
        group_id, alias = group[0], group[1]
        url = "https://timetable.spbu.ru/api/v1/{}/".format(alias) + \
              "studentgroup/{}/events".format(group_id)
        json_week_data = requests.get(url).json()
        data = json.dumps(json_week_data)
        cursor.execute("""UPDATE groups_data
                          SET json_week_data = ?
                          WHERE id = ? AND alias = ?""",
                       (data, group_id, alias))
        sql_con.commit()
    cursor.close()
    sql_con.close()
