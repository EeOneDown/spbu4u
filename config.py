import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config(object):
    # DB
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    # fix MySQL - https://www.pythonanywhere.com/forums/topic/2465/
    SQLALCHEMY_POOL_RECYCLE = 280
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # end fix
    # TG
    TELEGRAM_BOT_RELEASE_TOKEN = os.getenv('TELEGRAM_BOT_RELEASE_TOKEN')
    BOT_NAME = os.getenv('BOT_NAME')
    IS_THREADED_BOT = True if os.getenv('IS_THREADED_BOT') == "True" else False
    # YANDEX
    YANDEX_API_KEY = os.getenv('YANDEX_API_KEY')
    # FLASK
    BASE_DOMAIN = os.getenv('BASE_DOMAIN')
    SECRET_KEY = os.getenv('SECRET_KEY')
    OTHER_SECRET_KEY = os.getenv('OTHER_SECRET_KEY')
