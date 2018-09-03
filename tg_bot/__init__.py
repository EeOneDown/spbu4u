# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from telebot import TeleBot, logger
from config import Config


bot = TeleBot(
    token=Config.TELEGRAM_BOT_RELEASE_TOKEN,
    threaded=Config.IS_THREADED_BOT
)

logger.setLevel(logging.INFO)


from tg_bot import handlers
