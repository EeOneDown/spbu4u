# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot import bot
from bot.constants import emoji, briefly_info_answer, special_thanks


# Info message
@bot.message_handler(commands=["help"])
@bot.message_handler(func=lambda mess: mess.text == emoji["info"],
                     content_types=["text"])
def help_handler(message):
    bot.send_chat_action(message.chat.id, "typing")
    inline_full_info_keyboard = InlineKeyboardMarkup()
    inline_full_info_keyboard.row(
        *[InlineKeyboardButton(text=name, callback_data=name) for
          name in ["Благодарности"]])
    answer = briefly_info_answer
    bot.send_message(message.chat.id, answer,
                     parse_mode="HTML",
                     reply_markup=inline_full_info_keyboard,
                     disable_web_page_preview=True)


# Thanks callback for info message
@bot.callback_query_handler(func=lambda call_back:
                            call_back.data == "Благодарности")
def show_full_info(call_back):
    answer = special_thanks
    bot.edit_message_text(text=answer,
                          chat_id=call_back.message.chat.id,
                          message_id=call_back.message.message_id,
                          parse_mode="HTML",
                          disable_web_page_preview=True)
    inline_answer = "И тебе :)"
    bot.answer_callback_query(call_back.id, inline_answer, cache_time=1)
