# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import telebot_login
from tg_bot import bot


# Other message
@bot.message_handler(func=lambda mess: True, content_types=["text"])
@telebot_login.login_required
def other_text_handler(message):
    bot.reply_to(message, "Не понимаю")
