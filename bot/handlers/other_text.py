# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import bot.functions as func
from bot import bot


# Other message
@bot.message_handler(func=lambda mess: True, content_types=["text"])
def other_text_handler(message):
    bot.send_chat_action(message.chat.id, "typing")
    answer = "Не понимаю"
    func.send_long_message(bot, answer, message.chat.id)
