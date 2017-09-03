# -*- coding: utf-8 -*-
import json
import sqlite3
import requests
from datetime import datetime


def set_next_step(user_id, next_step):
    sql_con = sqlite3.connect("Bot_db")
    cursor = sql_con.cursor()
    cursor.execute("""UPDATE user_choice
                      SET step = ? 
                      WHERE user_id = ?""",
                   (next_step, user_id))
    sql_con.commit()
    cursor.close()
    sql_con.close()


def get_step(user_id):
    sql_con = sqlite3.connect("Bot_db")
    cursor = sql_con.cursor()
    cursor.execute("""SELECT  step
                      FROM user_choice
                      WHERE user_id = ?""", (user_id, ))
    step = cursor.fetchone()
    cursor.close()
    sql_con.close()
    if step is None:
        return None
    else:
        return step[0]


def delete_user(user_id, only_choice=False):
    sql_con = sqlite3.connect("Bot_db")
    cursor = sql_con.cursor()
    cursor.execute("""DELETE FROM user_choice WHERE user_id = ?""",
                   (user_id,))
    sql_con.commit()
    if not only_choice:
        cursor.execute("""DELETE FROM user_groups WHERE user_id = ?""",
                       (user_id,))
        sql_con.commit()
        cursor.execute("""DELETE FROM skips WHERE user_id = ?""",
                       (user_id,))
        sql_con.commit()
        cursor.execute("""DELETE FROM user_data WHERE id = ?""",
                       (user_id,))
        sql_con.commit()
    cursor.close()
    sql_con.close()


def date_from_iso(iso):
    return datetime.strptime("%d%02d%d" % (iso[0], iso[1], iso[2]),
                             "%Y%W%w").date()


def get_json_week_data(user_id, next_week=False):
    sql_con = sqlite3.connect("Bot_db")
    cursor = sql_con.cursor()
    if next_week:
        cursor.execute("""SELECT groups_data.alias, group_id, json_week_data
                          FROM groups_data
                            JOIN user_data
                              ON (groups_data.id = user_data.group_id AND 
                                  groups_data.alias = user_data.alias) 
                          WHERE  user_data.id= ?""", (user_id,))
        data = cursor.fetchone()

        alias, group_id = data[0], data[1]
        next_week_monday = json.loads(data[2])["NextWeekMonday"]
        url = "https://timetable.spbu.ru/api/v1/{}/".format(alias) + \
              "studentgroup/{}/events".format(group_id) + \
              "?weekMonday={}".format(next_week_monday)
        json_week_data = requests.get(url).json()
    else:
        cursor.execute("""SELECT json_week_data
                          FROM groups_data
                            JOIN user_data
                              ON (groups_data.id = user_data.group_id AND 
                                  groups_data.alias = user_data.alias) 
                          WHERE  user_data.id= ?""", (user_id, ))
        data = cursor.fetchone()

        json_week_data = json.loads(data[0])
    cursor.close()
    sql_con.close()
    return json_week_data


def get_json_day_data(user_id, day_date, json_week_data=None):
    if json_week_data is None:
        json_week_data = get_json_week_data(user_id)
    for day_info in json_week_data["Days"]:
        if datetime.strptime(day_info["Day"],
                             "%Y-%m-%dT%H:%M:%S").date() == day_date:
            return day_info
    return None


def create_schedule_answer(day_info, full=True):
    from constants import emoji, subject_short_type
    if day_info is None:

        return emoji["sleep"] + " Выходной"

    answer = emoji["calendar"] + " "
    answer += day_info["DayString"].capitalize() + "\n\n"
    day_study_events = day_info["DayStudyEvents"]
    for event in day_study_events:
        if not full:
            # TODO select skip lessons for user
            # skips = []
            pass
        else:
            # skips = []
            pass
        answer += emoji["clock"] + " " + event["TimeIntervalString"] + "\n"
        answer += "<b>"
        answer += subject_short_type[event["Subject"].split(", ")[-1]] + " - "
        answer += ", ".join(event["Subject"].split(", ")[:-1]) + "</b>\n"
        for location in event["EventLocations"]:
            answer += location["DisplayName"] + " <i>("
            educators = [educator["Item2"].split(", ")[0] for educator in
                         location["EducatorIds"]]
            answer += "; ".join(educators) + ")</i>\n\n"
    return answer


def is_user_exist(user_id):
    sql_con = sqlite3.connect("Bot_db")
    cursor = sql_con.cursor()
    cursor.execute("""SELECT count(id) 
                      FROM user_data
                      WHERE id = ?""", (user_id, ))
    data = cursor.fetchone()
    cursor.close()
    sql_con.close()
    return data[0]


def is_sending_on(user_id):
    sql_con = sqlite3.connect("Bot_db")
    cursor = sql_con.cursor()
    cursor.execute("""SELECT sending 
                      FROM user_data
                      WHERE id = ?""", (user_id, ))
    data = cursor.fetchone()
    cursor.close()
    sql_con.close()
    return data[0]


def set_sending(user_id, on=True):
    sql_con = sqlite3.connect("Bot_db")
    cursor = sql_con.cursor()
    cursor.execute("""UPDATE user_data
                      SET sending = ?
                      WHERE id = ?""",
                   (int(on), user_id))
    sql_con.commit()
    cursor.close()
    sql_con.close()
