from tg_bot import bot
from tg_bot.keyboards import (
    divisions_keyboard, levels_keyboard, programs_keyboard, years_keyboard,
    groups_keyboard
)


# Student status callback
@bot.callback_query_handler(
    func=lambda call_back: call_back.data == "Студент"
)
def select_division_handler(call_back):
    bot_msg = bot.edit_message_text(
        text="Загружаю список направлений\U00002026",
        chat_id=call_back.message.chat.id,
        message_id=call_back.message.message_id
    )
    bot.edit_message_text(
        text="Выбери направление:",
        chat_id=call_back.message.chat.id,
        message_id=bot_msg.message_id,
        reply_markup=divisions_keyboard()
    )


# Division callback
@bot.callback_query_handler(
    func=lambda call_back: call_back.message.text == "Выбери направление:"
)
def select_level_handler(call_back):
    bot_msg = bot.edit_message_text(
        text="Ищу подходящие ступени\U00002026",
        chat_id=call_back.message.chat.id,
        message_id=call_back.message.message_id
    )
    bot.edit_message_text(
        text="{0}/\n\nВыбери ступень:".format(call_back.data),
        chat_id=call_back.message.chat.id,
        message_id=bot_msg.message_id,
        reply_markup=levels_keyboard(call_back.data)
    )


# Level callback
@bot.callback_query_handler(
    func=lambda call_back: "Выбери ступень:" in call_back.message.text
)
def select_program_handler(call_back):
    bot_msg = bot.edit_message_text(
        text="Ищу подходящие образовательные программы\U00002026",
        chat_id=call_back.message.chat.id,
        message_id=call_back.message.message_id
    )
    bot.edit_message_text(
        text="{0}{1}/\n\nВыбери программу:".format(
            call_back.message.text.split("\n\n")[0],
            call_back.data
        ),
        chat_id=call_back.message.chat.id,
        message_id=bot_msg.message_id,
        reply_markup=programs_keyboard(
            alias=call_back.message.text.split("\n\n")[0],
            level_slice=call_back.data
        )
    )


# Program callback
@bot.callback_query_handler(
    func=lambda call_back: "Выбери программу:" in call_back.message.text
)
def select_year_handler(call_back):
    bot_msg = bot.edit_message_text(
        text="Смотрю доступные года\U00002026",
        chat_id=call_back.message.chat.id,
        message_id=call_back.message.message_id
    )
    bot.edit_message_text(
        text="{0}{1}/\n\nВыбери год поступления:".format(
            call_back.message.text.split("\n\n")[0],
            call_back.data
        ),
        chat_id=call_back.message.chat.id,
        message_id=bot_msg.message_id,
        reply_markup=years_keyboard(
            path=call_back.message.text.split("\n\n")[0],
            program_slice=call_back.data
        )
    )


# Year callback
@bot.callback_query_handler(
    func=lambda call_back: "Выбери год поступления:" in call_back.message.text
)
def select_group_handler(call_back):
    bot_msg = bot.edit_message_text(
        text="Получаю список групп\U00002026",
        chat_id=call_back.message.chat.id,
        message_id=call_back.message.message_id
    )
    bot.edit_message_text(
        text="{0}{1}/\n\nВыбери группу:".format(
            call_back.message.text.split("\n\n")[0],
            call_back.data
        ),
        chat_id=call_back.message.chat.id,
        message_id=bot_msg.message_id,
        reply_markup=groups_keyboard(program_id=int(call_back.data))
    )
