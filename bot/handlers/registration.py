# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import bot.registration_functions as reg_func
from bot import bot


# Registration stage
@bot.message_handler(func=lambda mess:
                     reg_func.get_step(mess.chat.id) == "select_division" and
                     mess.text != "/home" and mess.text.capitalize() != "Назад",
                     content_types=["text"])
def select_division_handler(message):
    bot.send_chat_action(message.chat.id, "typing")
    reg_func.select_division(message)
    return


# Registration stage
@bot.message_handler(func=lambda mess:
                     reg_func.get_step(mess.chat.id) == "select_study_level" and
                     mess.text != "/home" and mess.text.capitalize() != "Назад",
                     content_types=["text"])
def select_study_level_handler(message):
    bot.send_chat_action(message.chat.id, "typing")
    reg_func.select_study_level(message)
    return


# Registration stage
@bot.message_handler(
    func=lambda mess:
        reg_func.get_step(mess.chat.id) == "select_study_program_combination"
        and mess.text != "/home" and mess.text.capitalize() != "Назад",
    content_types=["text"])
def select_study_program_combination_handler(message):
    bot.send_chat_action(message.chat.id, "typing")
    reg_func.select_study_program_combination(message)
    return


# Registration stage
@bot.message_handler(func=lambda mess:
                     reg_func.get_step(mess.chat.id) == "select_admission_year"
                     and mess.text != "/home" and
                     mess.text.capitalize() != "Назад",
                     content_types=["text"])
def select_admission_year_handler(message):
    bot.send_chat_action(message.chat.id, "typing")
    reg_func.select_admission_year(message)
    return


# Registration stage
@bot.message_handler(func=lambda mess:
                     reg_func.get_step(mess.chat.id) == "select_student_group"
                     and mess.text != "/home" and
                     mess.text.capitalize() != "Назад",
                     content_types=["text"])
def select_student_group_handler(message):
    bot.send_chat_action(message.chat.id, "typing")
    reg_func.select_student_group(message)
    return


# Registration stage
@bot.message_handler(func=lambda mess:
                     reg_func.get_step(mess.chat.id) == "confirm_choice" and
                     mess.text != "/home" and mess.text.capitalize() != "Назад",
                     content_types=["text"])
def confirm_choice_handler(message):
    bot.send_chat_action(message.chat.id, "typing")
    reg_func.confirm_choice(message)
    return
