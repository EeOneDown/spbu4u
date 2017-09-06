# -*- coding: utf-8 -*-
import json
import sqlite3
import requests


def schedule_update():
    sql_con = sqlite3.connect("Bot_db")
    cursor = sql_con.cursor()
    # WITH construction don't work :(
    cursor.execute("""DELETE
                      FROM groups_data
                      WHERE id in (
                        SELECT
                          groups_data.id
                        FROM groups_data
                          LEFT OUTER JOIN user_data
                            ON (groups_data.id = user_data.group_id
                              AND groups_data.alias = user_data.alias)
                        WHERE user_data.id ISNULL
                      )
                            AND alias in (
                        SELECT
                          groups_data.alias
                        FROM groups_data
                          LEFT OUTER JOIN user_data
                            ON (groups_data.id = user_data.group_id
                              AND groups_data.alias = user_data.alias)
                        WHERE user_data.id ISNULL
                      );""")
    sql_con.commit()
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
