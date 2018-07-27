# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import spbu
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from app.constants import max_inline_button_text_len


def select_status_keyboard():
    """
    Creates select status keyboard

    :return: select status keyboard
    :rtype: InlineKeyboardMarkup
    """
    inline_keyboard = InlineKeyboardMarkup()
    inline_keyboard.row(
        *[InlineKeyboardButton(text=name, callback_data=name) for
          name in ["Преподаватель", "Студент"]]
    )
    return inline_keyboard


def divisions_keyboard():
    """
    Creates divisions keyboard

    :return: division keyboard
    :rtype: InlineKeyboardMarkup
    """
    divisions = spbu.get_study_divisions()

    inline_keyboard = InlineKeyboardMarkup(row_width=1)
    inline_keyboard.add(
        *[InlineKeyboardButton(
            text=d["Name"][:max_inline_button_text_len],
            callback_data=d["Alias"]
        ) for d in divisions]
    )
    return inline_keyboard


def levels_keyboard(alias):
    """
    Creates levels keyboard for alias

    :param alias: division's short name code (alias)
    :type alias: str
    :return: levels keyboard
    :rtype: InlineKeyboardMarkup
    """
    levels = spbu.get_program_levels(alias)

    inline_keyboard = InlineKeyboardMarkup(row_width=1)
    inline_keyboard.add(
        *[InlineKeyboardButton(
            text=l["StudyLevelName"][:max_inline_button_text_len],
            callback_data=l["StudyLevelName"][:max_inline_button_text_len]
        ) for l in levels]
    )
    return inline_keyboard


def programs_keyboard(alias, level_slice):
    """
    Creates programs keyboard for input alias and level (may be slice)

    :param alias: division's short name code (alias)
    :type alias: str
    :param level_slice: level's name (slice)
    :type level_slice: str
    :return: programs keyboard
    :rtype: InlineKeyboardMarkup
    """
    levels = spbu.get_program_levels(alias)

    programs = []
    for level in levels:
        if level_slice in level["StudyLevelName"]:
            programs = level["StudyProgramCombinations"]
            break

    inline_keyboard = InlineKeyboardMarkup(row_width=1)
    inline_keyboard.add(
        *[InlineKeyboardButton(
            text=p["Name"][:max_inline_button_text_len],
            callback_data=p["Name"][:max_inline_button_text_len]
        ) for p in programs]
    )
    return inline_keyboard


def years_keyboard(path, program_slice):
    """
    Create years keyboard for input path and program slice

    :param path: student's registration way joined by `/`
    :type path: str
    :param program_slice: program's name (slice)
    :type program_slice: str
    :return: years keyboard
    :rtype: InlineKeyboardMarkup
    """
    alias, level_slice = path.split("/")[:2]

    levels = spbu.get_program_levels(alias)

    years = []
    for level in levels:
        if level_slice in level["StudyLevelName"]:
            for program in level["StudyProgramCombinations"]:
                if program_slice in program["Name"]:
                    years = program["AdmissionYears"]
                    break
            break

    inline_keyboard = InlineKeyboardMarkup(row_width=1)
    inline_keyboard.add(
        *[InlineKeyboardButton(
            text=y["YearName"],
            callback_data=y["StudyProgramId"]
        ) for y in years]
    )
    return inline_keyboard


def groups_keyboard(program_id):
    """
    Creates groups keyboard for program's id

    :param program_id: student's program id
    :type program_id: int
    :return: groups keyboard
    :rtype: InlineKeyboardMarkup
    """
    groups = spbu.get_groups(program_id)

    inline_keyboard = InlineKeyboardMarkup(row_width=1)
    inline_keyboard.add(
        *[InlineKeyboardButton(
            text=g["StudentGroupName"],
            callback_data=g["StudentGroupId"]
        ) for g in groups]
    )
    return inline_keyboard


def found_educators_keyboard(data, need_cancel=False):
    """
    Creates inline keyboard with found educators

    :param data: spbu api json response
    :type data: dict
    :param need_cancel: is need to add `cancel` button
    :return:
    """
    inline_keyboard = InlineKeyboardMarkup(row_width=1)
    inline_keyboard.add(
        *[InlineKeyboardButton(
            text=educator["FullName"][:max_inline_button_text_len],
            callback_data=str(educator["Id"])
        ) for educator in data["Educators"]]
    )
    if need_cancel:
        inline_keyboard.row(InlineKeyboardButton(
            text="Отмена", callback_data="Отмена")
        )
    return inline_keyboard
