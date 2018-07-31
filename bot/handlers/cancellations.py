# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from telebot.apihelper import ApiException

from bot import bot, functions as func


# Cancel user by message
@bot.message_handler(func=lambda mess: not func.is_user_exist(mess.chat.id),
                     content_types=["text"])
def not_exist_user_handler(message):
    bot.send_chat_action(message.chat.id, "typing")
    answer = "Чтобы начать пользоваться сервисом, необходимо " \
             "зарегистрироваться.\nВоспользуйся коммандой /start"
    bot.send_message(message.chat.id, answer)


# Cancel callback
@bot.callback_query_handler(func=lambda call_back:
                            call_back.data == "Отмена")
def cancel_handler(call_back):
    answer = "Отмена"
    try:
        bot.edit_message_text(text=answer, chat_id=call_back.message.chat.id,
                              message_id=call_back.message.message_id)
    except ApiException:
        pass


# Cancel user by callback
@bot.callback_query_handler(func=lambda call_back:
                            not func.is_user_exist(call_back.message.chat.id))
def not_exist_user_callback_handler(call_back):
    answer = "Чтобы пользоваться сервисом, необходимо " \
             "зарегистрироваться.\nВоспользуйся коммандой /start"
    bot.edit_message_text(text=answer,
                          chat_id=call_back.message.chat.id,
                          message_id=call_back.message.message_id,
                          parse_mode="HTML")
