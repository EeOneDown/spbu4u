# -*- coding: utf-8 -*-
import json
import logging
import sqlite3
import requests
from datetime import datetime


def insert_skip(hide_event_data, hide_day, hide_time, user_id):
    sql_con = sqlite3.connect("Bot_db")
    cursor = sql_con.cursor()
    try:
        cursor.execute("""INSERT INTO lessons (name, type, day, time) 
                              VALUES (?, ?, ?, ?)""",
                       (hide_event_data[1], hide_event_data[0],
                        hide_day, hide_time))
        sql_con.commit()
    except sqlite3.IntegrityError:
        sql_con.rollback()
    finally:
        cursor.execute("""SELECT id 
                          FROM lessons 
                          WHERE name = ? 
                            AND type = ? 
                            AND day = ? 
                            AND time = ?""",
                       (hide_event_data[1], hide_event_data[0],
                        hide_day, hide_time))
        lesson_id = cursor.fetchone()[0]
    try:
        cursor.execute("""INSERT INTO skips VALUES (?, ?)""",
                       (lesson_id, user_id))
        sql_con.commit()
    except sqlite3.IntegrityError:
        sql_con.rollback()
    finally:
        cursor.close()
        sql_con.close()


def get_hide_lessons_data(user_id, db_path="Bot_db"):
    sql_con = sqlite3.connect(db_path)
    cursor = sql_con.cursor()
    cursor.execute("""SELECT
                        s.lesson_id,
                        l.name,
                        l.type,
                        l.day,
                        l.time
                      FROM skips AS s
                        JOIN lessons AS l
                          ON l.id = s.lesson_id
                      WHERE user_id = ?""", (user_id, ))
    data = cursor.fetchall()
    cursor.close()
    sql_con.close()
    return data


def delete_user(user_id, only_choice=False):
    sql_con = sqlite3.connect("Bot_db")
    cursor = sql_con.cursor()
    cursor.execute("""DELETE FROM user_choice 
                      WHERE user_id = ?""", (user_id,))
    sql_con.commit()
    if not only_choice:
        cursor.execute("""DELETE FROM user_groups 
                          WHERE user_id = ?""", (user_id,))
        sql_con.commit()
        cursor.execute("""DELETE FROM skips 
                          WHERE user_id = ?""", (user_id,))
        sql_con.commit()
        cursor.execute("""DELETE FROM user_data 
                          WHERE id = ?""", (user_id,))
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
        cursor.execute("""SELECT group_id, json_week_data
                          FROM groups_data
                            JOIN user_data
                              ON (groups_data.id = user_data.group_id AND 
                                  groups_data.alias = user_data.alias) 
                          WHERE  user_data.id= ?""", (user_id,))
        data = cursor.fetchone()

        group_id = data[0]
        next_week_monday = json.loads(data[1])["NextWeekMonday"]
        url = "https://timetable.spbu.ru/api/v1/groups/{}/events/{}".format(
            group_id, next_week_monday)
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


def get_json_day_data(user_id, day_date, json_week_data=None, next_week=False):
    if json_week_data is None:
        json_week_data = get_json_week_data(user_id, next_week)
    for day_info in json_week_data["Days"]:
        if datetime.strptime(day_info["Day"],
                             "%Y-%m-%dT%H:%M:%S").date() == day_date:
            return day_info
    return None


def is_event_in_skips(event, skips, week_day_string):
    for skip_lesson in skips:
        if skip_lesson[1] == ", ".join(event["Subject"].split(", ")[:-1]) and \
           skip_lesson[2] == event["Subject"].split(", ")[-1] and \
           (skip_lesson[3] == week_day_string or
                skip_lesson[3] == "all") and \
           (skip_lesson[4] == event["TimeIntervalString"] or
                skip_lesson[4] == "all"):
            return True
    return False


def create_schedule_answer(day_info, full_place, user_id=None, personal=True,
                           db_path="Bot_db"):
    from constants import emoji, subject_short_type

    if day_info is None:
        return emoji["sleep"] + " Выходной"

    answer = emoji["calendar"] + " "
    answer += day_info["DayString"].capitalize() + "\n\n"
    day_study_events = day_info["DayStudyEvents"]

    if personal:
        skips = get_hide_lessons_data(user_id, db_path)
    else:
        skips = []

    for event in day_study_events:
        if event["IsCancelled"]:
            continue
        if is_event_in_skips(event, skips,
                             day_info["DayString"].split(", ")[0]):
            continue
        answer += emoji["clock"] + " " + event["TimeIntervalString"] + "\n"
        answer += "<b>"
        subject_type = event["Subject"].split(", ")[-1]
        if subject_type in subject_short_type.keys():
            answer += subject_short_type[subject_type] + " - "
        else:
            answer += subject_type.capitalize() + " - "
        answer += ", ".join(event["Subject"].split(", ")[:-1]) + "</b>\n"
        for location in event["EventLocations"]:
            if full_place:
                location_name = location["DisplayName"]
            else:
                location_name = location["DisplayName"].split(", ")[-1]
            answer += location_name + " <i>("
            educators = [educator["Item2"].split(", ")[0] for educator in
                         location["EducatorIds"]]
            answer += "; ".join(educators) + ")</i>\n"
        answer += "\n"

    if len(answer.strip().split("\n\n")) == 1:
        return emoji["sleep"] + " Выходной"

    return answer


def create_master_schedule_answer(day_info):
    from constants import emoji, subject_short_type
    answer = "{} {}\n\n".format(emoji["calendar"], day_info["DayString"])
    for event in day_info["DayStudyEvents"]:
        answer += "{} {} <i>({})</i>\n".format(
            emoji["clock"], event["TimeIntervalString"],
            "; ".join(event["Dates"]))
        answer += "<b>"
        subject_type = event["Subject"].split(", ")[-1]
        if subject_type in subject_short_type.keys():
            answer += subject_short_type[subject_type] + " - "
        else:
            answer += subject_type.capitalize() + " - "
        answer += ", ".join(
            event["Subject"].split(", ")[:-1]) + "</b>\n"
        for location in event["EventLocations"]:
            location_name = location["DisplayName"]
            answer += location_name + " <i>({})</i>\n".format(
                "; ".join(name["Item1"] for name in
                          event["ContingentUnitNames"]))
        answer += "\n"
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


def select_all_users():
    sql_con = sqlite3.connect("Bot_db")
    cursor = sql_con.cursor()
    cursor.execute("""SELECT id 
                      FROM user_data""")
    ids = cursor.fetchall()
    cursor.close()
    sql_con.close()
    return ids


def is_full_place(user_id, db_path="Bot_db"):
    sql_con = sqlite3.connect(db_path)
    cursor = sql_con.cursor()
    cursor.execute("""SELECT full_place 
                      FROM user_data
                      WHERE id = ?""", (user_id, ))
    data = cursor.fetchone()
    cursor.close()
    sql_con.close()
    return data[0]


def set_full_place(user_id, on=True):
    sql_con = sqlite3.connect("Bot_db")
    cursor = sql_con.cursor()
    cursor.execute("""UPDATE user_data
                      SET full_place = ?
                      WHERE id = ?""",
                   (int(on), user_id))
    sql_con.commit()
    cursor.close()
    sql_con.close()


def get_rate_statistics():
    sql_con = sqlite3.connect("Bot_db")
    cursor = sql_con.cursor()
    cursor.execute("""SELECT sum(rate), count(id) 
                      FROM user_data
                      WHERE rate != 0""")
    data = cursor.fetchone()
    cursor.close()
    sql_con.close()
    if data[0] is None:
        return None
    else:
        return [data[0] / data[1], data[1]]


def set_rate(user_id, count_of_stars):
    sql_con = sqlite3.connect("Bot_db")
    cursor = sql_con.cursor()
    cursor.execute("""UPDATE user_data
                      SET rate = ?
                      WHERE id = ?""",
                   (int(count_of_stars), user_id))
    sql_con.commit()
    cursor.close()
    sql_con.close()


def write_log(update, work_time):
    log = ""
    if update.message is not None:
        chat_id = update.message.chat.id
        user_text = update.message.text
    else:
        chat_id = update.callback_query.message.chat.id
        user_text = update.callback_query.data
    log += "CHAT: {} ===== TEXT: {} ===== TIME: {}".format(
        chat_id, user_text, work_time)
    logging.info(log)


def get_templates(user_id):
    sql_con = sqlite3.connect("Bot_db")
    cursor = sql_con.cursor()
    cursor.execute("""SELECT gd.id, gd.json_week_data
                      FROM user_groups AS ug
                        JOIN groups_data AS gd
                          ON ug.group_id = gd.id
                      WHERE ug.user_id = ?;""", (user_id, ))
    data = cursor.fetchall()
    cursor.close()
    sql_con.close()
    groups = {}
    for group in data:
        groups[json.loads(group[1])["StudentGroupDisplayName"][7:]] = group[0]
    return groups


def get_current_group(user_id):
    week_data = get_json_week_data(user_id)
    group_data = {"title": week_data["StudentGroupDisplayName"][7:],
                  "id": week_data["StudentGroupId"]}
    return group_data


def save_group(group_id, user_id):
    sql_con = sqlite3.connect("Bot_db")
    cursor = sql_con.cursor()
    try:
        cursor.execute("""INSERT INTO user_groups VALUES (?, ?)""",
                       (group_id, user_id))
        sql_con.commit()
    except sqlite3.IntegrityError:
        sql_con.rollback()
    finally:
        cursor.close()
        sql_con.close()


def delete_group(group_id, user_id):
    sql_con = sqlite3.connect("Bot_db")
    cursor = sql_con.cursor()
    try:
        cursor.execute("""DELETE FROM user_groups 
                          WHERE group_id = ? 
                            AND user_id = ?""",
                       (group_id, user_id))
        sql_con.commit()
    except sqlite3.IntegrityError:
        sql_con.rollback()
    finally:
        cursor.close()
        sql_con.close()


def get_statistics_for_admin():
    data = {}
    sql_con = sqlite3.connect("Bot_db")
    cursor = sql_con.cursor()

    cursor.execute("""SELECT count(id)
                      FROM user_data""")
    data["count_of_users"] = cursor.fetchone()[0]

    cursor.execute("""SELECT count(id)
                      FROM groups_data""")
    data["count_of_groups"] = cursor.fetchone()[0]

    cursor.execute("""SELECT count(id)
                      FROM user_data
                      WHERE sending = 1
                      GROUP BY sending;""")
    data["count_of_sending"] = cursor.fetchone()[0]

    cursor.close()
    sql_con.close()
    return data


def get_fom_station_code(user_id):
    sql_con = sqlite3.connect("Bot_db")
    cursor = sql_con.cursor()
    cursor.execute("""SELECT home_station_code
                      FROM user_data
                      WHERE id = ?""", (user_id, ))
    from_station = cursor.fetchone()[0]
    cursor.close()
    sql_con.close()
    return from_station


def is_univer(user_id):
    sql_con = sqlite3.connect("Bot_db")
    cursor = sql_con.cursor()
    cursor.execute("""SELECT is_univer
                      FROM user_data
                      WHERE id = ?""", (user_id,))
    univer = cursor.fetchone()[0]
    cursor.close()
    sql_con.close()
    return univer


def change_home_station(user_id, station_title):
    from constants import all_stations

    home_station_code = all_stations[station_title]
    sql_con = sqlite3.connect("Bot_db")
    cursor = sql_con.cursor()
    cursor.execute("""UPDATE user_data
                      SET home_station_code = ?
                      WHERE id = ?""",
                   (home_station_code, user_id))
    sql_con.commit()
    cursor.close()
    sql_con.close()


def change_univer_station(user_id, univer):
    sql_con = sqlite3.connect("Bot_db")
    cursor = sql_con.cursor()
    cursor.execute("""UPDATE user_data
                      SET is_univer = ?
                      WHERE id = ?""",
                   (univer, user_id))
    sql_con.commit()
    cursor.close()
    sql_con.close()
