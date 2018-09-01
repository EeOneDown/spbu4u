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
    keyboard.row(
        "Допса" if date.today().month in [2, 9] else "Сессия", "Расписание"
    )
    return keyboard.row(
        emoji["info"], emoji["star"], emoji["settings"], emoji["suburban"],
        emoji["editor"]
    )


def schedule_keyboard():
    """
    Creates schedule menu keyboard

    :return: schedule menu keyboard
    :rtype: ReplyKeyboardMarkup
    """
    return ReplyKeyboardMarkup(
        resize_keyboard=True, one_time_keyboard=False
    ).row(
        "Сегодня", "Завтра", "Неделя"
    ).row(
        emoji["back"], emoji["bust_in_silhouette"],
        emoji["arrows_counterclockwise"], emoji["alarm_clock"]
    )


def settings_keyboard():
    """
    Creates settings menu keyboard

    :return: settings menu keyboard
    :rtype: ReplyKeyboardMarkup
    """
    return ReplyKeyboardMarkup(
        resize_keyboard=True, one_time_keyboard=False
    ).row(
        "Сменить группу", "Завершить"
    ).row(
        "Назад", "Поддержка"
    )


def suburban_keyboard():
    """
    Creates suburbans menu keyboard

    :return: suburbans menu keyboard
    :rtype: ReplyKeyboardMarkup
    """
    return ReplyKeyboardMarkup(
        resize_keyboard=True, one_time_keyboard=False
    ).row(
        "Домой", "В Универ", "Маршрут"
    ).row(
        "Назад", "Персонализация"
    )


def schedule_editor_keyboard():
    """
    Creates editor keyboard

    :return: editor menu keyboard
    :rtype: ReplyKeyboardMarkup
    """
    return ReplyKeyboardMarkup(
        resize_keyboard=True, one_time_keyboard=False
    ).row(
        "Скрыть", "Выбрать", "Вернуть"
    ).row(
        "Назад", "Адрес"
    )
