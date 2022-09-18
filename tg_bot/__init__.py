from telebot import TeleBot
from config import Config


bot = TeleBot(
    token=Config.TELEGRAM_BOT_RELEASE_TOKEN,
    threaded=Config.IS_THREADED_BOT
)


from tg_bot import handlers  # noqa
