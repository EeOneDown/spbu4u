# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config(object):
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TELEGRAM_BOT_RELEASE_TOKEN = os.getenv('TELEGRAM_BOT_RELEASE_TOKEN')
    OTHER_SECRET_KEY = os.getenv('OTHER_SECRET_KEY')
    YANDEX_API_KEY = os.getenv('YANDEX_API_KEY')
    BOT_NAME = os.getenv('BOT_NAME')
    IS_THREADED_BOT = True if os.getenv('IS_THREADED_BOT') == "True" else False
