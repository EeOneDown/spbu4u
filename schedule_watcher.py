from tg_bot import bot
from app import create_app, db
from app.models import Group, Educator
from app.constants import schedule_changed_answer
import requests


def watcher():
    for q in (Educator, Group):
        for obj in q.query.filter(q.id != 0).all():
            if obj.update_hash(requests.get(obj.get_tt_link(is_api=True)).content):
                for user in obj.current_members.filter_by(is_subscribed=True):
                    bot.send_message(
                        chat_id=user.tg_id,
                        text=schedule_changed_answer
                    )
    db.session.commit()


if __name__ == '__main__':
    with create_app().app_context():
        watcher()
