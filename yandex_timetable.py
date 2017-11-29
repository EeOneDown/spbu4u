# -*- coding: utf-8 -*-
from datetime import datetime, timedelta, time
from math import ceil

import requests

from bots_constants import yandex_key
from constants import emoji


def get_yandex_timetable_data(from_station, to_station, date, limit=3):
    from flask_app import server_timedelta
    url = "https://api.rasp.yandex.net/v3.0/search/?" \
          "from={0}" \
          "&to={1}" \
          "&format=json" \
          "&lang=ru_RU" \
          "&apikey={2}" \
          "&date={3}" \
          "&transport_types=suburban".format(from_station, to_station,
                                             yandex_key, date)
    req = requests.get(url)
    code, data = req.status_code, req.json()

    if code != 200:
        return {"answer": "Ошибка в обращении к серверу Яндекса. "
                          "Попробуйте повторить позже.",
                "is_tomorrow": False, "is_OK": False}

    from_title = data["search"]["from"]["title"]
    to_title = data["search"]["to"]["title"]

    answer = ""
    server_now_date = datetime.today() + server_timedelta

    for segment in data["segments"]:
        if len(answer.split("\n\n")) > limit:
            break

        segment_answer = " <i>Через</i> "

        departure_datetime = datetime.strptime(
            segment["departure"].split("+")[0], "%Y-%m-%dT%H:%M:%S")
        arrival_datetime = datetime.strptime(
            segment["arrival"].split("+")[0], "%Y-%m-%dT%H:%M:%S")
        if date > departure_datetime:
            continue

        time_left = departure_datetime - server_now_date
        total_minutes = ceil(time_left.total_seconds() / 60)

        if total_minutes >= 60:
            hours = total_minutes // 60
            segment_answer = emoji["blue_diamond"] + segment_answer
            segment_answer += "{0} ч ".format(hours)
            total_minutes %= 60
        elif 15.0 < total_minutes < 60:
            segment_answer = emoji["orange_diamond"] + segment_answer
        else:
            segment_answer = emoji["runner"] + segment_answer
        segment_answer += "{0} мин\n".format(total_minutes)
        segment_answer += "Отправление в <b>{0}</b> ({1})\n\n".format(
            departure_datetime.time().strftime("%H:%M"),
            arrival_datetime.time().strftime("%H:%M"))

        answer += segment_answer

    if answer != "":
        answer = "<b>{0}</b> => <b>{1}</b>\n\n".format(from_title, to_title) + \
                 answer
        is_tomorrow = False
    else:
        date = datetime.combine((datetime.today() + timedelta(days=1)).date(),
                                time())
        answer += get_yandex_timetable_data(from_station, to_station, date,
                                            limit=5)["answer"]
        is_tomorrow = True
    return {"answer": answer, "is_tomorrow": is_tomorrow, "is_OK": True}
