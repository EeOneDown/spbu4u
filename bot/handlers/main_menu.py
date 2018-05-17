# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot import bot, functions as func
from bot.constants import emoji
from bot.keyboards import main_keyboard, settings_keyboard, suburban_keyboard, \
    schedule_keyboard, schedule_editor_keyboard


# Cancel message (main menu)
@bot.message_handler(commands=["home"])
@bot.message_handler(
    func=lambda mess:
        mess.text.capitalize() == "Назад" or
        mess.text == emoji["back"], content_types=["text"])
def home_handler(message):
    bot.send_chat_action(message.chat.id, "typing")
    func.delete_user(message.chat.id, only_choice=True)
    answer = "Главное меню"
    bot.send_message(message.chat.id, answer, reply_markup=main_keyboard)


# Schedule menu message
@bot.message_handler(func=lambda mess: mess.text.capitalize() == "Расписание",
                     content_types=["text"])
def schedule_handler(message):
    bot.send_chat_action(message.chat.id, "typing")
    answer = "Меню расписания"
    bot.send_message(message.chat.id, answer, reply_markup=schedule_keyboard)


# Suburbans message
@bot.message_handler(func=lambda mess: mess.text == emoji["suburban"],
                     content_types=["text"])
def suburban_handler(message):
    bot.send_chat_action(message.chat.id, "typing")

    answer = "Меню расписания электричек\n\n" \
             "Данные предоставлены сервисом " \
             "<a href = 'http://rasp.yandex.ru/'>Яндекс.Расписания</a>"
    bot.send_message(message.chat.id,
                     answer,
                     reply_markup=suburban_keyboard,
                     parse_mode='HTML',
                     disable_web_page_preview=True)


# Editor message
@bot.message_handler(func=lambda mess: mess.text.title() == "Редактор",
                     content_types=["text"])
@bot.message_handler(func=lambda mess: mess.text == emoji["editor"],
                     content_types=["text"])
def schedule_editor_handler(message):
    bot.send_chat_action(message.chat.id, "typing")
    answer = "Редактор расписания"
    bot.send_message(message.chat.id,
                     answer,
                     reply_markup=schedule_editor_keyboard,
                     parse_mode='HTML')


# Settings message
@bot.message_handler(commands=["settings"])
@bot.message_handler(func=lambda mess: mess.text == emoji["settings"],
                     content_types=["text"])
def settings_handler(message):
    bot.send_chat_action(message.chat.id, "typing")
    func.delete_user(message.chat.id, only_choice=True)
    answer = "Настройки"
    bot.send_message(message.chat.id, answer, reply_markup=settings_keyboard)


# Rate message
@bot.message_handler(func=lambda mess: mess.text == emoji["star"],
                     content_types=["text"])
def rate_handler(message):
    bot.send_chat_action(message.chat.id, "typing")
    answer = "Оцените качество сервиса:"
    user_rate = func.get_user_rate(message.chat.id)
    rate_keyboard = InlineKeyboardMarkup(row_width=5)
    rate_keyboard.add(*[InlineKeyboardButton(
        text=emoji["star2"] if user_rate < count_of_stars else emoji["star"],
        callback_data=str(count_of_stars))
        for count_of_stars in (1, 2, 3, 4, 5)])
    rate_keyboard.add(
        *[InlineKeyboardButton(text=name, callback_data=name)
          for name in ["Связь", "Статистика"]])
    bot.send_message(message.chat.id, answer, parse_mode="HTML",
                     reply_markup=rate_keyboard)
