# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import spbu

from telebot.types import (
    InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
)
from datetime import date
from app.constants import emoji, all_stations, max_inline_button_text_len


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


def main_keyboard():
    """
    Creates main menu keyboard

    :return: main menu keyboard
    :rtype: ReplyKeyboardMarkup
    """
    keyboard = ReplyKeyboardMarkup(
        resize_keyboard=True, one_time_keyboard=False
    )
    if date.today().month in [12, 1, 5, 6]:
        keyboard.row("Сессия", "Расписание")
    else:
        keyboard.row("Расписание")
        keyboard.row(
            emoji["info"], emoji["star"], emoji["settings"], emoji["suburban"],
            emoji["editor"]
        )
    return keyboard


def schedule_keyboard():
    """
    Creates schedule menu keyboard

    :return: schedule menu keyboard
    :rtype: ReplyKeyboardMarkup
    """
    keyboard = ReplyKeyboardMarkup(
        resize_keyboard=True, one_time_keyboard=False
    )
    keyboard.row("Сегодня", "Завтра", "Неделя")
    keyboard.row(
        emoji["back"], emoji["bust_in_silhouette"],
        emoji["arrows_counterclockwise"], emoji["alarm_clock"]
    )
    return keyboard


def settings_keyboard():
    """
    Creates settings menu keyboard

    :return: settings menu keyboard
    :rtype: ReplyKeyboardMarkup
    """
    keyboard = ReplyKeyboardMarkup(
        resize_keyboard=True, one_time_keyboard=False
    )
    keyboard.row("Сменить группу", "Завершить")
    keyboard.row("Назад", "Поддержка")
    return keyboard


def suburban_keyboard():
    """
    Creates suburbans menu keyboard

    :return: suburbans menu keyboard
    :rtype: ReplyKeyboardMarkup
    """
    keyboard = ReplyKeyboardMarkup(
        resize_keyboard=True, one_time_keyboard=False
    )
    keyboard.row("Домой", "В Универ", "Маршрут")
    keyboard.row("Назад", "Персонализация")
    return keyboard


def schedule_editor_keyboard():
    """
    Creates editor keyboard

    :return: editor menu keyboard
    :rtype: ReplyKeyboardMarkup
    """
    keyboard = ReplyKeyboardMarkup(
        resize_keyboard=True, one_time_keyboard=False
    )
    keyboard.row("Скрыть", "Выбрать", "Вернуть")
    keyboard.row("Назад", "Адрес")
    return keyboard


def start_station_keyboard():
    """
    Creates start station keyboard

    :return: start station keyboard
    :rtype: InlineKeyboardMarkup
    """
    inline_keyboard = InlineKeyboardMarkup(row_width=1)
    inline_keyboard.add(
        *[InlineKeyboardButton(text=name, callback_data=name)
          for name in all_stations.keys()]
    )
    inline_keyboard.row(
        *[InlineKeyboardButton(text=name, callback_data=name)
          for name in ["Домой", "В Универ"]]
    )
    return inline_keyboard


def end_station_keyboard(chosen_station):
    """
    Creates end station inline keyboard

    :param chosen_station: chosen station title
    :type chosen_station: str
    :return: inline keyboard
    :rtype: InlineKeyboardMarkup
    """
    inline_keyboard = InlineKeyboardMarkup()
    inline_keyboard.add(
        *[InlineKeyboardButton(text=name, callback_data=name)
          for name in all_stations.keys() if name != chosen_station]
    )
    inline_keyboard.row(
        *[InlineKeyboardButton(text=name, callback_data=name)
          for name in ["Изменить начальную"]]
    )
    return inline_keyboard


def select_day_keyboard():
    """
    Creates select day keyboard

    :return: select day keyboard
    :rtype: InlineKeyboardMarkup
    """
    inline_keyboard = InlineKeyboardMarkup()
    inline_keyboard.row(
        *[InlineKeyboardButton(text=name, callback_data=name)
          for name in ["Сегодня", "Завтра"]]
    )
    return inline_keyboard


def update_keyboard(show_less=False, for_tomorrow=False):
    """
    Creates suburbans update keyboard

    :param show_less: is need to use nearest's buttons
    :type show_less: bool
    :param for_tomorrow: is need to use tomorrow's buttons
    :type for_tomorrow: bool
    :return: suburbans update keyboard
    :rtype: InlineKeyboardMarkup
    """
    inline_keyboard = InlineKeyboardMarkup()

    if for_tomorrow:
        if show_less:
            buttons = [InlineKeyboardButton(text=name, callback_data=name)
                       for name in ["Самые ранние"]]
        else:
            buttons = [InlineKeyboardButton(text=name, callback_data=name)
                       for name in ["Все на завтра"]]
    else:
        if show_less:
            buttons = [InlineKeyboardButton(text=name, callback_data=name)
                       for name in ["Ближайшие", "Обновить"]]
        else:
            buttons = [InlineKeyboardButton(text=name, callback_data=name)
                       for name in ["Оставшиеся", "Обновить"]]

    inline_keyboard.row(*buttons)

    return inline_keyboard


def special_thanks_keyboard():
    """
    Creates special thanks keyboard

    :return: special thanks keyboard
    :rtype: InlineKeyboardMarkup
    """
    inline_keyboard = InlineKeyboardMarkup()
    inline_keyboard.row(
        *[InlineKeyboardButton(text=name, callback_data=name)
          for name in ["Благодарности"]]
    )
    return inline_keyboard


def found_educators(data, need_cancel=True):
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
