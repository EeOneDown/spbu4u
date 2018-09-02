# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from flask import g

from tg_bot import bot
from app.constants import emoji
from tg_bot.keyboards import (
    main_keyboard, settings_keyboard, suburban_keyboard, schedule_keyboard,
    schedule_editor_keyboard, rate_keyboard
)
import telebot_login


# Cancel message (main menu)
@bot.message_handler(commands=["home"])
@bot.message_handler(
    func=lambda mess: mess.text.capitalize() == "Назад",
    content_types=["text"]
)
@bot.message_handler(
    func=lambda mess: mess.text == emoji["back"],
    content_types=["text"]
)
@telebot_login.login_required_message
def home_handler(message):
    user = g.current_tbot_user
    bot.send_chat_action(user.tg_id, "typing")
    answer = "Главное меню"
    bot.send_message(
        chat_id=user.tg_id,
        text=answer,
        reply_markup=main_keyboard()
    )


# Schedule menu message
@bot.message_handler(
    func=lambda mess: mess.text.capitalize() == "Расписание",
    content_types=["text"]
)
@telebot_login.login_required_message
def schedule_handler(message):
    user = g.current_tbot_user
    bot.send_chat_action(user.tg_id, "typing")
    answer = "Меню расписания"
    bot.send_message(
        chat_id=user.tg_id,
        text=answer,
        reply_markup=schedule_keyboard()
    )


# Suburbans message
@bot.message_handler(
    func=lambda mess: mess.text == emoji["suburban"],
    content_types=["text"]
)
@telebot_login.login_required_message
def suburban_handler(message):
    user = g.current_tbot_user
    bot.send_chat_action(user.tg_id, "typing")

    answer = "Меню расписания электричек\n\n" \
             "Данные предоставлены сервисом " \
             "<a href = 'http://rasp.yandex.ru/'>Яндекс.Расписания</a>"
    bot.send_message(
        chat_id=user.tg_id,
        text=answer,
        reply_markup=suburban_keyboard(),
        parse_mode='HTML',
        disable_web_page_preview=True
    )


# Editor message
@bot.message_handler(
    func=lambda mess: mess.text.title() == "Редактор",
    content_types=["text"]
)
@bot.message_handler(
    func=lambda mess: mess.text == emoji["editor"],
    content_types=["text"]
)
@telebot_login.login_required_message
def schedule_editor_handler(message):
    user = g.current_tbot_user
    bot.send_chat_action(user.tg_id, "typing")
    answer = "Редактор расписания"
    bot.send_message(
        chat_id=user.tg_id,
        text=answer,
        reply_markup=schedule_editor_keyboard(),
        parse_mode='HTML'
    )


# Settings message
@bot.message_handler(commands=["settings"])
@bot.message_handler(
    func=lambda mess: mess.text == emoji["settings"],
    content_types=["text"]
)
@telebot_login.login_required_message
def settings_handler(message):
    user = g.current_tbot_user
    bot.send_chat_action(user.tg_id, "typing")
    answer = "Настройки"
    bot.send_message(
        chat_id=user.tg_id,
        text=answer,
        reply_markup=settings_keyboard()
    )


# Rate message
@bot.message_handler(
    func=lambda mess: mess.text == emoji["star"],
    content_types=["text"]
)
@telebot_login.login_required_message
def rate_handler(message):
    user = g.current_tbot_user

    bot.send_message(
        chat_id=user.tg_id,
        text="Оцените качество сервиса:",
        parse_mode="HTML",
        reply_markup=rate_keyboard(user.rate or 0)
    )
