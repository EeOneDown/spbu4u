# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import sqlite3

import requests


def schedule_update(db_path="Bot.db"):
    sql_con = sqlite3.connect(db_path)
    cursor = sql_con.cursor()
    # WITH construction doesn't work :(
    cursor.execute("""DELETE
                      FROM groups_data
                      WHERE id in (
                        SELECT
                          groups_data.id
                        FROM groups_data
                          LEFT OUTER JOIN user_data
                            ON groups_data.id = user_data.group_id
                          LEFT OUTER JOIN user_groups
                            ON groups_data.id = user_groups.group_id
                        WHERE user_data.id ISNULL
                          AND user_groups.group_id ISNULL
                      )""")
    sql_con.commit()
    cursor.execute("""SELECT id FROM groups_data""")
    groups = cursor.fetchall()
    for group in groups:
        group_id = group[0]
        url = "https://timetable.spbu.ru/api/v1/groups/{0}/events".format(
            group_id)
        json_week_data = requests.get(url).json()
        data = json.dumps(json_week_data)
        cursor.execute("""UPDATE groups_data
                          SET json_week_data = ?
                          WHERE id = ?""",
                       (data, group_id))
        sql_con.commit()
    cursor.close()
    sql_con.close()


if __name__ == '__main__':
    schedule_update()
