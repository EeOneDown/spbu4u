# -*- coding: utf-8 -*-
import requests
from datetime import datetime, timedelta


yandex_key = "08661824-50dc-4372-8588-37596f156bda"


def get_suburban_timetable(from_station, to_station):
    today_moscow_datetime = datetime.today() + timedelta(hours=-3)
    today_moscow_date = today_moscow_datetime.date()
    url = "https://api.rasp.yandex.net/v3/search/?" + \
          "&from={}".format(from_station) + \
          "&to={}".format(to_station) + \
          "&format=json" + \
          "&lang=ru_RU" + \
          "&apikey={}".format(yandex_key) + \
          "&date={}".format(today_moscow_date)
    json_timetable = requests.get(url).json()
    # TODO parse json
    print(json_timetable)


from constants import all_stations
get_suburban_timetable(all_stations["Санкт-Петербург"],
                       all_stations["Университет"])