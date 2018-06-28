# -*- coding: utf-8 -*-
from __future__ import unicode_literals


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
