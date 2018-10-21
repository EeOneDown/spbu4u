from random import choice

from flask import g
from telebot.apihelper import ApiException

import telebot_login
from app import new_functions as nf
from app.constants import week_day_titles, loading_text, current_week_text
from tg_bot import bot
from tg_bot.keyboards import week_day_keyboard, current_next_keyboard


# Week schedule message
@bot.message_handler(
    func=lambda mess: mess.text.capitalize() == "Неделя",
    content_types=["text"]
)
@telebot_login.login_required_message
def week_handler(message):
    user = g.current_tbot_user

    bot.send_chat_action(user.tg_id, "typing")

    bot.send_message(
        chat_id=user.tg_id,
        text="Выбери день:",
        reply_markup=week_day_keyboard()
    )


# Week schedule callback
@bot.callback_query_handler(
    func=lambda call_back: call_back.message.text == "Выбери день:"
)
@telebot_login.login_required_callback
def select_week_day_schedule_handler(call_back):
    user = g.current_tbot_user

    if call_back.data == "Вся неделя":
        day = "Неделя"
    else:
        day = nf.get_key_by_value(week_day_titles, call_back.data)

    bot.edit_message_text(
        text="Расписание на: <i>{0}</i>\n".format(day),
        chat_id=user.tg_id,
        message_id=call_back.message.message_id,
        parse_mode="HTML",
        reply_markup=current_next_keyboard()
    )


# All week schedule callback
@bot.callback_query_handler(
    func=lambda call_back: "Расписание на: Неделя" in call_back.message.text
)
@bot.callback_query_handler(
    func=lambda call_back: current_week_text in call_back.message.text
)
@telebot_login.login_required_callback
@telebot_login.help_decorators.expected_failure_spbu_callback
def all_week_schedule_handler(call_back):
    user = g.current_tbot_user

    bot_msg = bot.edit_message_text(
        text="{0}\U00002026".format(choice(loading_text["schedule"])),
        chat_id=user.tg_id,
        message_id=call_back.message.message_id
    )
    answers = user.create_answers_for_interval(
        from_date=nf.get_work_monday(
            is_next_week=call_back.data == "Следующее"
        )
    )
    nf.tgbot_edit_first_and_send_messages(bot, answers, bot_msg)


# Week type callback
@bot.callback_query_handler(
    func=lambda call_back: call_back.data == "Текущее"
)
@bot.callback_query_handler(
    func=lambda call_back: call_back.data == "Следующее"
)
@telebot_login.help_decorators.expected_failure_spbu_callback
@telebot_login.login_required_callback
def week_day_schedule_handler(call_back):
    user = g.current_tbot_user

    bot_msg = bot.edit_message_text(
        text="{0}\U00002026".format(choice(loading_text["schedule"])),
        chat_id=user.tg_id,
        message_id=call_back.message.message_id
    )
    answer = user.create_answer_for_date(
        nf.get_date_by_weekday_title(
            title=week_day_titles[call_back.message.text.split(": ")[-1]],
            is_next_week=call_back.data == "Следующее"
        )
    )
    try:
        bot.edit_message_text(
            text=answer,
            chat_id=user.tg_id,
            message_id=bot_msg.message_id,
            parse_mode="HTML"
        )
    except ApiException:
        nf.tgbot_send_long_message(bot, answer, user.tg_id)
