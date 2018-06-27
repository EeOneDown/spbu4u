# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from app import db
import spbu
from bot import functions as f
from datetime import timedelta


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
    telegram_id = db.Column(db.Integer, index=True, unique=True, nullable=False)
    is_educator = db.Column(db.Boolean, default=False, nullable=False)
    is_full_place = db.Column(db.Boolean, default=True, nullable=False)
    is_subscribed = db.Column(db.Boolean, default=False, nullable=False)
    home_station_code = db.Column(db.String(10), default="c2", nullable=False)
    univer_station_code = db.Column(db.String(10), default="s9603770",
                                    nullable=False)
    current_group_id = db.Column(db.Integer, db.ForeignKey("groups.id"))
    groups = db.relationship("Group", secondary=users_groups,
                             back_populates="members", lazy="dynamic")
    added_lessons = db.relationship("Lesson", secondary=users_added_lesson,
                                    lazy="dynamic")
    hidden_lessons = db.relationship("Lesson", secondary=users_hidden_lessons,
                                     lazy="dynamic")
    chosen_educators = db.relationship("Lesson",
                                       secondary=users_chosen_educators,
                                       lazy="dynamic")
    current_group = db.relationship("Group")

    def create_day_schedule_answer(self, date):
        schedule_data = self.current_group.get_events(
            from_date=date, to_date=date + timedelta(days=1)
        )['Days']
        if len(schedule_data):
            answer = f.create_schedule_answer(schedule_data[0],
                                              self.is_full_place)
        else:
            answer = "Выходной"
        return answer


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
        Будет возвращен либо новый объект, либо уже существующий."""

        lesson = Lesson.query.filter_by(name=name, types=types, days=days,
                                        times=times, educators=educators,
                                        places=places).one_or_none()
        if not lesson:
            lesson = Lesson(name=name, types=types, days=days, times=times,
                            educators=educators, places=places)
        return lesson
