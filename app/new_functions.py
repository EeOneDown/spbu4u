# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import re
from datetime import datetime, timedelta, date

from telebot.apihelper import ApiException

from app.constants import (
    emoji, subject_short_type, week_day_number, week_day_titles, months,
    reg_before_30, reg_only_30, reg_only_31, interval_off_answer
)


def delete_cancelled_events(events):
    """
    Function to delete all cancelled events.
    :param events: all elements of `DayStudyEvents`
    :type events: list
    :return: list of available events
    :rtype: list
    """
    available_day_events = [
        event for event in events
        if not event["IsCancelled"]
    ]
    return available_day_events


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
    return datetime.strptime(dt_string, "%Y-%m-%dT%H:%M:%S")


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
    day = datetime.today().date()
    delta = day.weekday() if day.weekday() != 6 else -1
    if is_next_week:
        delta += timedelta(days=7)
    return day - timedelta(days=delta)


def get_date_by_weekday_title(title, is_next_week=False):
    """
    Returns date for current or next week by day title
    :param title: weekday title (Russian)
    :type title: str
    :param is_next_week: (Optional) is for next week
    :type is_next_week: bool
    :return: date
    :rtype: date
    """
    work_monday = get_work_monday(is_next_week=is_next_week)
    delta = week_day_number[week_day_titles[title]]
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
    stripped_subject_type = " ".join(subject_type.split()[:2])
    if stripped_subject_type in subject_short_type.keys():
        answer += subject_short_type[stripped_subject_type] + " - "
    else:
        answer += subject_type.upper() + " - "
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


def create_schedule_answer(event, full_place):
    answer = ""

    if event["IsAssigned"]:
        answer += emoji["new"] + " "
    answer += parse_event_time(event)
    if event["TimeWasChanged"]:
        answer += " " + emoji["warning"]

    answer += "\n<b>" + parse_event_subject(event) + "</b>\n"

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
