from random import choice

from flask import g

import telebot_login
from app import new_functions as nf
from app.constants import loading_text
from tg_bot import bot
from tg_bot.keyboards import att_months_keyboard


# Session message
@bot.message_handler(
    func=lambda mess: mess.text.title() == "Сессия",
    content_types=["text"]
)
@bot.message_handler(
    func=lambda mess: mess.text.title() == "Допса",
    content_types=["text"]
)
@telebot_login.login_required_message
@telebot_login.help_decorators.expected_failure_spbu_message
def attestation_handler(message):
    user = g.current_tbot_user

    bot.send_chat_action(user.tg_id, "typing")

    is_resit = message.text.title() == "Допса"

    month = user.get_attestation_months(is_resit=is_resit)

    if month and not is_resit:
        answer = "Выбери месяц:"
    elif month and is_resit:
        answer = "Выбери месяц для <b>допсы</b>:"
    else:
        answer = "<i>Нет событий</i>"

    bot.send_message(
        chat_id=user.tg_id,
        text=answer,
        reply_markup=att_months_keyboard(month=month, text=message.text),
        parse_mode="HTML"
    )


# Switch callbacks
@bot.callback_query_handler(
    func=lambda call_back: call_back.data == "Допса"
)
@bot.callback_query_handler(
    func=lambda call_back: call_back.data == "Сессия"
)
@telebot_login.login_required_callback
@telebot_login.help_decorators.expected_failure_spbu_callback
def switch_session_type_handler(call_back):
    user = g.current_tbot_user

    bot_msg = bot.edit_message_text(
        text="{0}\U00002026".format(choice(loading_text["schedule"])),
        chat_id=call_back.message.chat.id,
        message_id=call_back.message.message_id
    )
    is_resit = call_back.data == "Допса"

    month = user.get_attestation_months(is_resit=is_resit)

    if month and not is_resit:
        answer = "Выбери месяц:"
    elif month and is_resit:
        answer = "Выбери месяц для <b>допсы</b>:"
    else:
        answer = "<i>Нет событий</i>"

    bot.edit_message_text(
        chat_id=call_back.message.chat.id,
        text=answer,
        message_id=bot_msg.message_id,
        parse_mode="HTML",
        reply_markup=att_months_keyboard(month=month, text=call_back.data)
    )


# Month callback
@bot.callback_query_handler(
    func=lambda call_back: "Выбери месяц" in call_back.message.text
)
@telebot_login.login_required_callback
@telebot_login.help_decorators.expected_failure_spbu_callback
def select_months_att_handler(call_back):
    user = g.current_tbot_user

    bot_msg = bot.edit_message_text(
        text="{0}\U00002026".format(choice(loading_text["schedule"])),
        chat_id=call_back.message.chat.id,
        message_id=call_back.message.message_id
    )
    answers = user.create_answers_for_interval(
        *nf.get_term_dates(),
        lessons_type="Attestation",
        is_resit=call_back.message.text != "Выбери месяц:"
    )
    nf.tgbot_edit_first_and_send_messages(bot, answers, bot_msg)
