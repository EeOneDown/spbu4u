import json
from app.constants import webhook_url_path


def test_json_data(client):
    response = client.post(f"/tg{webhook_url_path}", json={"update_id": 1})
    assert response.status_code == 200
