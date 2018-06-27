# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TELEGRAM_BOT_RELEASE_TOKEN = os.environ.get('TELEGRAM_BOT_RELEASE_TOKEN')
    OTHER_SECRET_KEY = os.environ.get('OTHER_SECRET_KEY')
    YANDEX_API_KEY = os.environ.get('YANDEX_API_KEY')
    BOT_NAME = os.environ.get('BOT_NAME')
