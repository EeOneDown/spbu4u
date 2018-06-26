# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from bot import bot


if __name__ == '__main__':
    bot.remove_webhook()
    bot.polling(none_stop=True, interval=0)
