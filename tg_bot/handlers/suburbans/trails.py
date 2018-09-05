from datetime import date, timedelta
from random import choice

from flask import g
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

import telebot_login
from app import new_functions as nf
from app.constants import (
    emoji, all_stations, loading_text, fast_trail_answer_select_day
)
from tg_bot import bot
from tg_bot.keyboards import (
    start_station_keyboard, end_station_keyboard, select_day_keyboard,
    update_keyboard
)


# Fast trail messages
@bot.message_handler(
    func=lambda mess: mess.text.title() == "В Универ",
    content_types=["text"]
)
@bot.message_handler(
    func=lambda mess: mess.text.title() == "Домой",
    content_types=["text"]
)
@telebot_login.login_required_message
def fast_trail_handler(message):
    user = g.current_tbot_user

    bot.send_chat_action(user.tg_id, "typing")

    if message.text.title() == "В Универ":
        from_code = user.home_station_code
        to_code = user.univer_station_code
    else:
        from_code = user.univer_station_code
        to_code = user.home_station_code

    answer, is_tomorrow, is_error = nf.create_suburbans_answer(
        from_code=from_code,
        to_code=to_code,
        for_date=date.today()
    )

    if not is_error:
        if is_tomorrow:
            bot.send_message(
                chat_id=user.tg_id,
                text=emoji["warning"] + " На сегодня нет электричек"
            )
        inline_keyboard = update_keyboard(for_tomorrow=is_tomorrow)
    else:
        inline_keyboard = InlineKeyboardMarkup()

    bot.send_message(
        chat_id=user.tg_id,
        text=answer,
        reply_markup=inline_keyboard,
        parse_mode='HTML',
        disable_web_page_preview=True
    )


# Trail message
@bot.message_handler(
    func=lambda mess: mess.text.title() == "Маршрут",
    content_types=["text"]
)
@telebot_login.login_required_message
def own_trail_handler(message):
    user = g.current_tbot_user

    bot.send_message(
        chat_id=user.tg_id,
        text="Выбери начальную станцию:",
        reply_markup=start_station_keyboard()
    )


# personal trails callbacks
@bot.callback_query_handler(
    func=lambda call_back: call_back.data == "Домой"
)
@bot.callback_query_handler(
    func=lambda call_back: call_back.data == "В Универ"
)
@telebot_login.login_required_callback
def to_home_or_univer_handler(call_back):
    user = g.current_tbot_user

    if call_back.data == "В Универ":
        from_code = user.home_station_code
        to_code = user.univer_station_code
    else:
        from_code = user.univer_station_code
        to_code = user.home_station_code

    answer = fast_trail_answer_select_day.format(
        from_title=nf.get_key_by_value(all_stations, from_code),
        to_title=nf.get_key_by_value(all_stations, to_code)
    )
    bot.edit_message_text(
        text=answer,
        chat_id=user.tg_id,
        message_id=call_back.message.message_id,
        reply_markup=select_day_keyboard(),
        parse_mode="HTML"
    )


# From station callback
@bot.callback_query_handler(
    func=lambda call_back: call_back.message.text == "Выбери начальную станцию:"
)
@telebot_login.login_required_callback
def start_station_handler(call_back):
    user = g.current_tbot_user

    answer = "Начальная: <b>{0}</b>\nВыбери конечную станцию:".format(
        call_back.data
    )
    bot.edit_message_text(
        text=answer,
        chat_id=user.tg_id,
        message_id=call_back.message.message_id,
        reply_markup=end_station_keyboard(call_back.data),
        parse_mode="HTML"
    )


# Change start station callback
@bot.callback_query_handler(
    func=lambda call_back: call_back.data == "Изменить начальную"
)
@telebot_login.login_required_callback
def change_start_station_handler(call_back):
    user = g.current_tbot_user

    answer = "Выбери начальную станцию:"

    bot.edit_message_text(
        text=answer,
        chat_id=user.tg_id,
        message_id=call_back.message.message_id,
        reply_markup=start_station_keyboard()
    )


# To station callback
@bot.callback_query_handler(
    func=lambda call_back: "Выбери конечную станцию:" in call_back.message.text
)
@telebot_login.login_required_callback
def end_station_handler(call_back):
    user = g.current_tbot_user

    answer = nf.add_end_station(call_back.message.text, call_back.data)

    inline_keyboard = select_day_keyboard()
    inline_keyboard.row(
        *[InlineKeyboardButton(text=name, callback_data=name)
          for name in ["Изменить конечную"]]
    )
    bot.edit_message_text(
        text=answer,
        chat_id=user.tg_id,
        message_id=call_back.message.message_id,
        reply_markup=inline_keyboard,
        parse_mode="HTML"
    )


# Change end station callback
@bot.callback_query_handler(
    func=lambda call_back: call_back.data == "Изменить конечную"
)
@telebot_login.login_required_callback
def change_end_station_handler(call_back):
    user = g.current_tbot_user

    start_station = nf.get_station_title_from_text(call_back.message.text)

    answer = "Начальная: <b>{0}</b>\nВыбери конечную станцию:".format(
        start_station
    )
    bot.edit_message_text(
        text=answer,
        chat_id=user.tg_id,
        message_id=call_back.message.message_id,
        reply_markup=end_station_keyboard(start_station)
    )


# Day callback
@bot.callback_query_handler(
    func=lambda call_back: "Выбери день:" in call_back.message.text
)
@telebot_login.login_required_callback
def build_trail_handler(call_back):
    user = g.current_tbot_user

    bot_msg = bot.edit_message_text(
        text="{0}\U00002026".format(choice(loading_text["ya_timetable"])),
        chat_id=user.tg_id,
        message_id=call_back.message.message_id
    )
    answer, is_tomorrow, is_error = nf.create_suburbans_answer(
        from_code=nf.get_station_code_from_text(
            call_back.message.text
        ),
        to_code=nf.get_station_code_from_text(
            call_back.message.text, is_end=True
        ),
        for_date=date.today() + timedelta(
            days=(1 if call_back.data == "Завтра" else 0)
        ),
        limit=7 if call_back.data == "Завтра" else 3
    )
    if not is_error:
        if call_back.data == "Завтра" or is_tomorrow:
            if is_tomorrow:
                inline_answer = emoji["warning"] + " На сегодня нет электричек"
                bot.answer_callback_query(
                    call_back.id, inline_answer, show_alert=True
                )
            inline_keyboard = update_keyboard(for_tomorrow=True)
        else:
            inline_keyboard = update_keyboard()
    else:
        inline_keyboard = InlineKeyboardMarkup()

    bot.edit_message_text(
        text=answer,
        chat_id=user.tg_id,
        message_id=bot_msg.message_id,
        reply_markup=inline_keyboard,
        parse_mode="HTML"
    )
