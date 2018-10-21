from tg_bot import bot
from app import create_app
from app.models import Group, Educator
import requests


def watcher():
    for q in (Educator, Group):
        for obj in q.query.all():
            if obj.update_hash(
                    requests.get("https://timetable.spbu.ru/api/v1/educators/{0}/events".format(obj.id)).content
            ):
                for user in obj.current_member:
                    bot.send_message(
                        chat_id=user.tg_id,
                        text="В расписании появились изменения! Заходи и проверь текущую неделю."
                    )


if __name__ == '__main__':
    with create_app().app_context():
        watcher()
