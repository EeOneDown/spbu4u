# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import timedelta, date

import spbu

import app.new_functions as nf
from app import db, new_functions as f
from app.constants import (
    week_off_answer, weekend_answer, emoji, max_answers_count,
    interval_exceeded_answer, changed_to_full_answer, changed_to_class_answer,
    week_day_number
)


users_groups_templates = db.Table(
    "users_groups",
    db.Column("group_id", db.Integer, db.ForeignKey("groups.id"),
              primary_key=True),
    db.Column("user_id", db.Integer, db.ForeignKey("users.id"),
              primary_key=True)
)

users_educators_templates = db.Table(
    "users_educators",
    db.Column("educator_id", db.Integer, db.ForeignKey("educators.id"),
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
    current_educator_id = db.Column(db.Integer, db.ForeignKey("educators.id"))
    groups = db.relationship("Group", secondary=users_groups_templates,
                             back_populates="members", lazy="dynamic")
    educators = db.relationship("Educator",
                                secondary=users_educators_templates,
                                back_populates="members", lazy="dynamic")
    added_lessons = db.relationship("Lesson", secondary=users_added_lesson,
                                    lazy="dynamic")
    hidden_lessons = db.relationship("Lesson", secondary=users_hidden_lessons,
                                     lazy="dynamic")
    chosen_educators = db.relationship("Lesson",
                                       secondary=users_chosen_educators,
                                       lazy="dynamic")
    _current_group = db.relationship("Group")
    _current_educator = db.relationship("Educator")

    def _get_events(self, from_date, to_date):
        """
        Gets user's suitable events data

        :param from_date: the date the events start from
        :type from_date: date
        :param to_date: (Optional) the date the events ends
        :type to_date: date
        :return: list of events data (json)
        :rtype: list
        """
        if self.is_educator:
            return self._current_educator.get_events(
                from_date=from_date, to_date=to_date
            )["Days"]
        else:
            return self._current_group.get_events(
                from_date=from_date, to_date=to_date
            )["Days"]

    def _parse_event(self, event):
        lesson = Lesson().de_json(event)
        suitable_skips = self.hidden_lessons.filter_by(name=lesson.name).all()
        for skip in suitable_skips:
            if lesson in skip:
                return ""
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
        if len(answer.split("\n\n")) == 2:
            answer += weekend_answer
        return answer

    def create_answer_for_date(self, for_date):
        """
        This method gets the schedule for date and parses it

        :param for_date: date for schedule
        :type for_date: date
        :return: html safe string
        :rtype: str
        """
        events = self._get_events(
            from_date=for_date,
            to_date=for_date + timedelta(days=1)
        )
        if len(events):
            answer = self._parse_day_events(events[0])
        else:
            answer = weekend_answer

        return answer

    def create_answers_for_interval(self, from_date, to_date=None):
        """
        Method to create answers for interval. if no `to_date` will return for
        7 days

        :param from_date: the date the events start from
        :type from_date: date
        :param to_date: (Optional) the date the events ends
        :type to_date: date
        :return: list of schedule answers
        :rtype: list of str
        """
        answers = []

        if not to_date:
            to_date = from_date + timedelta(days=7)

        events = self._get_events(
            from_date=from_date,
            to_date=to_date
        )
        for event in events:
            answers.append(self._parse_day_events(event))

        if len(answers) > max_answers_count:
            answers = [interval_exceeded_answer]
        elif not len(answers):
            if from_date.isoweekday() == 1 and (to_date - from_date).days == 7:
                answers = [week_off_answer]
            else:
                answers = [nf.create_interval_off_answer(from_date, to_date)]
        return answers

    def get_block_answer(self, for_date, block_num=1):
        """
        Creates block answer number `block_num` for current `weekday_short` date

        :param for_date: date for schedule
        :type for_date: date
        :param block_num: (Optional) wanted block's human number (NOT AN INDEX)
        :type block_num: int
        :return:
        :rtype: str
        """
        events = self._get_events(
            from_date=for_date,
            to_date=for_date + timedelta(days=1)
        )[0]
        blocks = nf.create_events_blocks(events["DayStudyEvents"])
        block = blocks[block_num - 1]
        answer = "<b>{0} из {1}</b> <i>({2})</i>\n\n".format(
            block_num, len(blocks),
            nf.get_key_by_value(week_day_number, for_date.isoweekday())
        )
        for event in block:
            sub_answer = f.create_schedule_answer(event, self.is_full_place)

            lesson = Lesson().de_json(event)
            for skip in self.hidden_lessons.filter_by(name=lesson.name).all():
                if lesson in skip:
                    sub_answer = emoji["cross_mark"] + " " + sub_answer
                    break
            answer += sub_answer
        return answer

    def get_current_status_title(self):
        """
        Gets title of current status (group/educator)

        :return: suitable title
        :rtype: str
        """
        if self.is_educator:
            return self._current_educator.title
        else:
            return self._current_group.title

    def get_sav_del_button_text(self):
        """
        Gets `Save` or `Delete` text for templates's button

        :return: text
        :rtype: str
        """
        if self.is_educator and self._current_educator in self.educators \
                or not self.is_educator and self._current_group in self.groups:
            return "Удалить"
        else:
            return "Сохранить"

    def save_current_status_into_templates(self):
        """
        Saves current group/educator into templates

        :return: None
        """
        if self.is_educator:
            self.educators.append(self._current_educator)
        else:
            self.groups.append(self._current_group)

    def delete_current_status_from_templates(self):
        """
        Deletes current group/educator from templates

        :return: None
        """
        if self.is_educator:
            self.educators.remove(self._current_educator)
        else:
            self.groups.remove(self._current_group)

    def get_place_edited_answer(self):
        """
        Gets place edited answer for place type

        :return: suitable answer
        :rtype: str
        """
        if self.is_full_place:
            return changed_to_full_answer
        else:
            return changed_to_class_answer

    def clear_all(self):
        """
        Deletes all personalization

        :return: None
        """
        self.groups.all().clear()
        self.educators.all().clear()
        self.added_lessons.all().clear()
        self.hidden_lessons.all().clear()
        self.chosen_educators.all().clear()


class Group(db.Model):
    __tablename__ = "groups"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    members = db.relationship("User", secondary=users_groups_templates,
                              back_populates="groups", lazy="dynamic")

    def get_events(self, from_date=None, to_date=None, lessons_type=None):
        """
        Method to get raw data for group from SPBU

        :param from_date: from date
        :param to_date: to date
        :param lessons_type: type of lessons
        :return: raw data
        :rtype: dict
        """
        return spbu.get_group_events(self.id, from_date, to_date, lessons_type)


class Educator(db.Model):
    __tablename__ = "educators"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    members = db.relationship("User", secondary=users_educators_templates,
                              back_populates="educators", lazy="dynamic")

    def get_events(self, from_date=None, to_date=None, lessons_type=None):
        # TODO change spbu method in future
        return spbu.get_group_events(self.id, from_date, to_date, lessons_type)

    def get_term_events(self, is_next_term=False):
        """
        Method to get raw data for educator's term from SPBU

        :param is_next_term: whether to show the events for the next term
        :type is_next_term: bool
        :return: raw data
        :rtype: dict
        """
        return spbu.get_educator_events(self.id, is_next_term)

    def create_answers_for_term(self, is_next_term=False):
        """
        Method to create educators's term answers

        :param is_next_term: (Optional) is for next term
        :type is_next_term: bool
        :return: list of schedule answers
        :rtype: list of str
        """
        data = self.get_term_events(is_next_term)
        answers = [
            "{0} Расписание преподавателя: <b>{1}</b>\n\n{2} {3}".format(
                emoji["bust_in_silhouette"], data["EducatorLongDisplayText"],
                emoji["calendar"], data["DateRangeDisplayText"]
            )
        ]
        if not data["HasEvents"]:
            answers[-1] += "\n\n<i>Нет событий</i>"
        else:
            for day in data["EducatorEventsDays"]:
                if day["DayStudyEventsCount"]:
                    answers.append(nf.create_master_schedule_answer(day))
        return answers


class Lesson(db.Model):
    __tablename__ = "lessons"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128))
    types = db.Column(db.JSON)
    days = db.Column(db.JSON)
    times = db.Column(db.JSON)
    educators = db.Column(db.JSON)
    locations = db.Column(db.JSON)

    def __contains__(self, other):
        """

        :param other:
        :type other: Lesson
        :return:
        """
        return (other.name == self.name
                and other.types in self.types if self.types else 1
                and other.days in self.days if self.days else 1
                and other.times in self.times if self.times else 1
                and other.educators in self.educators if self.educators else 1
                and other.locations in self.locations if self.locations else 1)

    def __eq__(self, other):
        """

        :param other:
        :type other: Lesson
        :return:
        """
        return (self.name == other.name
                and self.types == other.types
                and self.days == other.days
                and self.times == other.times
                and self.educators == other.educators
                and self.locations == other.locations)

    @staticmethod
    def add_or_get(name, types, days, times, educators, places):
        """
        Так как из полей типа JSON сделать уникальный индекс нельзя, то
        приходится проверять наличие элемента в базе перед добавлением.
        Будет возвращен либо новый объект, либо уже существующий.
        """
        lesson = Lesson.query.filter_by(name=name, types=types, days=days,
                                        times=times, educators=educators,
                                        places=places).first()
        if not lesson:
            lesson = Lesson(name=name, types=types, days=days, times=times,
                            educators=educators, places=places)
            db.session.add(lesson)
        return lesson

    def de_json(self, event):
        self.name = event["Subject"].split(", ")[0]
        self.types = event["Subject"].split(", ")[1]
        self.days = nf.get_key_by_value(
            dct=week_day_number,
            val=nf.datetime_from_string(event["Start"]).date().isoweekday()
        )
        self.times = "{0:0>2}:{1:0>2}{2}{3:0>2}:{4:0>2}".format(
            nf.datetime_from_string(event["Start"]).time().hour,
            nf.datetime_from_string(event["Start"]).time().minute,
            emoji["en_dash"],
            nf.datetime_from_string(event["End"]).time().hour,
            nf.datetime_from_string(event["End"]).time().minute
        )
        self.educators = [e["Item2"].split(", ")[0]
                          for e in event["EducatorIds"]]
        self.locations = [p["DisplayName"] for p in event["EventLocations"]]
        return self
