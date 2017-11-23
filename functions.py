# -*- coding: utf-8 -*-
import json
import logging
import sqlite3
import requests
from datetime import datetime, date
from telebot.apihelper import ApiException


def insert_skip(hide_event_data, hide_day, hide_time, user_id):
    sql_con = sqlite3.connect("Bot.db")
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


def get_hide_lessons_data(user_id, db_path="Bot.db"):
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
    sql_con = sqlite3.connect("Bot.db")
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


def select_all_group_data():
    sql_con = sqlite3.connect("Bot.db")
    cursor = sql_con.cursor()
    cursor.execute("""SELECT json_week_data
                      FROM groups_data""")
    data = cursor.fetchall()
    cursor.close()
    sql_con.close()

    data = [json.loads(group_data[0]) for group_data in data]
    return data


def get_json_week_data(user_id, next_week=False, for_day=None):
    sql_con = sqlite3.connect("Bot.db")
    cursor = sql_con.cursor()
    if next_week:
        cursor.execute("""SELECT group_id, json_week_data
                          FROM groups_data
                            JOIN user_data
                              ON groups_data.id = user_data.group_id 
                          WHERE  user_data.id= ?""", (user_id,))
        data = cursor.fetchone()

        group_id = data[0]
        next_week_monday = json.loads(data[1])["NextWeekMonday"]
        url = "https://timetable.spbu.ru/api/v1/groups/{0}/events/{1}".format(
            group_id, next_week_monday)
        json_week_data = requests.get(url).json()
    elif for_day is not None:
        cursor.execute("""SELECT group_id
                          FROM user_data 
                          WHERE  id= ?""", (user_id,))
        data = cursor.fetchone()

        group_id = data[0]
        url = "https://timetable.spbu.ru/api/v1/groups/{0}/events/{1}".format(
            group_id, for_day)
        json_week_data = requests.get(url).json()
    else:
        cursor.execute("""SELECT json_week_data
                          FROM groups_data
                            JOIN user_data
                              ON groups_data.id = user_data.group_id 
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
                           db_path="Bot.db", only_exams=False):
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
        if event["IsCancelled"] or \
                (only_exams and "пересдача" in event["Subject"]) or \
                (only_exams and "комиссия" in event["Subject"]):
            continue
        if is_event_in_skips(event, skips,
                             day_info["DayString"].split(", ")[0]):
            continue
        if event["IsAssigned"]:
            answer += emoji["new"] + " "
        answer += emoji["clock"] + " " + event["TimeIntervalString"]
        if event["TimeWasChanged"]:
            answer += " " + emoji["warning"]
        answer += "\n<b>"
        subject_type = event["Subject"].split(", ")[-1]
        if subject_type in subject_short_type.keys():
            answer += subject_short_type[subject_type] + " - "
        else:
            answer += subject_type.capitalize() + " - "
        answer += ", ".join(event["Subject"].split(", ")[:-1]) + "</b>\n"
        for location in event["EventLocations"]:
            if location["IsEmpty"]:
                continue
            if full_place:
                location_name = location["DisplayName"].strip(", ")
            else:
                location_name = location["DisplayName"].split(", ")[-1]
            answer += location_name
            if location["HasEducators"]:
                answer += " <i>("
                educators = [educator["Item2"].split(", ")[0] for educator in
                             location["EducatorIds"]]
                answer += "; ".join(educators) + ")</i>"
            if event["LocationsWereChanged"] or \
                    event["EducatorsWereReassigned"]:
                answer += " " + emoji["warning"]
            answer += "\n"
        answer += "\n"

    if len(answer.strip().split("\n\n")) == 1:
        return emoji["sleep"] + " Выходной"

    return answer


def create_master_schedule_answer(day_info):
    from constants import emoji, subject_short_type
    answer = "{0} {1}\n\n".format(emoji["calendar"], day_info["DayString"])
    for event in day_info["DayStudyEvents"]:
        answer += "{0} {1} <i>({2})</i>\n".format(
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
            answer += location_name + " <i>({0})</i>\n".format(
                "; ".join(name["Item1"] for name in
                          event["ContingentUnitNames"]))
        answer += "\n"
    return answer


def is_user_exist(user_id):
    sql_con = sqlite3.connect("Bot.db")
    cursor = sql_con.cursor()
    cursor.execute("""SELECT count(id) 
                      FROM user_data
                      WHERE id = ?""", (user_id, ))
    data = cursor.fetchone()
    cursor.close()
    sql_con.close()
    return data[0]


def is_sending_on(user_id):
    sql_con = sqlite3.connect("Bot.db")
    cursor = sql_con.cursor()
    cursor.execute("""SELECT sending 
                      FROM user_data
                      WHERE id = ?""", (user_id, ))
    data = cursor.fetchone()
    cursor.close()
    sql_con.close()
    return data[0]


def set_sending(user_id, on=True):
    sql_con = sqlite3.connect("Bot.db")
    cursor = sql_con.cursor()
    cursor.execute("""UPDATE user_data
                      SET sending = ?
                      WHERE id = ?""",
                   (int(on), user_id))
    sql_con.commit()
    cursor.close()
    sql_con.close()


def select_all_users():
    sql_con = sqlite3.connect("Bot.db")
    cursor = sql_con.cursor()
    cursor.execute("""SELECT id 
                      FROM user_data""")
    ids = cursor.fetchall()
    cursor.close()
    sql_con.close()
    return ids


def is_full_place(user_id, db_path="Bot.db"):
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
    sql_con = sqlite3.connect("Bot.db")
    cursor = sql_con.cursor()
    cursor.execute("""UPDATE user_data
                      SET full_place = ?
                      WHERE id = ?""",
                   (int(on), user_id))
    sql_con.commit()
    cursor.close()
    sql_con.close()


def get_rate_statistics():
    sql_con = sqlite3.connect("Bot.db")
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
    sql_con = sqlite3.connect("Bot.db")
    cursor = sql_con.cursor()
    cursor.execute("""UPDATE user_data
                      SET rate = ?
                      WHERE id = ?""",
                   (int(count_of_stars), user_id))
    sql_con.commit()
    cursor.close()
    sql_con.close()


def write_log(update, work_time, was_error=False):
    if update.message is not None:
        chat_id = update.message.chat.id
        user_text = update.message.text
    elif update.callback_query is not None:
        chat_id = update.callback_query.message.chat.id
        user_text = update.callback_query.data
    else:
        chat_id = "ERROR"
        user_text = str(update)
    log = "CHAT: {0} ===== TEXT: {1} ===== TIME: {2}".format(
        chat_id, user_text, work_time)
    if was_error:
        log += "        ERROR"
    logging.info(log)


def get_templates(user_id):
    sql_con = sqlite3.connect("Bot.db")
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
    sql_con = sqlite3.connect("Bot.db")
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
    sql_con = sqlite3.connect("Bot.db")
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
    sql_con = sqlite3.connect("Bot.db")
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
                      GROUP BY sending""")
    r_data = cursor.fetchone()
    data["count_of_sending"] = 0 if r_data is None else r_data[0]

    cursor.close()
    sql_con.close()
    return data


def get_fom_station_code(user_id):
    sql_con = sqlite3.connect("Bot.db")
    cursor = sql_con.cursor()
    cursor.execute("""SELECT home_station_code
                      FROM user_data
                      WHERE id = ?""", (user_id, ))
    from_station = cursor.fetchone()[0]
    cursor.close()
    sql_con.close()
    return from_station


def is_univer(user_id):
    sql_con = sqlite3.connect("Bot.db")
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
    sql_con = sqlite3.connect("Bot.db")
    cursor = sql_con.cursor()
    cursor.execute("""UPDATE user_data
                      SET home_station_code = ?
                      WHERE id = ?""",
                   (home_station_code, user_id))
    sql_con.commit()
    cursor.close()
    sql_con.close()


def change_univer_station(user_id, univer):
    sql_con = sqlite3.connect("Bot.db")
    cursor = sql_con.cursor()
    cursor.execute("""UPDATE user_data
                      SET is_univer = ?
                      WHERE id = ?""",
                   (univer, user_id))
    sql_con.commit()
    cursor.close()
    sql_con.close()


def send_long_message(bot, text, user_id):
    try:
        bot.send_message(user_id, text, parse_mode="HTML")
    except ApiException as ApiExcept:
        json_err = json.loads(ApiExcept.result.text)
        if json_err["description"] == "Bad Request: message is too long":
            event_count = len(text.split("\n\n"))
            first_part = "\n\n".join(text.split("\n\n")[:event_count // 2])
            second_part = "\n\n".join(text.split("\n\n")[event_count // 2:])
            send_long_message(bot, first_part, user_id)
            send_long_message(bot, second_part, user_id)


def get_user_rate(user_id):
    sql_con = sqlite3.connect("Bot.db")
    cursor = sql_con.cursor()
    cursor.execute("""SELECT rate
                      FROM user_data
                      WHERE id = ?""", (user_id,))
    rate = cursor.fetchone()[0]
    cursor.close()
    sql_con.close()
    return rate


def is_correct_educator_name(text):
    return text.replace(".", "").replace("-", "").replace(" ", "").isalnum()


def text_to_date(text):
    from constants import months

    text = text.replace(".", " ").replace(",", " ")
    if text.replace(" ", "").isalnum():
        words = text.split()[:3]
        for word in words:
            if not (word.isdecimal() or (
                    word.isalpha() and (word.lower() in months.keys()))):
                return False
        try:
            day = int(words[0])
            month = datetime.today().month
            year = datetime.today().year
            if len(words) > 1:
                month = int(words[1]) if words[1].isdecimal() else months[
                                                                    words[1]]
                if len(words) > 2:
                    year = int(words[2])
            return datetime.today().replace(day=day, month=month,
                                            year=year).date()
        except ValueError:
            return False
    return False


def add_new_user(user_id, group_id, week_data=None):
    sql_con = sqlite3.connect("Bot.db")
    cursor = sql_con.cursor()
    try:
        cursor.execute("""INSERT INTO user_data (id, group_id)
                          VALUES (?, ?)""",
                       (user_id, group_id))
    except sqlite3.IntegrityError:
        sql_con.rollback()
        cursor.execute("""UPDATE user_data 
                          SET group_id = ?
                          WHERE id = ?""",
                       (group_id, user_id))
    finally:
        sql_con.commit()
        cursor.execute("""DELETE FROM user_choice WHERE user_id = ?""",
                       (user_id,))
        sql_con.commit()
    if week_data is None:
        url = "https://timetable.spbu.ru/api/v1/groups/{0}/events".format(
            group_id)
        week_data = requests.get(url).json()
    data = json.dumps(week_data)
    try:
        cursor.execute("""INSERT INTO groups_data 
                          (id, json_week_data)
                          VALUES (?, ?)""",
                       (group_id, data))
    except sqlite3.IntegrityError:
        cursor.execute("""UPDATE groups_data
                          SET json_week_data = ?
                          WHERE id = ?""",
                       (data, group_id))
    finally:
        sql_con.commit()
        cursor.close()
        sql_con.close()


def get_semester_dates(today):
    if today.month in range(2, 8):
        start_year = today.year
        end_year = today.year
        start_month = 2
        end_month = 8
    else:
        start_year = today.year - 1 if today.month < 2 else today.year
        end_year = today.year + 1 if today.month > 7 else today.year
        start_month = 8
        end_month = 2

    return [date(year=start_year, month=start_month, day=1),
            date(year=end_year, month=end_month, day=1)]


def get_json_attestation(user_id):
    sql_con = sqlite3.connect("Bot.db")
    cursor = sql_con.cursor()
    cursor.execute("""SELECT groups_data.interim_attestation
                      FROM user_data
                        JOIN groups_data
                          ON user_data.group_id = groups_data.id
                      WHERE user_data.id = ?""", (user_id, ))
    data = cursor.fetchone()[0]
    cursor.close()
    sql_con.close()
    return json.loads(data)


def get_available_months(user_id):
    from constants import months_date

    json_att = get_json_attestation(user_id)
    available_months = {}
    for day_data in json_att["Days"]:
        data = datetime.strptime(day_data["Day"], "%Y-%m-%dT%H:%M:%S")
        available_months[data.month] = "{0} {1}".format(months_date[data.month],
                                                        data.year)
    return available_months


def get_blocks(user_id, day_date):
    from constants import emoji, subject_short_type

    json_day = get_json_day_data(user_id, day_date)
    day_string = json_day["DayString"].capitalize()

    day_study_events = json_day["DayStudyEvents"]
    block_answers = []
    for num, event in enumerate(day_study_events):
        answer = "\n<b>{0}. ".format(num + 1)
        subject_type = event["Subject"].split(", ")[-1]
        if subject_type in subject_short_type.keys():
            answer += subject_short_type[subject_type] + " - "
        else:
            answer += subject_type.capitalize() + " - "
        answer += ", ".join(event["Subject"].split(", ")[:-1]) + "</b>\n"
        for location in event["EventLocations"]:
            if location["IsEmpty"]:
                continue
            location_name = location["DisplayName"].strip(", ")
            answer += location_name
            if location["HasEducators"]:
                answer += " <i>("
                educators = [educator["Item2"].split(", ")[0] for educator in
                             location["EducatorIds"]]
                answer += "; ".join(educators) + ")</i>"
            answer += "\n"
        # TODO change if to HasTheSameTimeAsPreviousItem
        if num != 0 and event["TimeIntervalString"] == \
                day_study_events[num - 1]["TimeIntervalString"]:
            block_answers[-1] += answer
        else:
            answer = "{0} {1}\n".format(emoji["clock"],
                                        event["TimeIntervalString"]) + answer
            block_answers.append(answer)
    return day_string, [block + "\nВыбери занятие:" for block in block_answers]


def get_current_block(message_text, user_id, is_prev=False):
    from flask_app import server_timedelta
    from constants import week_day_number, week_day_titles
    current_block = int(message_text.split(" ")[0]) - 1
    day_string = message_text.split(")")[0].split("(")[-1]

    iso_day_date = list((datetime.today() + server_timedelta).isocalendar())
    if iso_day_date[2] == 7:
        iso_day_date[1] += 1
    iso_day_date[2] = week_day_number[week_day_titles[day_string]]
    day_date = date_from_iso(iso_day_date)

    blocks = get_blocks(user_id, day_date)[1]
    if is_prev:
        block_index = (current_block - 1) % len(blocks)
    else:
        block_index = (current_block + 1) % len(blocks)

    block = blocks[block_index]
    answer = "<b>{0} из {1}</b> <i>({2})</i>\n\n{3}".format(
        (block_index % len(blocks) + 1), len(blocks), day_string, block)
    events = [event.split("\n")[0] for event in block.split("\n\n")[1:-1]]
    return answer, events
