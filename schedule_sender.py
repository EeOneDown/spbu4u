# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime, timedelta

from bot import bot
from app.constants import server_timedelta
from bot.functions import get_json_day_data, create_schedule_answer, \
    is_full_place, send_long_message, get_connection


def schedule_sender():
    sql_con = get_connection()
    cursor = sql_con.cursor()
    cursor.execute("""SELECT id
                      FROM user_data
                      WHERE sending = 1""")
    data = cursor.fetchall()
    cursor.close()
    sql_con.close()

    send_cnt = 0
    err_cnt = 0

    tomorrow_moscow_datetime = \
        datetime.today() + timedelta(days=1) + server_timedelta
    tomorrow_moscow_date = tomorrow_moscow_datetime.date()

    for user_data in data:
        user_id = user_data[0]
        json_day = get_json_day_data(user_id, tomorrow_moscow_date)
        full_place = is_full_place(user_id)
        answer = create_schedule_answer(json_day, full_place, user_id)

        if "Выходной" in answer:
            continue

        try:
            answer = "Расписание на завтра:\n\n" + answer
            send_long_message(bot, answer, user_id)
            send_cnt += 1
        except Exception as err:
            print(err)
            print(user_id)
            err_cnt += 1
            continue

    return send_cnt, err_cnt


if __name__ == '__main__':
    send_cnt, err_cnt = schedule_sender()
    print(datetime.today().time(),
          "Sends: {0}; Errs: {1}".format(send_cnt, err_cnt))
