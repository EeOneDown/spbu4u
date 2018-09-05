from tg_bot import bot
from app.constants import (
    emoji, all_stations, personalization_answer, select_home_station,
    select_univer_station
)
from app import new_functions as nf, db
from flask import g
import telebot_login
from tg_bot.keyboards import stations_keyboard, personalization_keyboard


# Personalization message
@bot.message_handler(
    func=lambda mess: mess.text.title() == "Персонализация",
    content_types=["text"]
)
@telebot_login.login_required_message
def personalisation_handler(message):
    user = g.current_tbot_user

    home_title = nf.get_key_by_value(all_stations, user.home_station_code)
    univer_title = nf.get_key_by_value(all_stations, user.univer_station_code)

    answer = personalization_answer.format(home_title, univer_title)

    bot.send_message(
        chat_id=user.tg_id,
        text=answer,
        reply_markup=personalization_keyboard(),
        parse_mode="HTML"
    )


# Choose station type callback
@bot.callback_query_handler(
    func=lambda call_back: call_back.data == "Домашняя"
)
@bot.callback_query_handler(
    func=lambda call_back: call_back.data == "Университетская"
)
@telebot_login.login_required_callback
def home_station_handler(call_back):
    user = g.current_tbot_user

    if call_back.data == "Домашняя":
        answer = select_home_station
    else:
        answer = select_univer_station

    bot.edit_message_text(
        text=answer,
        chat_id=user.tg_id,
        message_id=call_back.message.message_id,
        reply_markup=stations_keyboard()
    )


# Choose station callback
@bot.callback_query_handler(
    func=lambda call_back: call_back.message.text == select_home_station
)
@bot.callback_query_handler(
    func=lambda call_back: call_back.message.text == select_univer_station
)
@telebot_login.login_required_callback
def change_home_station_handler(call_back):
    user = g.current_tbot_user

    is_both_changed = False
    if "домашнюю" in call_back.message.text:
        if call_back.data == user.univer_station_code:
            user.univer_station_code = user.home_station_code
            is_both_changed = True
        user.home_station_code = call_back.data
        type_station = "Домашняя"
    else:
        if call_back.data == user.home_station_code:
            user.home_station_code = user.univer_station_code
            is_both_changed = True
        user.univer_station_code = call_back.data
        type_station = "Университетская"

    answer = "{0} станция изменена на <b>{1}</b>\n".format(
        type_station,
        nf.get_key_by_value(all_stations, call_back.data)
    )
    if is_both_changed:
        inline_answer = "{0} Изменены обе станции!".format(emoji["warning"])
        bot.answer_callback_query(
            callback_query_id=call_back.id,
            text=inline_answer,
            show_alert=True
        )
    db.session.commit()

    bot.edit_message_text(
        text=answer,
        chat_id=user.tg_id,
        message_id=call_back.message.message_id,
        parse_mode="HTML"
    )
