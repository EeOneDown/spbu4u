# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
from json import loads
from time import time

from flask import request, abort
from telebot.apihelper import ApiException
from telebot.types import Update

from app import db, new_functions as nf
from app.constants import (
    webhook_url_base, webhook_url_path, ids, other_error_answer
)
from app.models import User
from app.tg import bp
from tg_bot import bot


def run_bot(update):
    tic = time()
    was_error = False
    answer = "No error"
    try:
        bot.process_new_updates([update])
    except ApiException as ApiExcept:
        was_error = True
        json_err = loads(ApiExcept.result.text)
        if json_err["description"] == "Forbidden: tg_bot was blocked by " \
                                      "the user":
            if update.message:
                chat_id = update.message.chat.id
            else:
                chat_id = update.callback_query.message.chat.id
            user = User.query.filter_by(tg_id=chat_id).first()
            user.clear_all()
            db.session.delete(user)
            db.session.commit()

            logging.info("USER LEFT {0}".format(
                update.message.chat.id))
        else:
            logging.info("ERROR: {0}".format(
                json_err["description"]))
    except Exception as err:
        answer = other_error_answer
        was_error = True
        bot.send_message(
            chat_id=ids["my"],
            text=str(err)
        )
    finally:
        if was_error:
            if update.message:
                chat_id = update.message.chat.id
            else:
                chat_id = update.callback_query.message.chat.id
            bot.send_message(
                chat_id=chat_id,
                text=answer,
                disable_web_page_preview=True,
                parse_mode="HTML"
            )
        nf.write_log(update, time() - tic, was_error)


@bp.route("/reset_webhook", methods=["GET", "HEAD"])
def reset_webhook():
    bot.remove_webhook()
    bot.set_webhook(url=webhook_url_base + webhook_url_path)
    return "OK", 200


@bp.route(webhook_url_path, methods=["POST"])
def webhook():
    if request.headers.get("content-type") == "application/json":
        # Запускать бота фоновым процессом в RQ?
        run_bot(
            update=Update.de_json(
                json_type=request.get_data().decode("utf-8")
            )
        )
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
