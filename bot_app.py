# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from tg_bot import bot
from app import create_app


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        from telebot import apihelper
        apihelper.proxy = {"https": "socks5://127.0.0.1:9150"}
        bot.remove_webhook()
        bot.polling(none_stop=True, interval=0)
