# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import date, timedelta

from app import new_functions as nf
from app.constants import weekend_answer
from app.models import User
from tg_bot import bot


def schedule_sender():
    send_cnt, err_cnt = 0, 0

    for user in User.query.filter_by(is_subscribed=True).all():
        answer = user.create_answer_for_date(
            for_date=date.today() + timedelta(days=1)
        )
        if answer == weekend_answer:
            continue

        try:
            answer = "Расписание на завтра:\n\n" + answer
            nf.send_long_message(bot, answer, user.tg_id)
            send_cnt += 1
        except Exception as err:
            print("---------------ERROR START---------------")
            print(err)
            print("USER ID:", user.id)
            print("----------------ERROR END----------------")
            err_cnt += 1
    return send_cnt, err_cnt


if __name__ == '__main__':
    print("OK: {0}; ERRORS: {1}".format(*schedule_sender()))
