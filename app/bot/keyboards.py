# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from telebot import types
from time import localtime
from app.bot.constants import emoji


main_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True,
                                          one_time_keyboard=False)
if localtime().tm_mon in [12, 1, 5, 6]:
    main_keyboard.row("Сессия", "Расписание")
else:
    main_keyboard.row("Расписание")
main_keyboard.row(emoji["info"], emoji["star"], emoji["settings"],
                  emoji["suburban"], emoji["editor"])


schedule_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True,
                                              one_time_keyboard=False)
schedule_keyboard.row("Сегодня", "Завтра", "Неделя")
schedule_keyboard.row(emoji["back"], emoji["bust_in_silhouette"],
                      emoji["arrows_counterclockwise"],
                      emoji["alarm_clock"])


settings_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True,
                                              one_time_keyboard=False)
settings_keyboard.row("Сменить группу", "Завершить")
settings_keyboard.row("Назад", "Поддержка")


suburban_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True,
                                              one_time_keyboard=False)
suburban_keyboard.row("Домой", "В Универ", "Маршрут")
suburban_keyboard.row("Назад", "Персонализация")


schedule_editor_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True,
                                                     one_time_keyboard=False)
schedule_editor_keyboard.row("Скрыть", "Выбрать", "Вернуть")
schedule_editor_keyboard.row("Назад", "Адрес")
