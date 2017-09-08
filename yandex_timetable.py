# -*- coding: utf-8 -*-
import math
import requests
from datetime import datetime, timedelta, time
from constants import emoji, yandex_key


def get_yandex_timetable_data(from_station, to_station, date, limit=3):
    from flask_app import server_timedelta
    url = 'https://api.rasp.yandex.net/v3.0/search/?' \
          'from={}' \
          '&to={}' \
          '&format=json' \
          '&lang=ru_RU' \
          '&apikey={}' \
          '&date={}' \
          '&transport_types=suburban'.format(from_station, to_station,
                                             yandex_key, date)
    data = requests.get(url).json()

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
        total_minutes = math.ceil(time_left.total_seconds() / 60)

        if total_minutes >= 59:
            hours = total_minutes // 60
            segment_answer = emoji["blue_diamond"] + segment_answer
            segment_answer += "{} ч ".format(hours)
            total_minutes %= 60
        elif 15.0 < total_minutes < 60:
            segment_answer = emoji["orange_diamond"] + segment_answer
        else:
            segment_answer = emoji["runner"] + segment_answer
        segment_answer += "{} мин\n".format(total_minutes)
        segment_answer += "Отправление в <b>{}</b> ({})\n\n".format(
            departure_datetime.time().strftime("%H:%M"),
            arrival_datetime.time().strftime("%H:%M"))

        answer += segment_answer

    if answer != "":
        answer = "<b>{}</b> => <b>{}</b>\n\n".format(from_title, to_title) + \
                 answer
        is_tomorrow = False
    else:
        date = datetime.combine((datetime.today() + timedelta(days=1)).date(),
                                time())
        answer += get_yandex_timetable_data(from_station, to_station, date,
                                            limit=5)["answer"]
        is_tomorrow = True
    return {"answer": answer, "is_tomorrow": is_tomorrow}
