# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import logging
import re
from datetime import datetime, timedelta, date

import requests
from telebot.apihelper import ApiException
from telebot.types import Message

from app.constants import (
    emoji, subject_short_types, week_day_number, months,
    reg_before_30, reg_only_30, reg_only_31, interval_off_answer, urls,
    yandex_error_answer, yandex_segment_answer, all_stations,
    ask_to_select_types_answer, updated_types_answer
)
from config import Config


def get_term_dates():
    """

    :return: Returns current term's start and end dates
    :rtype: tuple
    """
    today = datetime.today()
    if today.month in range(2, 8):
        start_year = today.year
        end_year = today.year
        start_month = 2
        end_month = 8
    else:
        start_year = today.year - 1 if today.month < 2 else today.year
        end_year = today.year + 1 if today.month > 7 else today.year
        start_month = 8
        end_month = 2

    return (date(year=start_year, month=start_month, day=1),
            date(year=end_year, month=end_month, day=1))


def get_resits_events(events):
    """
        Deletes all resits from events

        :param events: all elements of `DayStudyEvents`
        :type events: list
        :return: list of available events
        :rtype: list
        """
    return [
        event for event in events
        if ("пересдача" in event["Subject"]
            or "консультация" in event["Subject"]
            or "комиссия" in event["Subject"])
    ]


def delete_resits_events(events):
    """
    Deletes all resits from events

    :param events: all elements of `DayStudyEvents`
    :type events: list
    :return: list of available events
    :rtype: list
    """
    return [
        event for event in events
        if ("пересдача" not in event["Subject"]
            or "консультация" not in event["Subject"]
            or "комиссия" not in event["Subject"])
    ]


def delete_cancelled_events(events):
    """
    Function to delete all cancelled events.

    :param events: all elements of `DayStudyEvents`
    :type events: list
    :return: list of available events
    :rtype: list
    """
    return [
        event for event in events
        if not event["IsCancelled"]
    ]


def create_events_blocks(events):
    """
    Function to create list of events grouped by time.

    :param events: all (or available) elements of `DayStudyEvents`
    :type events: list
    :return: list of events grouped by time
    :rtype: list of list
    """
    event_blocks = []
    for i in range(len(events)):
        if i and (
                events[i]["Start"] == events[i - 1]["Start"]
                and events[i]["End"] == events[i - 1]["End"]
        ):
            event_blocks[-1].append(events[i])
        else:
            event_blocks.append([events[i]])
    return event_blocks


def datetime_from_string(dt_string):
    """
    Converts string to datetime object

    :param dt_string: datetime string
    :type dt_string: str
    :return: datetime object
    :rtype: datetime
    """
    return datetime.strptime(
        dt_string.split("+")[0].split("Z")[0], "%Y-%m-%dT%H:%M:%S"
    )


def get_key_by_value(dct, val):
    """
    Gets key by value from input dictionary

    :param dct: input dictionary
    :type dct: dict
    :param val: value in input dictionary (MUST BE)
    :return: suitable key
    """
    for item in dct.items():
        if item[1] == val:
            return item[0]


def get_work_monday(is_next_week=False):
    """
    Returns date of current  or next monday for Mon-Sat, nex monday for Sunday

    :param is_next_week: (Optional) is for next week
    :type is_next_week: bool
    :return: monday date
    :rtype: date
    """
    today = date.today()
    delta = today.weekday() if today.weekday() != 6 else -1
    if is_next_week:
        delta -= 7
    return today - timedelta(days=delta)


def get_date_by_weekday_title(title, is_next_week=False):
    """
    Returns date for current or next week by day short title

    :param title: short weekday title (Russian)
    :type title: str
    :param is_next_week: (Optional) is for next week
    :type is_next_week: bool
    :return: date
    :rtype: date
    """
    work_monday = get_work_monday(is_next_week=is_next_week)
    delta = week_day_number[title] - 1
    return work_monday + timedelta(days=delta)


def datetime_to_string(date_value):
    """
    Converts date object to string

    :param date_value: date object
    :type date_value: date
    :return: date string
    :rtype: str
    """
    return "{day} {month_title} {year}".format(
        day=date_value.day,
        month_title=get_key_by_value(months, date_value.month),
        year=date_value.year)


def text_to_date(text):
    """
    Checks if the text is a date then converts it to a date object or
    returns False

    :param text: some text
    :type text: str
    :return: date object or False
    :rtype: date or False
    """
    regs = [reg_before_30, reg_only_30, reg_only_31]
    for reg in regs:
        res = re.search(reg, text)
        if res:
            groups = res.groups()
            day = int(groups[0])
            month = int(groups[3]) if groups[3] else date.today().month
            year = int(groups[5]) if groups[5] else date.today().year
            return date(day=day, month=month, year=year)
    return False


def text_to_interval(text):
    """
    Checks if text is a dates interval and converts it to two date objects or
    returns False

    :param text: some text
    :type text: str
    :return: two date objects
    :rtype: tuple of date
    """
    dates = text.split("-")
    if len(dates) == 2:
        from_date = text_to_date(dates[0].strip())
        to_date = text_to_date(dates[1].strip())
        if from_date and to_date and from_date < to_date:
            return from_date, to_date
    return False


def create_interval_off_answer(from_date, to_date):
    """
    Creates interval off answer for dates

    :param from_date: first date
    :type from_date: date
    :param to_date: second date
    :type to_date: date
    :return: interval off answer
    :rtype: str
    """
    return interval_off_answer.format(
        emoji["sleep"],
        datetime_to_string(from_date),
        datetime_to_string(to_date)
    )


def is_correct_educator_name(text):
    """
    Checks if the text is correct

    :param text: input text
    :type text: str
    :return: True or False
    :rtype: bool
    """
    return text.replace(".", "").replace("-", "").replace(" ", "").isalnum()


def parse_event_time(event):
    return "{0} {1:0>2}:{2:0>2}{3}{4:0>2}:{5:0>2}".format(
        emoji["clock"],
        datetime_from_string(event["Start"]).time().hour,
        datetime_from_string(event["Start"]).time().minute,
        emoji["en_dash"],
        datetime_from_string(event["End"]).time().hour,
        datetime_from_string(event["End"]).time().minute
    )


def parse_event_subject(event):
    answer = ""
    subject_name = ", ".join(event["Subject"].split(", ")[:-1])

    subject_type = event["Subject"].split(", ")[-1]
    # оставляем только перыве два слова
    stripped_subject_type = " ".join(subject_type.split()[:2])
    if stripped_subject_type in subject_short_types.keys():
        answer += subject_short_types[stripped_subject_type] \
                  + " " + emoji["en_dash"] + " "
    else:
        answer += subject_type.upper() \
                  + " " + emoji["en_dash"] + " "
    answer += subject_name

    return answer


def parse_event_location(location, full_place=True, have_chosen_educator=False,
                         chosen_educator=None):
    answer = ""

    if location["IsEmpty"]:
        return answer

    if have_chosen_educator and not chosen_educator.issuperset(
            {edu["Item2"].split(", ")[0] for edu in location["EducatorIds"]}
    ):
        return answer

    if full_place:
        location_name = location["DisplayName"].strip(", ").strip()
    else:
        location_name = location["DisplayName"].split(", ")[-1].strip()

    answer += location_name

    if location["HasEducators"]:
        educators = [educator["Item2"].split(", ")[0] for educator in
                     location["EducatorIds"]]

        if len(educators):
            answer += " <i>({0})</i>".format("; ".join(educators))

    return answer


def parse_event_sub_loc_edu(event, full_place):
    answer = "<b>" + parse_event_subject(event) + "</b>\n"

    for location in event["EventLocations"]:
        loc_answer = parse_event_location(location, full_place)
        answer += loc_answer

        if loc_answer:
            if event["LocationsWereChanged"] or \
                    event["EducatorsWereReassigned"]:
                answer += " " + emoji["warning"]
            answer += "\n"

    answer += "\n"
    return answer


def create_schedule_answer(event, full_place):
    answer = ""

    if event["IsAssigned"]:
        answer += emoji["new"] + " "
    answer += parse_event_time(event)
    if event["TimeWasChanged"]:
        answer += " " + emoji["warning"]

    answer += "\n" + parse_event_sub_loc_edu(event, full_place)
    return answer


def create_master_schedule_answer(day_info):
    answer = "{0} {1}\n\n".format(emoji["calendar"], day_info["DayString"])

    for event in day_info["DayStudyEvents"]:
        answer += "{0} {1} <i>({2})</i>\n".format(
            emoji["clock"], event["TimeIntervalString"],
            "; ".join(event["Dates"])
        )
        answer += "<b>"
        subject_type = event["Subject"].split(", ")[-1]
        stripped_subject_type = " ".join(subject_type.split()[:2])
        if stripped_subject_type in subject_short_types.keys():
            answer += subject_short_types[stripped_subject_type] \
                      + " " + emoji["en_dash"] + " "
        else:
            answer += subject_type.upper() \
                  + " " + emoji["en_dash"] + " "
        answer += ", ".join(
            event["Subject"].split(", ")[:-1]
        ) + "</b>\n"

        for location in event["EventLocations"]:
            location_name = location["DisplayName"]
            answer += location_name + " <i>({0})</i>\n".format(
                "; ".join(name["Item1"] for name in
                          event["ContingentUnitNames"])
            )
        answer += "\n"
    return answer


def get_hours_minutes_by_seconds(seconds):
    """
    Gets hours and minutes by input seconds

    :param seconds: seconds
    :type seconds: int
    :return: hours and minutes
    :rtype: tuple
    """
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return h, m


def get_yandex_raw_data(from_station, to_station, for_date):
    """
    Gets yandex raw data and status code

    :param from_station: `from` station yandex code
    :type from_station: str
    :param to_station: `to` station yandex code
    :type to_station: str
    :param for_date: date for which data should be received
    :type for_date: date
    :return: status code and raw json data
    :rtype: tuple
    """
    params = {
        "from": from_station,
        "to": to_station,
        "apikey": Config.YANDEX_API_KEY,
        "date": for_date,
        "format": "json",
        "lang": "ru_RU",
        "transport_types": "suburban"
    }
    url = urls["ya_search"]
    req = requests.get(url, params=params)
    return req.status_code, req.json()


def parse_yandex_segment(segment, current_datetime=datetime.now()):
    """
    Parses segments data to yandex_segment_answer

    :param segment: segment's json data from api.rasp.yandex's search method
    :type segment: dict
    :param current_datetime: current datetime
    :type current_datetime: datetime
    :return: parsed yandex segment answer
    :rtype: str
    """
    departure_datetime = datetime_from_string(segment["departure"])
    arrival_datetime = datetime_from_string(segment["arrival"])

    hours, minutes = get_hours_minutes_by_seconds(
        (departure_datetime - current_datetime).seconds
    )

    if hours:
        time_mark = emoji["blue_diamond"]
        lef_time = "{0} ч {1} мин".format(hours, minutes)
    elif 15.0 < minutes < 60.0:
        time_mark = emoji["orange_diamond"]
        lef_time = "{0} мин".format(minutes)
    else:
        time_mark = emoji["runner"]
        lef_time = "{0} мин".format(minutes)

    if segment["thread"]["express_type"]:
        train_mark = emoji["express"]
    else:
        train_mark = emoji["train"]

    if segment["tickets_info"]:
        price = str(
            segment["tickets_info"]["places"][0]["price"]["whole"]
        )
        if segment["tickets_info"]["places"][0]["price"]["cents"]:
            price += ",{0}".format(
                segment["tickets_info"]["places"][0]["price"]["cents"]
            )
    else:
        price = "?"

    return yandex_segment_answer.format(
        time_mark=time_mark,
        lef_time=lef_time,
        train_mark=train_mark,
        dep_time=departure_datetime.time().strftime("%H:%M"),
        arr_time=arrival_datetime.time().strftime("%H:%M"),
        price=price,
        ruble_sign=emoji["ruble_sign"]
    )


def create_suburbans_answer(from_code, to_code, for_date, limit=3):
    """
    Creates yandex suburbans answer for date by stations codes

    :param from_code: `from` yandex station code
    :type from_code: str
    :param to_code: `to` yandex station code
    :type to_code: str
    :param for_date: date for which data should be received
    :type for_date: date
    :param limit: limit of segments in answer
    :type limit: int
    :return: tuple with `answer`, `is_tomorrow` and `is_error` data
    :rtype: tuple
    """
    code, data = get_yandex_raw_data(from_code, to_code, for_date)

    if code != 200:
        return yandex_error_answer, False, True

    from_title = data["search"]["from"]["title"]
    to_title = data["search"]["to"]["title"]

    answer = ""

    for segment in data["segments"]:
        if len(answer.split("\n\n")) > limit:
            break

        if datetime_from_string(segment["departure"]) >= datetime.now():
            answer += parse_yandex_segment(segment)

    if answer:
        answer = "<b>{0}</b> => <b>{1}</b>\n\n".format(
            from_title, to_title
        ) + answer
        is_tomorrow = False
    else:
        for_date = date.today() + timedelta(days=1)
        answer += create_suburbans_answer(
            from_code, to_code, for_date, limit=5
        )[0]
        is_tomorrow = True

    return answer, is_tomorrow, False


def get_station_title_from_text(text, is_end=False, is_full=False):
    """
    Gets start/end station title from bot's answer text

    :param text: bot's answer text
    :type text: str
    :param is_end: is get end station title
    :type is_end: bool
    :param is_full: if the text is full answer created by
    `create_suburbans_answer` function
    :type is_full: bool
    :return: station title
    :rtype: str
    """
    if is_full:
        return text.split("\n")[0].split(" => ")[int(is_end)]
    else:
        return text.split("\n")[int(is_end)].split(": ")[-1]


def get_station_code_from_text(text, is_end=False, is_full=False):
    """
    Gets start/end station yandex code from bot's answer text

    :param text: bot's answer text
    :type text: str
    :param is_end: is get end station title
    :type is_end: bool
    :param is_full: if the text is full answer created by
    `create_suburbans_answer` function
    :type is_full: bool
    :return: yandex station code
    :rtype: str
    """
    return all_stations[get_station_title_from_text(text, is_end, is_full)]


def add_end_station(text, end_title):
    """
    Changes answer text by adding end station title

    :param text: bot's answer text
    :type text: str
    :param end_title: end station title
    :type end_title: str
    :return: answer text
    :type: str
    """
    return "Начальная: <b>{0}</b>\nКончная: <b>{1}</b>\nВыбери день:".format(
        get_station_title_from_text(text), end_title
    )


def update_suburbans_answer(text, show_more=False, for_tomorrow=False):
    """
    Updates suburbans answer created by `create_suburbans_answer` function

    :param text: bot's answer text
    :type text: str
    :param show_more: is need to show future trails
    :type show_more: bool
    :param for_tomorrow: is need to show trails for tomorrow
    :type for_tomorrow: bool
    :return:
    """
    return create_suburbans_answer(
        from_code=get_station_code_from_text(text, is_full=True),
        to_code=get_station_code_from_text(text, is_full=True, is_end=True),
        for_date=date.today() + timedelta(days=int(for_tomorrow)),
        limit=100 if show_more else (7 if for_tomorrow else 3)
    )


def bot_waiting_for(msg, waiting_bot_text):
    """
    Checks if the message is a reply to ask for input educator

    :param msg: bot's message
    :type msg: Message
    :param waiting_bot_text: text which bot sent
    :type waiting_bot_text: str
    :return: True or False
    :rtype: bool
    """
    if msg.reply_to_message:
        if msg.reply_to_message.from_user.username == Config.BOT_NAME:
            if msg.reply_to_message.text == waiting_bot_text:
                return True
    return False


def get_block_data_from_block_answer(text):
    """
    Gets count of blocks, current block number and schedule's date from
    created block answer by `User.get_block_answer()`

    :param text: block answer
    :type text: str
    :return: count of blocks, current block number and schedule's date
    :rtype: tuple
    """
    rows = text.split("\n\n")

    current_block_num, blocks_count = list(map(int, rows[0].split()[::2]))
    for_date = get_date_by_weekday_title(rows[1].split()[-1][1:-1])
    return blocks_count, current_block_num, for_date


def get_event_data_from_block_answer(text, idx):
    """
    Gets event's day short title, time, type, name and educators from
    created block answer by `User.get_block_answer()`

    :param text: block answer
    :type text: str
    :param idx: event index
    :type idx: int
    :return: event's day short title, time, type, name and educators
    :rtype: tuple
    """
    rows = text.split("\n\n")

    emoji_time_day = rows[1].split()
    event_time = emoji_time_day[1]
    event_day_short = emoji_time_day[-1][1:-1]

    event_data = rows[idx + 2].split("\n")
    event_type_name = event_data[0].split(" " + emoji["en_dash"] + " ")
    event_name = (" " + emoji["en_dash"] + " ").join(event_type_name[1:])
    event_type = event_type_name[0].strip(
        str(idx + 1) + ". "
    ).replace(
        emoji["cross_mark"] + " ", ""
    )
    event_educators = "; ".join(
        [place_edu.split("(")[-1].split(")")[0]
         for place_edu in event_data[1:]]
    )
    return event_day_short, event_time, event_type, event_name, event_educators


def update_types_answer(text, new_type):
    """
    Updates text by adding/removing type

    :param text: bot's ald text
    :type text: str
    :param new_type: selected short type
    :type new_type: str
    :return: updated answer
    :rtype: str
    """
    lesson_data = text.split("\n\n")[1].split("\n")

    if lesson_data[-1] == "Типы: Все":
        types = [new_type]
    else:
        types = lesson_data[-1][6:].split("; ")
        if new_type in types:
            types.remove(new_type)
        else:
            types.append(new_type)

    lesson_data[-1] = "Типы: {0}".format("; ".join(types) if types else "Все")

    return "\n\n".join([
        updated_types_answer,
        "\n".join(lesson_data),
        ask_to_select_types_answer
    ])


def get_lesson_data(data, hide_type):
    """
    Creates dict with lesson data for `Lesson.__init__()`

    :param data: `selected_lesson_info_answer` with data
    :type data: str
    :param hide_type: `ЛЛЛ`, `ЛКК`, etc
    :type hide_type: str
    :return: dict with lesson data
    :rtype: dict
    """
    return dict(
        name=data[2][10:],
        types=[get_key_by_value(dct=subject_short_types, val=t) for t in
               data[-1][6:].split("; ")] if "Все" not in data[-1] else None,
        days=[data[0][6:]] if hide_type[0] == "К" else None,
        times=[data[1][7:]] if hide_type[1] == "К" else None,
        educators=data[3][15:].split("; ") if hide_type[2] == "К" else None,
        locations=None
    )


def send_long_message(bot, text, user_id, split="\n\n"):
    try:
        bot.send_message(user_id, text, parse_mode="HTML")
    except ApiException as ApiExcept:
        json_err = json.loads(ApiExcept.result.text)
        if json_err["description"] == "Bad Request: message is too long":
            event_count = len(text.split(split))
            first_part = split.join(text.split(split)[:event_count // 2])
            second_part = split.join(text.split(split)[event_count // 2:])
            send_long_message(bot, first_part, user_id, split)
            send_long_message(bot, second_part, user_id, split)


def write_log(update, work_time, was_error=False):
    if update.message is not None:
        chat_id = update.message.chat.id
        user_text = update.message.text
    elif update.callback_query is not None:
        chat_id = update.callback_query.message.chat.id
        user_text = update.callback_query.data
    else:
        chat_id = "ERROR"
        user_text = str(update)
    log = "CHAT: {0} ===== TEXT: {1} ===== TIME: {2}".format(
        chat_id, user_text, work_time)
    if was_error:
        log += "\t\t\tERROR"
    logging.info(log)
