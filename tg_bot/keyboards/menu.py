# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import date

from telebot.types import ReplyKeyboardMarkup

from app.constants import emoji


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
