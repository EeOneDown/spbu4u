# -*- coding: utf-8 -*-
import json
import sqlite3
import requests
import telebot


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


def select_division(message):
    from flask_app import bot

    answer = ""

    sql_con = sqlite3.connect("Bot_db")
    cursor = sql_con.cursor()
    cursor.execute("""SELECT divisions_json 
                      FROM user_choice 
                      WHERE user_id = ?""", (message.chat.id,))
    data = cursor.fetchone()
    cursor.close()
    sql_con.close()

    divisions = json.loads(data[0])
    division_names = [division["Name"] for division in divisions]
    aliases = [division["Alias"] for division in divisions]
    if message.text in division_names:
        answer += "Выбери ступень:"
        study_programs_keyboard = telebot.types.ReplyKeyboardMarkup(True, False)
        index = division_names.index(message.text)
        alias = aliases[index]
        study_programs = requests.get(
            "https://timetable.spbu.ru/api/v1/{}/studyprograms".format(alias)
        ).json()
        for study_program in study_programs:
            study_programs_keyboard.row(study_program["StudyLevelName"])
        study_programs_keyboard.row("Другое направление")

        data = json.dumps(study_programs)
        sql_con = sqlite3.connect("Bot_db")
        cursor = sql_con.cursor()
        cursor.execute("""UPDATE user_choice 
                          SET alias = ?, division_name = ?, 
                              study_programs_json = ? 
                          WHERE user_id = ?""",
                       (alias, message.text, data, message.chat.id))
        sql_con.commit()
        cursor.close()
        sql_con.close()

        bot.send_message(message.chat.id, answer,
                         reply_markup=study_programs_keyboard)
        set_next_step(message.chat.id, "select_study_level")
    else:
        answer += "Пожалуйста, укажи направление:"
        bot.send_message(message.chat.id, answer)
        set_next_step(message.chat.id, "select_division")


def select_study_level(message):
    from flask_app import bot, start_handler

    answer = ""

    sql_con = sqlite3.connect("Bot_db")
    cursor = sql_con.cursor()
    cursor.execute("""SELECT study_programs_json 
                      FROM user_choice 
                      WHERE user_id = ?""", (message.chat.id,))
    data = cursor.fetchone()[0]
    cursor.close()
    sql_con.close()

    study_programs = json.loads(data)

    study_level_names = []
    for study_program in study_programs:
        study_level_names.append(study_program["StudyLevelName"])
    if message.text in study_level_names:
        answer += "Укажи программу:"
        study_program_combinations_keyboard = telebot.types.ReplyKeyboardMarkup(
            True, False)
        index = study_level_names.index(message.text)
        study_program_combinations = study_programs[index][
            "StudyProgramCombinations"]
        for study_program_combination in study_program_combinations:
            study_program_combinations_keyboard.row(
                study_program_combination["Name"])
        study_program_combinations_keyboard.row("Другая ступень")

        sql_con = sqlite3.connect("Bot_db")
        cursor = sql_con.cursor()
        cursor.execute("""UPDATE user_choice 
                          SET study_level_name = ?
                          WHERE user_id = ?""",
                       (message.text, message.chat.id))
        sql_con.commit()
        cursor.close()
        sql_con.close()

        bot.send_message(message.chat.id, answer,
                         reply_markup=study_program_combinations_keyboard)
        set_next_step(message.chat.id, "select_study_program_combination")
    elif message.text == "Другое направление":
        start_handler(message)
        return
    else:
        answer += "Пожалуйста, укажи ступень:"
        bot.send_message(message.chat.id, answer)
        set_next_step(message.chat.id, "select_study_level")


def select_study_program_combination(message):
    from flask_app import bot

    answer = ""

    sql_con = sqlite3.connect("Bot_db")
    cursor = sql_con.cursor()
    cursor.execute("""SELECT study_level_name, study_programs_json 
                      FROM user_choice 
                      WHERE user_id = ?""", (message.chat.id,))
    data = cursor.fetchone()
    cursor.close()
    sql_con.close()

    study_level_name, study_programs = data[0], json.loads(data[1])
    study_level_names = []
    for study_program in study_programs:
        study_level_names.append(study_program["StudyLevelName"])
    index = study_level_names.index(study_level_name)
    study_program_combinations = study_programs[index][
        "StudyProgramCombinations"]
    study_program_combination_names = []
    for study_program_combination in study_program_combinations:
        study_program_combination_names.append(
            study_program_combination["Name"])
    if message.text in study_program_combination_names:
        answer += "Укажи год поступления:"
        admission_years_keyboard = telebot.types.ReplyKeyboardMarkup(True,
                                                                     False)
        index = study_program_combination_names.index(message.text)
        admission_years = study_program_combinations[index]["AdmissionYears"]
        for admission_year in admission_years:
            admission_years_keyboard.row(admission_year["YearName"])
        admission_years_keyboard.row("Другая программа")

        sql_con = sqlite3.connect("Bot_db")
        cursor = sql_con.cursor()
        cursor.execute("""UPDATE user_choice
                          SET study_program_combination_name = ? 
                          WHERE user_id = ?""",
                       (message.text, message.chat.id))
        sql_con.commit()
        cursor.close()
        sql_con.close()

        bot.send_message(message.chat.id, answer,
                         reply_markup=admission_years_keyboard)
        set_next_step(message.chat.id, "select_admission_year")
    elif message.text == "Другая ступень":
        sql_con = sqlite3.connect("Bot_db")
        cursor = sql_con.cursor()
        cursor.execute("""SELECT division_name 
                          FROM user_choice 
                          WHERE user_id = ?""", (message.chat.id,))
        data = cursor.fetchone()
        cursor.close()
        sql_con.close()

        message.text = data[0]
        select_division(message)
        return
    else:
        answer += "Пожалуйста, укажи программу:"
        bot.send_message(message.chat.id, answer)
        set_next_step(message.chat.id, "select_study_program_combination")


def select_admission_year(message):
    from flask_app import bot

    answer = ""

    sql_con = sqlite3.connect("Bot_db")
    cursor = sql_con.cursor()
    cursor.execute("""SELECT study_programs_json, study_level_name, 
                             study_program_combination_name, alias
                      FROM user_choice 
                      WHERE user_id = ?""", (message.chat.id,))
    data = cursor.fetchone()
    cursor.close()
    sql_con.close()

    study_programs = json.loads(data[0])
    study_level_name = data[1]
    study_program_combination_name = data[2]
    alias = data[3]
    study_level_names = []
    for study_program in study_programs:
        study_level_names.append(study_program["StudyLevelName"])
    index = study_level_names.index(study_level_name)
    study_program_combinations = study_programs[index][
        "StudyProgramCombinations"]
    study_program_combination_names = []
    for study_program_combination in study_program_combinations:
        study_program_combination_names.append(
            study_program_combination["Name"])
    index = study_program_combination_names.index(
        study_program_combination_name)
    admission_years = study_program_combinations[index]["AdmissionYears"]
    admission_year_names = []
    for admission_year in admission_years:
        admission_year_names.append(admission_year["YearName"])
    if message.text in admission_year_names:
        answer += "Укажи группу:"
        index = admission_year_names.index(message.text)
        study_program_id = admission_years[index]["StudyProgramId"]
        url = "https://timetable.spbu.ru/api/v1/{}/".format(alias) + \
              "studyprogram/{}/studentgroups".format(study_program_id)
        student_groups = requests.get(url).json()
        student_group_names = []
        for student_group in student_groups:
            student_group_names.append(student_group["StudentGroupName"])
        student_groups_keyboard = telebot.types.ReplyKeyboardMarkup(True, False)
        for student_group_name in student_group_names:
            student_groups_keyboard.row(student_group_name)
        student_groups_keyboard.row("Другой год")
        data = json.dumps(student_groups)

        sql_con = sqlite3.connect("Bot_db")
        cursor = sql_con.cursor()
        cursor.execute("""UPDATE user_choice 
                          SET admission_year_name = ?, 
                              student_groups_json = ? 
                          WHERE user_id = ?""",
                       (message.text, data, message.chat.id))
        sql_con.commit()
        cursor.close()
        sql_con.close()

        bot.send_message(message.chat.id, answer,
                         reply_markup=student_groups_keyboard)
        set_next_step(message.chat.id, "select_student_group")
    elif message.text == "Другая программа":
        sql_con = sqlite3.connect("Bot_db")
        cursor = sql_con.cursor()
        cursor.execute("""SELECT study_level_name
                          FROM user_choice 
                          WHERE user_id = ?""", (message.chat.id,))
        data = cursor.fetchone()
        cursor.close()
        sql_con.close()

        message.text = data[0]
        select_study_level(message)
        return
    else:
        answer += "Пожалуйста, укажи год:"
        bot.send_message(message.chat.id, answer)
        set_next_step(message.chat.id, "select_admission_year")


def select_student_group(message):
    from flask_app import bot

    answer = ""

    sql_con = sqlite3.connect("Bot_db")
    cursor = sql_con.cursor()
    cursor.execute("""SELECT student_groups_json
                      FROM user_choice 
                      WHERE user_id = ?""", (message.chat.id,))
    data = cursor.fetchone()[0]
    cursor.close()
    sql_con.close()

    student_groups = json.loads(data)
    student_group_names = []
    for student_group in student_groups:
        student_group_names.append(student_group["StudentGroupName"])
    if message.text in student_group_names:
        index = student_group_names.index(message.text)
        student_group_id = student_groups[index]["StudentGroupId"]

        sql_con = sqlite3.connect("Bot_db")
        cursor = sql_con.cursor()
        cursor.execute("""UPDATE user_choice 
                          SET student_group_name = ?, 
                              student_group_id = ? 
                          WHERE user_id = ?""",
                       (message.text, student_group_id, message.chat.id))
        sql_con.commit()
        cursor.execute("""SELECT division_name, study_level_name, 
                                 study_program_combination_name,
                                 admission_year_name, student_group_name 
                          FROM user_choice 
                          WHERE user_id = ?""", (message.chat.id,))
        data = cursor.fetchone()
        cursor.close()
        sql_con.close()

        text = ">> " + "\n>> ".join(data)
        answer += "Подтверди выбор:\n" + "<b>" + text + "</b>"
        choice_keyboard = telebot.types.ReplyKeyboardMarkup(True, False)
        buttons = ["Все верно", "Другая группа", "Другой год",
                   "Другая программа", "Другая ступень", "Другое направление"]
        for button in buttons:
            choice_keyboard.row(button)
        bot.send_message(message.chat.id, answer, parse_mode="HTML",
                         reply_markup=choice_keyboard)
        set_next_step(message.chat.id, "confirm_choice")
    elif message.text == "Другой год":
        sql_con = sqlite3.connect("Bot_db")
        cursor = sql_con.cursor()
        cursor.execute("""SELECT study_program_combination_name
                          FROM user_choice 
                          WHERE user_id = ?""", (message.chat.id,))
        data = cursor.fetchone()
        cursor.close()
        sql_con.close()

        message.text = data[0]
        select_study_program_combination(message)
        return
    else:
        answer += "Пожалуйста, укажи группу:"
        bot.send_message(message.chat.id, answer)
        set_next_step(message.chat.id, "select_student_group")


def confirm_choice(message):
    from flask_app import bot, start_handler, main_keyboard
    from constants import emoji

    if message.text == "Все верно":
        sql_con = sqlite3.connect("Bot_db")
        cursor = sql_con.cursor()
        cursor.execute("""SELECT alias, student_group_id
                          FROM user_choice 
                          WHERE user_id = ?""", (message.chat.id,))
        data = cursor.fetchone()
        alias = data[0]
        group_id = data[1]
        try:
            cursor.execute("""INSERT INTO user_data (id, alias, group_id)
                              VALUES (?, ?, ?)""",
                           (message.chat.id, alias, group_id))
        except sqlite3.IntegrityError:
            cursor.execute("""UPDATE user_data 
                              SET alias = ?, group_id = ?
                              WHERE id = ?""",
                           (alias, group_id, message.chat.id))
        finally:
            sql_con.commit()
            cursor.execute("""DELETE FROM user_choice WHERE user_id = ?""",
                           (message.chat.id,))
            sql_con.commit()
        url = "https://timetable.spbu.ru/api/v1/{}/".format(alias) + \
              "studentgroup/{}/events".format(group_id)
        week_data = requests.get(url).json()
        data = json.dumps(week_data)
        try:
            cursor.execute("""INSERT INTO groups_data 
                              (id, alias, json_week_data)
                              VALUES (?, ?, ?)""",
                           (group_id, alias, data))
        except sqlite3.IntegrityError:
            cursor.execute("""UPDATE groups_data
                              SET json_week_data = ?
                              WHERE id = ? AND alias = ?""",
                           (data, group_id, alias))
        finally:
            sql_con.commit()
            cursor.close()
            sql_con.close()
        answer = "Главное меню\n\n"
        answer += emoji["info"] + " - информация о боте\n"
        answer += emoji["star"] + " - оценить бота\n"
        answer += emoji["settings"] + " - настройки\n"
        answer += emoji["suburban"] + " - электрички\n"
        answer += emoji["editor"] + " - редактор расписания"
        bot.send_message(message.chat.id, answer, reply_markup=main_keyboard,
                         parse_mode="HTML")
    elif message.text == "Другая группа":
        sql_con = sqlite3.connect("Bot_db")
        cursor = sql_con.cursor()
        cursor.execute("""SELECT admission_year_name
                          FROM user_choice 
                          WHERE user_id = ?""", (message.chat.id,))
        data = cursor.fetchone()
        cursor.close()
        sql_con.close()

        message.text = data[0]
        select_admission_year(message)
        return
    elif message.text == "Другой год":
        select_student_group(message)
        return
    elif message.text == "Другая программа":
        select_admission_year(message)
        return
    elif message.text == "Другая ступень":
        select_study_program_combination(message)
        return
    elif message.text == "Другое направление":
        start_handler(message)
        return
