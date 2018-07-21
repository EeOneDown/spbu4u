# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import g

from tg_bot import bot, functions as func
from app.constants import emoji
from tg_bot.keyboards import main_keyboard, settings_keyboard, suburban_keyboard, \
    schedule_keyboard, schedule_editor_keyboard
import telebot_login


# Cancel message (main menu)
@bot.message_handler(commands=["home"])
@bot.message_handler(
    func=lambda mess:
        mess.text.capitalize() == "Назад" or
        mess.text == emoji["back"], content_types=["text"]
    )
@telebot_login.login_required
def home_handler(message):
    user = g.current_tbot_user
    bot.send_chat_action(user.tg_id, "typing")
    answer = "Главное меню"
    bot.send_message(user.tg_id, answer, reply_markup=main_keyboard)


# Schedule menu message
@bot.message_handler(func=lambda mess: mess.text.capitalize() == "Расписание",
                     content_types=["text"])
@telebot_login.login_required
def schedule_handler(message):
    user = g.current_tbot_user
    bot.send_chat_action(user.tg_id, "typing")
    answer = "Меню расписания"
    bot.send_message(user.tg_id, answer, reply_markup=schedule_keyboard)


# Suburbans message
@bot.message_handler(func=lambda mess: mess.text == emoji["suburban"],
                     content_types=["text"])
@telebot_login.login_required
def suburban_handler(message):
    user = g.current_tbot_user
    bot.send_chat_action(user.tg_id, "typing")

    answer = "Меню расписания электричек\n\n" \
             "Данные предоставлены сервисом " \
             "<a href = 'http://rasp.yandex.ru/'>Яндекс.Расписания</a>"
    bot.send_message(user.tg_id,
                     answer,
                     reply_markup=suburban_keyboard,
                     parse_mode='HTML',
                     disable_web_page_preview=True)


# Editor message
@bot.message_handler(func=lambda mess: mess.text.title() == "Редактор",
                     content_types=["text"])
@bot.message_handler(func=lambda mess: mess.text == emoji["editor"],
                     content_types=["text"])
@telebot_login.login_required
def schedule_editor_handler(message):
    user = g.current_tbot_user
    bot.send_chat_action(user.tg_id, "typing")
    answer = "Редактор расписания"
    bot.send_message(user.tg_id,
                     answer,
                     reply_markup=schedule_editor_keyboard,
                     parse_mode='HTML')


# Settings message
@bot.message_handler(commands=["settings"])
@bot.message_handler(func=lambda mess: mess.text == emoji["settings"],
                     content_types=["text"])
@telebot_login.login_required
def settings_handler(message):
    user = g.current_tbot_user
    bot.send_chat_action(user.tg_id, "typing")
    answer = "Настройки"
    bot.send_message(user.tg_id, answer, reply_markup=settings_keyboard)


# Rate message
@bot.message_handler(func=lambda mess: mess.text == emoji["star"],
                     content_types=["text"])
def rate_handler(message):
    user = g.current_tbot_user
    bot.send_chat_action(user.tg_id, "typing")
    answer = "Оцените качество сервиса:"
    # TODO
    user_rate = func.get_user_rate(message.chat.id)
    rate_keyboard = InlineKeyboardMarkup(row_width=5)
    rate_keyboard.add(*[InlineKeyboardButton(
        text=emoji["star2"] if user_rate < count_of_stars else emoji["star"],
        callback_data=str(count_of_stars))
        for count_of_stars in (1, 2, 3, 4, 5)])
    rate_keyboard.add(
        *[InlineKeyboardButton(text=name, callback_data=name)
          for name in ["Связь", "Статистика"]])
    bot.send_message(user.tg_id, answer, parse_mode="HTML",
                     reply_markup=rate_keyboard)
