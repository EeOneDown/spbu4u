# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from app.constants import (
    main_menu_first_answer
)
from app.models import User
from tg_bot import bot
from tg_bot.keyboards import main_keyboard


# Group callback
@bot.callback_query_handler(
    func=lambda call_back: "Выбери группу:" in call_back.message.text
)
# Educator choose message
@bot.callback_query_handler(
    func=lambda call_back: call_back.message.text == "Выбери преподавателя:"
)
def register_student_handler(call_back):
    bot_msg = bot.edit_message_text(
        text="Почти готово! Запоминаю твой выбор\U00002026",
        chat_id=call_back.message.chat.id,
        message_id=call_back.message.message_id
    )
    user = User.reg_user(
        o_id=int(call_back.data),
        is_edu=call_back.message.text == "Выбери преподавателя:",
        tg_id=call_back.message.chat.id
    )
    bot.edit_message_text(
        chat_id=user.tg_id,
        text="Готово!",
        message_id=bot_msg.message_id
    )
    bot.send_message(
        text=main_menu_first_answer,
        parse_mode="HTML",
        chat_id=user.tg_id,
        reply_markup=main_keyboard()
    )
