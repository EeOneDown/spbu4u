# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from telebot import TeleBot, logger
from config import Config


bot = TeleBot(Config.TELEGRAM_BOT_RELEASE_TOKEN, threaded=False)

logger.setLevel(logging.INFO)


from bot import handlers
