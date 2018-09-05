from app.constants import emoji, briefly_info_answer, special_thanks
from tg_bot import bot
from tg_bot.keyboards import special_thanks_keyboard


# Info message
@bot.message_handler(commands=["help"])
@bot.message_handler(
    func=lambda mess: mess.text == emoji["info"],
    content_types=["text"]
)
def help_handler(message):
    bot.send_chat_action(message.chat.id, "typing")

    bot.send_message(
        chat_id=message.chat.id,
        text=briefly_info_answer,
        parse_mode="HTML",
        reply_markup=special_thanks_keyboard(),
        disable_web_page_preview=True
    )


# Thanks callback for info message
@bot.callback_query_handler(
    func=lambda call_back: call_back.data == "Благодарности"
)
def show_full_info(call_back):
    bot.edit_message_text(
        text=special_thanks,
        chat_id=call_back.message.chat.id,
        message_id=call_back.message.message_id,
        parse_mode="HTML",
        disable_web_page_preview=True
    )
    inline_answer = "И тебе :)"
    bot.answer_callback_query(call_back.id, inline_answer, cache_time=1)
