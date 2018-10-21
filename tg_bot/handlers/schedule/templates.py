from flask import g

import telebot_login
from app import db
from app.constants import emoji, templates_answer
from tg_bot import bot
from tg_bot.handlers.start import start_handler
from tg_bot.keyboards import status_templates_keyboard, templates_list_keyboard


# Templates message
@bot.message_handler(
    func=lambda mess: mess.text == emoji["arrows_counterclockwise"],
    content_types=["text"]
)
@telebot_login.login_required_message
def templates_handler(message):
    user = g.current_tbot_user

    bot.send_chat_action(user.tg_id, "typing")

    answer = templates_answer.format(
        user.get_current_status_title()
    )
    bot.send_message(
        chat_id=user.tg_id,
        text=answer,
        reply_markup=status_templates_keyboard(),
        parse_mode="HTML"
    )


# Groups/Educators templates
@bot.callback_query_handler(
    func=lambda call_back: call_back.data == "Группы"
)
@bot.callback_query_handler(
    func=lambda call_back: call_back.data == "Преподаватели"
)
@telebot_login.login_required_callback
def g_e_templates(call_back):
    user = g.current_tbot_user

    last_row = ["Отмена"]
    if call_back.data == "Группы":
        items = user.groups.all()
        choose_text = "группу"
        no_items_text = "групп"
        if not user.is_educator:
            last_row.append(user.get_sav_del_button_text())
    else:
        items = user.educators.all()
        choose_text = "преподавателя"
        no_items_text = "преподавателей"
        if user.is_educator:
            last_row.append(user.get_sav_del_button_text())

    if items:
        answer = "Выбери {0} для переключения:".format(choose_text)
    else:
        answer = "Нет сохраненных {0}.".format(no_items_text)

    bot.edit_message_text(
        text=answer,
        chat_id=user.tg_id,
        message_id=call_back.message.message_id,
        parse_mode="HTML",
        reply_markup=templates_list_keyboard(items, last_row)
    )


# Save/Delete into/from templates callback
@bot.callback_query_handler(
    func=lambda call_back: call_back.data == "Сохранить"
)
@bot.callback_query_handler(
    func=lambda call_back: call_back.data == "Удалить"
)
@telebot_login.login_required_callback
def sav_del_current_status_handler(call_back):
    user = g.current_tbot_user

    if call_back.data == "Сохранить":
        user.save_current_status_into_templates()
        sav_del_text = "сохранен"
        if not user.is_educator:
            sav_del_text += "а"
    else:
        user.delete_current_status_from_templates()
        sav_del_text = "удален"
        if not user.is_educator:
            sav_del_text += "а"

    db.session.commit()

    if user.is_educator:
        answer = "Преподаватель <b>{0}</b> {1}.".format(
            user.get_current_status_title(),
            sav_del_text
        )
    else:
        answer = "Группа <b>{0}</b> {1}.".format(
            user.get_current_status_title(),
            sav_del_text
        )
    bot.edit_message_text(
        text=answer,
        chat_id=user.tg_id,
        message_id=call_back.message.message_id,
        parse_mode="HTML"
    )


# Choose template callback
@bot.callback_query_handler(
    func=lambda call_back:
        "Выбери группу для переключения:" in call_back.message.text
)
@bot.callback_query_handler(
    func=lambda call_back:
        "Выбери преподавателя для переключения:" in call_back.message.text
)
@telebot_login.login_required_callback
def change_template_handler(call_back):
    user = g.current_tbot_user

    if "группу" in call_back.message.text:
        user.current_group_id = call_back.data
        user.current_educator_id = 0
        user.is_educator = False
    else:
        user.current_group_id = 0
        user.current_educator_id = call_back.data
        user.is_educator = True

    answer = "Изменено. Текущее расписания для <b>{0}</b>".format(
        user.get_current_status_title()
    )
    db.session.commit()

    bot.edit_message_text(
        text=answer,
        chat_id=user.tg_id,
        message_id=call_back.message.message_id,
        parse_mode="HTML"
    )


# Relogin callback
@bot.callback_query_handler(
    func=lambda call_back: call_back.data == "Перезайти"
)
@telebot_login.login_required_callback
def relogin_callback_handler(call_back):
    user = g.current_tbot_user

    answer = "<i>Перезайти</i>\nИспользуй /home для отмены"
    bot.edit_message_text(
        text=answer,
        chat_id=user.tg_id,
        message_id=call_back.message.message_id,
        parse_mode="HTML"
    )
    call_back.message.text = call_back.data
    start_handler(call_back.message)
