# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import timedelta

import spbu

from app import db, new_functions as f
from app.constants import (
    week_off_answer, weekend_answer, emoji, max_answers_count,
    interval_exceeded_answer
)
import app.new_functions as nf

users_groups = db.Table(
    "users_groups",
    db.Column("group_id", db.Integer, db.ForeignKey("groups.id"),
              primary_key=True),
    db.Column("user_id", db.Integer, db.ForeignKey("users.id"),
              primary_key=True)
)


users_added_lesson = db.Table(
    "users_added_lesson",
    db.Column("lesson", db.Integer, db.ForeignKey("lessons.id"),
              primary_key=True),
    db.Column("user_id", db.Integer, db.ForeignKey("users.id"),
              primary_key=True)
)


users_hidden_lessons = db.Table(
    "users_hidden_lessons",
    db.Column("lesson", db.Integer, db.ForeignKey("lessons.id"),
              primary_key=True),
    db.Column("user_id", db.Integer, db.ForeignKey("users.id"),
              primary_key=True)
)


users_chosen_educators = db.Table(
    "users_chosen_educators",
    db.Column("lesson", db.Integer, db.ForeignKey("lessons.id"),
              primary_key=True),
    db.Column("user_id", db.Integer, db.ForeignKey("users.id"),
              primary_key=True)
)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tg_id = db.Column(db.Integer, index=True, unique=True, nullable=False)
    is_educator = db.Column(db.Boolean, default=False, nullable=False)
    is_full_place = db.Column(db.Boolean, default=True, nullable=False)
    is_subscribed = db.Column(db.Boolean, default=False, nullable=False)
    home_station_code = db.Column(db.String(10), default="c2", nullable=False)
    univer_station_code = db.Column(db.String(10), default="s9603770",
                                    nullable=False)
    current_group_id = db.Column(db.Integer, db.ForeignKey("groups.id"))
    educator_id = db.Column(db.Integer, nullable=True)
    groups = db.relationship("Group", secondary=users_groups,
                             back_populates="members", lazy="dynamic")
    added_lessons = db.relationship("Lesson", secondary=users_added_lesson,
                                    lazy="dynamic")
    hidden_lessons = db.relationship("Lesson", secondary=users_hidden_lessons,
                                     lazy="dynamic")
    chosen_educators = db.relationship("Lesson",
                                       secondary=users_chosen_educators,
                                       lazy="dynamic")
    _current_group = db.relationship("Group")

    def _parse_event(self, event):
        # TODO delete hidden lessons
        return f.create_schedule_answer(event, self.is_full_place)

    def _parse_day_events(self, events):
        """
        This method parses the events data from SPBU API
        :param events: an element of `DayStudyEvents`
        :type events: dict
        :return: html safe string
        :rtype: str
        """
        answer = "{0} {1}\n\n".format(
            emoji["calendar"], events["DayString"].capitalize()
        )

        events = f.delete_cancelled_events(events["DayStudyEvents"])
        for event in events:
            answer += self._parse_event(event)
        return answer

    def create_answer_for_date(self, date):
        """
        This method gets the schedule for date and parses it
        :param date: date for schedule
        :type date: datetime.date
        :return: html safe string
        :rtype: str
        """
        if self.is_educator:
            """
            In future:
            json_day_events = spbu.get_educator_events(self.current_group_id
                from_date=date, to_date=date + timedelta(days=1)  
            )["Days"]
            """
            json_day_events = []
        else:
            json_day_events = self._current_group.get_events(
                from_date=date, to_date=date + timedelta(days=1)
            )["Days"]

        if len(json_day_events):
            answer = self._parse_day_events(json_day_events[0])
        else:
            answer = weekend_answer

        return answer

    def create_answers_for_interval(self, from_date, to_date=None):
        """
        Method to create answers for interval. if no `to_date` will return for
        7 days
        :param from_date: the datetime the events start from
        :type from_date: datetime.date
        :param to_date: (Optional) the datetime the events ends
        :type to_date: datetime.date
        :return: list of schedule answers
        :rtype: list of str
        """
        answers = []

        if not to_date:
            to_date = from_date + timedelta(days=7)

        if self.is_educator:
            """
            In future:
            json_day_events = spbu.get_educator_events(self.current_group_id
                from_date=from_date, to_date=to_date  
            )["Days"]
            """
            json_day_events = []
        else:
            json_day_events = self._current_group.get_events(
                from_date=from_date, to_date=to_date
            )["Days"]

        for event in json_day_events:
            answers.append(self._parse_day_events(event))

        if len(answers) > max_answers_count:
            answers = [interval_exceeded_answer]
        elif not len(answers):
            if from_date.weekday() == 1:
                answers = [week_off_answer]
            else:
                answers = [nf.create_interval_off_answer(from_date, to_date)]
        return answers


class Group(db.Model):
    __tablename__ = "groups"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    members = db.relationship("User", secondary=users_groups,
                              back_populates="groups", lazy="dynamic")

    def get_events(self, from_date=None, to_date=None, lessons_type=None):
        return spbu.get_group_events(self.id, from_date, to_date, lessons_type)


class Lesson(db.Model):
    __tablename__ = "lessons"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128))
    types = db.Column(db.JSON)
    days = db.Column(db.JSON)
    times = db.Column(db.JSON)
    educators = db.Column(db.JSON)
    places = db.Column(db.JSON)

    @staticmethod
    def add_or_get(name, types, days, times, educators, places):
        """
        Так как из полей типа JSON сделать уникальный индекс нельзя, то
        приходится проверять наличие элемента в базе перед добавлением.
        Будет возвращен либо новый объект, либо уже существующий.
        """
        lesson = Lesson.query.filter_by(name=name, types=types, days=days,
                                        times=times, educators=educators,
                                        places=places).one_or_none()
        if not lesson:
            lesson = Lesson(name=name, types=types, days=days, times=times,
                            educators=educators, places=places)
        return lesson
