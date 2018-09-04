# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from datetime import datetime, date, timedelta

import pymysql
import spbu

from app.constants import emoji, subject_short_types


server_timedelta = timedelta(hours=0)


def parse_event_time(event):
    return "{0} {1:0>2}:{2:0>2}{3}{4:0>2}:{5:0>2}".format(
        emoji["clock"],
        datetime_from_string(event["Start"]).time().hour,
        datetime_from_string(event["Start"]).time().minute,
        emoji["en_dash"],
        datetime_from_string(event["End"]).time().hour,
        datetime_from_string(event["End"]).time().minute
    )


def parse_event_subject(event):
    answer = ""
    subject_name = ", ".join(event["Subject"].split(", ")[:-1])

    subject_type = event["Subject"].split(", ")[-1]
    stripped_subject_type = " ".join(subject_type.split()[:2])
    if stripped_subject_type in subject_short_types.keys():
        answer += subject_short_types[stripped_subject_type] + " - "
    else:
        answer += subject_type.upper() + " - "
    answer += subject_name

    return answer


def parse_event_location(location, full_place=True, have_chosen_educator=False,
                         chosen_educator=None):
    answer = ""

    if location["IsEmpty"]:
        return answer

    if have_chosen_educator and not chosen_educator.issuperset(
            {edu["Item2"].split(", ")[0] for edu in location["EducatorIds"]}
    ):
        return answer

    if full_place:
        location_name = location["DisplayName"].strip(", ").strip()
    else:
        location_name = location["DisplayName"].split(", ")[-1].strip()

    answer += location_name

    if location["HasEducators"]:
        educators = [educator["Item2"].split(", ")[0] for educator in
                     location["EducatorIds"]]

        if len(educators):
            answer += " <i>({0})</i>".format("; ".join(educators))

    return answer


def insert_skip(event_name, types, event_day, event_time,
                educators, user_id, is_choose_educator=False):
    sql_con = get_connection()
    cursor = sql_con.cursor()
    try:
        cursor.execute("""INSERT INTO lessons 
                          (name, types, day, time, educators) 
                              VALUES (%s, %s, %s, %s, %s)""",
                       (event_name, types, event_day, event_time, educators))
        sql_con.commit()
    except pymysql.IntegrityError:
        sql_con.rollback()
    finally:
        cursor.execute("""SELECT id 
                          FROM lessons 
                          WHERE name = %s 
                            AND types = %s 
                            AND day = %s 
                            AND time = %s
                            AND educators = %s""",
                       (event_name, types, event_day, event_time, educators))
        lesson_id = cursor.fetchone()[0]
    try:
        if is_choose_educator:
            cursor.execute("""INSERT INTO user_educators VALUES (%s, %s)""",
                           (user_id, lesson_id))
        else:
            cursor.execute("""INSERT INTO skips VALUES (%s, %s)""",
                           (lesson_id, user_id))
        sql_con.commit()
    except pymysql.IntegrityError:
        sql_con.rollback()
    finally:
        cursor.close()
        sql_con.close()


def get_hide_lessons_data(user_id, week_day=None,
                          is_educator=False):
    sql_con = get_connection()
    cursor = sql_con.cursor()
    sql_req = """SELECT
                   s.lesson_id,
                   l.name,
                   l.types,
                   l.day,
                   l.time,
                   l.educators
              """
    if is_educator:
        sql_req += """FROM user_educators AS s
                        JOIN lessons AS l
                          ON l.id = s.lesson_id
                   """
    else:
        sql_req += """FROM skips AS s
                        JOIN lessons AS l
                          ON l.id = s.lesson_id
                   """
    sql_req += """WHERE user_id = %s"""
    req_param = (user_id,)
    if week_day:
        sql_req += "  AND (day = 'all' OR day = %s)"
        req_param += (week_day, )
    cursor.execute(sql_req, req_param)
    data = cursor.fetchall()
    cursor.close()
    sql_con.close()
    return data


def get_connection():
    import sqlite3
    return sqlite3.connect("app.db")


def date_from_iso(iso):
    return datetime.strptime("%d%02d%d" % (iso[0], iso[1], iso[2]),
                             "%Y%W%w").date()


def get_current_monday_date():
    iso_day_date = list((date.today() + server_timedelta).isocalendar())
    if iso_day_date[2] == 7:
        iso_day_date[1] += 1
    iso_day_date[2] = 1
    monday_date = date_from_iso(iso_day_date)
    return monday_date


def delete_symbols(json_obj):
    return json.loads(
        json.dumps(json_obj).replace("<", "").replace(">", "").replace("&", "")
    )


def get_chosen_educators(user_id):
    sql_con = get_connection()
    cursor = sql_con.cursor()
    data = {}
    sql_req = """SELECT
                   lessons.name,
                   lessons.educators
                 FROM user_educators
                   JOIN lessons
                     ON user_educators.lesson_id = lessons.id
                 WHERE user_educators.user_id = %s"""
    cursor.execute(sql_req, (user_id,))
    for row in cursor.fetchall():
        if row[0] in data.keys():
            data[row[0]].add(row[1])
        else:
            data[row[0]] = {row[1]}
    return data


def datetime_from_string(dt_string):
    return datetime.strptime(dt_string, "%Y-%m-%dT%H:%M:%S")


def is_event_in_skips(event, skips, week_day_string):
    event_educators = []
    for educator in event["EducatorIds"]:
        event_educators.append(educator["Item2"].split(", ")[0])
    event_educators = set(event_educators)

    for skip_lesson in skips:
        skip_educators = set(skip_lesson[5].split("; "))
        stripped_type = " ".join(event["Subject"].split(", ")[-1].split()[:2])
        if skip_lesson[1] == ", ".join(event["Subject"].split(", ")[:-1]) and \
                (skip_lesson[2] == "all" or
                 stripped_type in skip_lesson[2].split("; ")) and \
                (skip_lesson[3] == "all" or
                 skip_lesson[3] == week_day_string) and \
                (skip_lesson[4] == "all" or
                 skip_lesson[4] == parse_event_time(event)) and \
                (skip_lesson[5] == "all" or
                 event_educators.issubset(skip_educators)):
            return True
    return False


def get_json_week_data(user_id, next_week=False, for_day=None):
    sql_con = get_connection()
    cursor = sql_con.cursor()
    cursor.execute("""SELECT group_id
                      FROM user_data 
                      WHERE  id= %s""", (user_id,))
    group_id = cursor.fetchone()[0]
    cursor.close()
    sql_con.close()

    if for_day:
        monday_date = for_day
    elif next_week:
        monday_date = get_current_monday_date()
        monday_date += timedelta(days=7)
    else:
        monday_date = get_current_monday_date()

    json_week_data = spbu.get_group_events(group_id=group_id,
                                           from_date=monday_date)
    return delete_symbols(json_week_data)


def get_json_day_data(user_id, day_date, json_week_data=None, next_week=False):
    if json_week_data is None:
        json_week_data = get_json_week_data(user_id, next_week)
    for day_info in json_week_data["Days"]:
        if datetime_from_string(day_info["Day"]).date() == day_date:
            return day_info
    return None


def get_lessons_with_educators(user_id, day_date):
    json_day = get_json_day_data(user_id, day_date)
    answer = ""
    day_study_events = json_day["DayStudyEvents"]
    count = 0
    for event in day_study_events:
        event_text = ""
        if (event["IsCancelled"]
                or len([loc for loc in event["EventLocations"]
                        if loc["HasEducators"]]) < 2):
            continue
        subject_name = ", ".join(event["Subject"].split(", ")[:-1])
        event_text += "{0}</b>".format(subject_name)
        if is_event_in_skips(event, get_hide_lessons_data(
                user_id, week_day=json_day["DayString"].split(", ")[0]),
                             json_day["DayString"].split(", ")[0]):
            event_text += " {0}".format(emoji["cross_mark"])
        event_text += "\n"

        chosen_educators = get_chosen_educators(user_id)
        have_chosen_educator = False
        if subject_name in chosen_educators.keys() \
                and any(
            ch_edu in [
                edu["Item2"].split(", ")[0] for edu in event["EducatorIds"]
            ] for ch_edu in chosen_educators[subject_name]
        ):
            have_chosen_educator = True
        for location in event["EventLocations"]:
            event_text += location["DisplayName"].strip(", ")
            educators = {educator["Item2"].split(", ")[0] for educator in
                         location["EducatorIds"]}
            if len(educators):
                event_text += " <i>({0})</i>".format("; ".join(educators))
            if have_chosen_educator and educators.issubset(chosen_educators[
                                                               subject_name]):
                event_text += " {0}".format(emoji["heavy_check_mark"])
            event_text += "\n"
        if event_text not in answer:
            count += 1
            answer += "<b>{0}. {1}\n".format(count, event_text)
    if answer == "":
        data = {"is_empty": True, "answer": "Подходящих занятий нет",
                "date": json_day["DayString"].capitalize()}
    else:
        data = {"is_empty": False, "answer": answer.strip("\n\n"),
                "date": json_day["DayString"].capitalize()}
    return data
