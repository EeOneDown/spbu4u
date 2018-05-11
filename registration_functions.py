# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

import spbu
import telebot

import functions


def set_next_step(user_id, next_step):
    sql_con = functions.get_connection()
    cursor = sql_con.cursor()
    cursor.execute("""UPDATE user_choice
                      SET step = %s 
                      WHERE user_id = %s""",
                   (next_step, user_id))
    sql_con.commit()
    cursor.close()
    sql_con.close()


def get_step(user_id):
    sql_con = functions.get_connection()
    cursor = sql_con.cursor()
    cursor.execute("""SELECT  step
                      FROM user_choice
                      WHERE user_id = %s""", (user_id, ))
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

    sql_con = functions.get_connection()
    cursor = sql_con.cursor()
    cursor.execute("""SELECT divisions_json 
                      FROM user_choice 
                      WHERE user_id = %s""", (message.chat.id,))
    data = cursor.fetchone()
    cursor.close()
    sql_con.close()

    divisions = json.loads(data[0])
    division_names = [division["Name"].strip() for division in divisions]
    aliases = [division["Alias"].strip() for division in divisions]
    if message.text in division_names:
        answer += "Выбери ступень:"
        study_programs_keyboard = telebot.types.ReplyKeyboardMarkup(
            resize_keyboard=True, one_time_keyboard=False
        )
        index = division_names.index(message.text)
        alias = aliases[index]
        study_programs = spbu.get_program_levels(alias)
        for study_program in study_programs:
            study_programs_keyboard.row(study_program["StudyLevelName"])
        study_programs_keyboard.row("Другое направление")

        data = json.dumps(study_programs)
        sql_con = functions.get_connection()
        cursor = sql_con.cursor()
        cursor.execute("""UPDATE user_choice 
                          SET alias = %s, division_name = %s, 
                              study_programs_json = %s 
                          WHERE user_id = %s""",
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

    sql_con = functions.get_connection()
    cursor = sql_con.cursor()
    cursor.execute("""SELECT study_programs_json 
                      FROM user_choice 
                      WHERE user_id = %s""", (message.chat.id,))
    data = cursor.fetchone()[0]
    cursor.close()
    sql_con.close()

    study_programs = json.loads(data)

    study_level_names = []
    for study_program in study_programs:
        study_level_names.append(study_program["StudyLevelName"].strip())
    if message.text in study_level_names:
        answer += "Укажи программу:"
        study_program_combinations_keyboard = telebot.types.ReplyKeyboardMarkup(
            resize_keyboard=True, one_time_keyboard=False
        )
        index = study_level_names.index(message.text)
        study_program_combinations = study_programs[index][
            "StudyProgramCombinations"]
        for study_program_combination in study_program_combinations:
            study_program_combinations_keyboard.row(
                study_program_combination["Name"])
        study_program_combinations_keyboard.row("Другая ступень")

        sql_con = functions.get_connection()
        cursor = sql_con.cursor()
        cursor.execute("""UPDATE user_choice 
                          SET study_level_name = %s
                          WHERE user_id = %s""",
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

    sql_con = functions.get_connection()
    cursor = sql_con.cursor()
    cursor.execute("""SELECT study_level_name, study_programs_json 
                      FROM user_choice 
                      WHERE user_id = %s""", (message.chat.id,))
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
            study_program_combination["Name"].strip())
    if message.text in study_program_combination_names:
        answer += "Укажи год поступления:"
        admission_years_keyboard = telebot.types.ReplyKeyboardMarkup(
            resize_keyboard=True, one_time_keyboard=False
        )
        index = study_program_combination_names.index(message.text)
        admission_years = study_program_combinations[index]["AdmissionYears"]
        for admission_year in admission_years:
            admission_years_keyboard.row(admission_year["YearName"])
        admission_years_keyboard.row("Другая программа")

        sql_con = functions.get_connection()
        cursor = sql_con.cursor()
        cursor.execute("""UPDATE user_choice
                          SET study_program_combination_name = %s 
                          WHERE user_id = %s""",
                       (message.text, message.chat.id))
        sql_con.commit()
        cursor.close()
        sql_con.close()

        bot.send_message(message.chat.id, answer,
                         reply_markup=admission_years_keyboard)
        set_next_step(message.chat.id, "select_admission_year")
    elif message.text == "Другая ступень":
        sql_con = functions.get_connection()
        cursor = sql_con.cursor()
        cursor.execute("""SELECT division_name 
                          FROM user_choice 
                          WHERE user_id = %s""", (message.chat.id,))
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

    sql_con = functions.get_connection()
    cursor = sql_con.cursor()
    cursor.execute("""SELECT study_programs_json, study_level_name, 
                             study_program_combination_name
                      FROM user_choice 
                      WHERE user_id = %s""", (message.chat.id,))
    data = cursor.fetchone()
    cursor.close()
    sql_con.close()

    study_programs = json.loads(data[0])
    study_level_name = data[1]
    study_program_combination_name = data[2]
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
        admission_year_names.append(admission_year["YearName"].strip())
    if message.text in admission_year_names:
        answer += "Укажи группу:"
        index = admission_year_names.index(message.text)
        study_program_id = admission_years[index]["StudyProgramId"]
        student_groups = spbu.get_groups(study_program_id)
        student_group_names = []
        for student_group in student_groups["Groups"]:
            student_group_names.append(student_group["StudentGroupName"])
        student_groups_keyboard = telebot.types.ReplyKeyboardMarkup(
            resize_keyboard=True, one_time_keyboard=False
        )
        for student_group_name in student_group_names:
            student_groups_keyboard.row(student_group_name)
        student_groups_keyboard.row("Другой год")
        data = json.dumps(student_groups)

        sql_con = functions.get_connection()
        cursor = sql_con.cursor()
        cursor.execute("""UPDATE user_choice 
                          SET admission_year_name = %s, 
                              student_groups_json = %s 
                          WHERE user_id = %s""",
                       (message.text, data, message.chat.id))
        sql_con.commit()
        cursor.close()
        sql_con.close()

        bot.send_message(message.chat.id, answer,
                         reply_markup=student_groups_keyboard)
        set_next_step(message.chat.id, "select_student_group")
    elif message.text == "Другая программа":
        sql_con = functions.get_connection()
        cursor = sql_con.cursor()
        cursor.execute("""SELECT study_level_name
                          FROM user_choice 
                          WHERE user_id = %s""", (message.chat.id,))
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

    sql_con = functions.get_connection()
    cursor = sql_con.cursor()
    cursor.execute("""SELECT student_groups_json
                      FROM user_choice 
                      WHERE user_id = %s""", (message.chat.id,))
    data = cursor.fetchone()[0]
    cursor.close()
    sql_con.close()

    student_groups = json.loads(data)
    student_group_names = []
    for student_group in student_groups["Groups"]:
        student_group_names.append(student_group["StudentGroupName"].strip())
    if message.text in student_group_names:
        index = student_group_names.index(message.text)
        student_group_id = student_groups["Groups"][index]["StudentGroupId"]

        sql_con = functions.get_connection()
        cursor = sql_con.cursor()
        cursor.execute("""UPDATE user_choice 
                          SET student_group_name = %s, 
                              student_group_id = %s 
                          WHERE user_id = %s""",
                       (message.text, student_group_id, message.chat.id))
        sql_con.commit()
        cursor.execute("""SELECT division_name, study_level_name, 
                                 study_program_combination_name,
                                 admission_year_name, student_group_name 
                          FROM user_choice 
                          WHERE user_id = %s""", (message.chat.id,))
        data = cursor.fetchone()
        cursor.close()
        sql_con.close()

        text = ">> " + "\n>> ".join(data)
        answer += "Подтверди выбор:\n" + "<b>" + text + "</b>"
        choice_keyboard = telebot.types.ReplyKeyboardMarkup(
            resize_keyboard=True, one_time_keyboard=False
        )
        buttons = ["Все верно", "Другая группа", "Другой год",
                   "Другая программа", "Другая ступень", "Другое направление"]
        for button in buttons:
            choice_keyboard.row(button)
        bot.send_message(message.chat.id, answer, parse_mode="HTML",
                         reply_markup=choice_keyboard)
        set_next_step(message.chat.id, "confirm_choice")
    elif message.text == "Другой год":
        sql_con = functions.get_connection()
        cursor = sql_con.cursor()
        cursor.execute("""SELECT study_program_combination_name
                          FROM user_choice 
                          WHERE user_id = %s""", (message.chat.id,))
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
        sql_con = functions.get_connection()
        cursor = sql_con.cursor()
        cursor.execute("""SELECT student_group_id
                          FROM user_choice 
                          WHERE user_id = %s""", (message.chat.id,))
        group_id = cursor.fetchone()[0]
        user_id = message.chat.id

        cursor.close()
        sql_con.close()

        functions.add_new_user(user_id, group_id)

        answer = "Главное меню\n\n" \
                 "{0} - информация о боте\n" \
                 "{1} - оценить бота\n" \
                 "{2} - настройки\n" \
                 "{3} - электрички\n" \
                 "{4} - <b>редактор расписания</b>\n" \
                 "@Spbu4u_news - новости бота".format(emoji["info"],
                                                      emoji["star"],
                                                      emoji["settings"],
                                                      emoji["suburban"],
                                                      emoji["editor"])
        bot.send_message(message.chat.id, answer, reply_markup=main_keyboard,
                         parse_mode="HTML")
    elif message.text == "Другая группа":
        sql_con = functions.get_connection()
        cursor = sql_con.cursor()
        cursor.execute("""SELECT admission_year_name
                          FROM user_choice 
                          WHERE user_id = %s""", (message.chat.id,))
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
