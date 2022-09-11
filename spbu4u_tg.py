from tg_bot import bot
from app import create_app


if __name__ == '__main__':
    with create_app().app_context():
        bot.delete_webhook()
        bot.polling(none_stop=True, interval=0)
