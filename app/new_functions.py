# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime

from app.constants import emoji, subject_short_type


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
    return datetime.strptime(dt_string, "%Y-%m-%dT%H:%M:%S")


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
