from app.constants import webhook_url_path
from unittest.mock import patch
from tg_bot import bot

def test_json_data(client):
    response = client.post(f"/tg{webhook_url_path}", json={"update_id": 1})
    assert response.status_code == 200


@patch("telebot.TeleBot.process_new_updates", lambda *_, **__: None)
@patch("app.new_functions.write_log", lambda *_, **__: None)
def test_message(client):
    response = client.post(
        f"/tg{webhook_url_path}", 
        json={"update_id": 1, "message": {"message_id": 1, "date": 1, "chat": {"id": 1, "type": "private"}}},
    )
    assert response.status_code == 200


@patch("telebot.TeleBot.process_new_updates", lambda *_, **__: None)
@patch("app.new_functions.write_log", lambda *_, **__: None)
def test_callback(client):
    response = client.post(
        f"/tg{webhook_url_path}", 
        json={"update_id": 1, "callback_query": {"id": 1, "from": {"id": 1, "is_bot": False, "first_name": "test"}, "chat_instance": "test"}},
    )
    assert response.status_code == 200


def test_tg_bot_init():
    assert bot.message_handlers
    assert bot.callback_query_handlers
