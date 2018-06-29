# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
from json import loads
from time import time

from flask import render_template, request, abort, current_app
from telebot.apihelper import ApiException
from telebot.types import Update

from bot import bot
from app.constants import webhook_url_base, webhook_url_path, ids
from bot.functions import delete_user, write_log
from app.main import bp


@bp.route("/")
@bp.route("/index")
def main_page():
    from requests import get

    url = "https://api.rasp.yandex.net/v3.0/copyright/"
    params = {"apikey": current_app.config['YANDEX_API_KEY'], "format": "json"}

    data = get(url, params=params).json()["copyright"]

    return render_template("index.html", bot_name="Spbu4UBot", url=data["url"],
                           text=data["text"])


@bp.route("/reset_webhook", methods=["GET", "HEAD"])
def reset_webhook():
    bot.remove_webhook()
    bot.set_webhook(url=webhook_url_base + webhook_url_path)
    return "OK", 200


@bp.route(webhook_url_path, methods=["POST"])
def webhook():
    if request.headers.get("content-type") == "application/json":
        json_string = request.get_data().decode("utf-8")
        update = Update.de_json(json_string)
        was_error = False
        tic = time()
        try:
            bot.process_new_updates([update])
        except Exception as err:
            answer = "Кажется, произошла ошибка.\n" \
                     "Возможно, информация по этому поводу есть в нашем " \
                     "канале - @Spbu4u_news\nИ ты всегда можешь связаться с " \
                     "<a href='https://t.me/eeonedown'>разработчиком</a>"
            was_error = True
            if update.message is not None:
                try:
                    bot.send_message(update.message.chat.id,
                                     answer,
                                     disable_web_page_preview=True,
                                     parse_mode="HTML")
                    bot.send_message(ids["my"],
                                     str(err) + "\n\nWas sent: True")
                except ApiException as ApiExcept:
                    json_err = loads(ApiExcept.result.text)
                    if json_err["description"] == "Forbidden: bot was " \
                                                  "blocked by the user":
                        delete_user(update.message.chat.id)
                        logging.info("USER LEFT {0}".format(
                            update.message.chat.id))
                    else:
                        logging.info("ERROR: {0}".format(
                            json_err["description"]))
            else:
                pass
        finally:
            write_log(update, time() - tic, was_error)
        return "OK", 200
    else:
        abort(403)


@bp.route("/test_route", methods=["POST"])
def test_route():
    json_string = request.get_data().decode("utf-8")
    print(json_string)
    update = Update.de_json(json_string)
    bot.process_new_updates([update])
    return "OK", 200
