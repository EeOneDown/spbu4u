# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from telebot import TeleBot, logger

from bot.bots_constants import release_token


bot = TeleBot(release_token, threaded=False)

logger.setLevel(logging.INFO)


from bot import handlers
