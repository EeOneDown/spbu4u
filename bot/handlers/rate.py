# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from telebot.apihelper import ApiException
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ForceReply

from bot import bot, functions as func
from bot.bots_constants import bot_name
from bot.constants import emoji, ids
from bot.keyboards import main_keyboard


# Feedback text message
@bot.message_handler(
    func=lambda mess:
        mess.reply_to_message is not None and
        mess.reply_to_message.from_user.username == bot_name and
        mess.reply_to_message.text == "Напиши мне что-нибудь:",
    content_types=["text"])
def users_callback_handler(message):
    bot.send_chat_action(message.chat.id, "typing")
    bot.forward_message(ids["my"], message.chat.id, message.message_id)
    bot.send_message(message.chat.id, "Записал", reply_markup=main_keyboard,
                     reply_to_message_id=message.message_id)


# Statistics callback
@bot.callback_query_handler(func=lambda call_back:
                            call_back.data == "Статистика")
def statistics_handler(call_back):
    data = func.get_rate_statistics()
    if data is None:
        answer = "Пока что нет оценок."
    else:
        rate = emoji["star"] * int(round(data[0]))
        answer = "Средняя оценка: {0}\n{1} ({2})".format(
                                            round(data[0], 1), rate, data[1])
    if call_back.message.chat.id in ids.values():
        admin_data = func.get_statistics_for_admin()
        admin_answer = "\n\nКолличество пользователей: {0}\n" \
                       "Колличество групп: {1}\nКолличество пользователей с " \
                       "активной рассылкой: {2}".format(
                                    admin_data["count_of_users"],
                                    admin_data["count_of_groups"],
                                    admin_data["count_of_sending"])
        bot.send_message(call_back.message.chat.id, admin_answer)
    try:
        bot.edit_message_text(text=answer,
                              chat_id=call_back.message.chat.id,
                              message_id=call_back.message.message_id,
                              parse_mode="HTML")
    except ApiException:
        pass


# Feedback callback
@bot.callback_query_handler(func=lambda call_back:
                            call_back.data == "Связь")
def feedback_handler(call_back):
    markup = ForceReply(False)
    try:
        bot.edit_message_text(text="Обратная связь",
                              chat_id=call_back.message.chat.id,
                              message_id=call_back.message.message_id)
    except ApiException:
        pass
    finally:
        answer = "Напиши мне что-нибудь:"
        bot.send_message(call_back.message.chat.id, answer,
                         reply_markup=markup)


# Rate mark callback
@bot.callback_query_handler(func=lambda call_back:
                            call_back.data in ["1", "2", "3", "4", "5"])
def set_rate_handler(call_back):
    rate = call_back.data
    answer = ""
    func.set_rate(call_back.message.chat.id, rate)
    if rate == "5":
        answer += "{0} Пятёрка! Супер! Спасибо большое!".format(emoji["smile"])
    elif rate == "4":
        answer += "{0} Стабильная четверочка. Спасибо!".format(emoji["halo"])
    elif rate == "3":
        answer += "{0} Удовлетворительно? Ничего... тоже оценка. " \
                  "Буду стараться лучше.".format(emoji["cold_sweat"])
    elif rate == "2":
        answer += "{0} Двойка? Быть может, я могу что-то исправить? " \
                  "Сделать лучше?\n\nОпиши проблему " \
                  "<a href='https://t.me/eeonedown'>разработчику</a>, " \
                  "и вместе мы ее решим!".format(emoji["disappointed"])
    elif rate == "1":
        answer += "{0} Единица? Быть может, я могу что-то исправить? " \
                  "Сделать лучше?\n\nОпиши проблему " \
                  "<a href='https://t.me/eeonedown'>разработчику</a>, " \
                  "и вместе мы ее решим!".format(emoji["disappointed"])
    user_rate = func.get_user_rate(call_back.message.chat.id)
    rate_keyboard = InlineKeyboardMarkup(row_width=5)
    rate_keyboard.add(*[InlineKeyboardButton(
        text=emoji["star2"] if user_rate < count_of_stars else emoji["star"],
        callback_data=str(count_of_stars))
        for count_of_stars in (1, 2, 3, 4, 5)])
    rate_keyboard.add(
        *[InlineKeyboardButton(text=name, callback_data=name)
          for name in ["Связь", "Статистика"]])
    try:
        bot.edit_message_text(text=answer,
                              chat_id=call_back.message.chat.id,
                              message_id=call_back.message.message_id,
                              parse_mode="HTML",
                              reply_markup=rate_keyboard,
                              disable_web_page_preview=True)
    except ApiException:
        pass
