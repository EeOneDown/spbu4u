from flask import g

import telebot_login
from app import db
from app.constants import (
    emoji, sending_off_answer, sending_on_answer, sending_info_answer
)
from tg_bot import bot
from tg_bot.keyboards import sending_keyboard


# Schedule sending message
@bot.message_handler(
    func=lambda mess: mess.text == emoji["alarm_clock"],
    content_types=["text"]
)
@telebot_login.login_required_message
def sending_handler(message):
    user = g.current_tbot_user

    bot.send_chat_action(user.tg_id, "typing")

    bot.send_message(
        chat_id=user.tg_id,
        text=sending_info_answer,
        parse_mode="HTML",
        reply_markup=sending_keyboard(user.is_subscribed)
    )


# Subscribe/Unsubscribe for sending callback
@bot.callback_query_handler(
    func=lambda call_back: call_back.data == "Подписаться"
)
@bot.callback_query_handler(
    func=lambda call_back: call_back.data == "Отписаться"
)
@telebot_login.login_required_callback
def sending_subscribing_handler(call_back):
    user = g.current_tbot_user

    if call_back.data == "Отписаться":
        user.is_subscribed = False
        answer = sending_off_answer
    else:
        user.is_subscribed = True
        answer = sending_on_answer

    db.session.commit()

    bot.edit_message_text(
        text=answer,
        chat_id=user.tg_id,
        message_id=call_back.message.message_id,
        parse_mode="HTML"
    )
