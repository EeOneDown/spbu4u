# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import timedelta, date, datetime

import spbu

from app import db, new_functions as nf
from app.constants import (
    week_off_answer, weekend_answer, emoji, changed_to_full_answer,
    changed_to_class_answer, week_day_number, hide_lesson_answer,
    no_lessons_answer, ask_to_select_lesson_answer, hidden_lessons_list_answer,
    no_hidden_lessons_answer, chosen_educators_list_answer,
    ask_to_select_edu_answer, no_chosen_educators_answer,
    selectable_block_answer, ask_to_select_block_lesson_answer,
    months_date
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
    rate = db.Column(db.SmallInteger, default=0)
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

    @staticmethod
    def reg_user(o_id, is_edu, tg_id):
        """
        Registers or updates user

        :param o_id: an object id (educator or group)
        :type o_id: int
        :param is_edu: if the user is an educator
        :type is_edu: bool
        :param tg_id: the user's telegram chat id
        :type tg_id: int
        :return: the new or updated user
        :rtype: User
        """
        obj = (Educator if is_edu else Group).query.get(o_id)
        if not obj:
            if is_edu:
                obj = Educator(
                    id=o_id,
                    title=spbu.get_educator_events(
                        educator_id=o_id)
                    ["EducatorLongDisplayText"]
                )
            else:
                obj = Group(
                    id=o_id,
                    title=spbu.get_group_events(
                        group_id=o_id
                    )["StudentGroupDisplayName"]
                )
            db.session.add(obj)

        user = User.query.filter_by(tg_id=tg_id).first()
        if not user:
            user = User(
                tg_id=tg_id,
                is_educator=is_edu,
                current_group_id=0 if is_edu else o_id,
                current_educator_id=o_id if is_edu else 0
            )
        else:
            user.current_group_id = 0 if is_edu else o_id
            user.current_educator_id = o_id if is_edu else 0
            user.is_educator = is_edu
        db.session.add(user)

        db.session.commit()

        return user

    @staticmethod
    def get_rates():
        """
        Gets users rates dict: keys - rate value, Values - count of users

        :return: users rates
        :rtype: dict
        """
        q = User.query.filter(User.rate != 0).group_by(User.rate)

        rates = {}
        for i in range(1, 6):
            rates[i] = q.filter_by(rate=i).count().scalar()
        return rates

    @staticmethod
    def get_admin_statistics():
        """
        Gets statistics for admins: counts of users, groups, educators and
        subscribed users

        :return: admin statistics
        :rtype: tuple
        """

        return (
            User.query.count().scalar(),
            Group.query.count().scalar(),
            Educator.query.count().scalar(),
            User.query.filter_by(is_subscribed=True).count().scalar()
        )

    def _get_events(self, from_date, to_date, lessons_type=None):
        """
        Gets user's suitable events data

        :param from_date: the date the events start from
        :type from_date: date
        :param to_date: (Optional) the date the events ends
        :type to_date: date
        :param lessons_type: type of lessons
        :type lessons_type: str
        :return: list of events data (json)
        :rtype: list
        """
        if self.is_educator:
            return self._current_educator.get_events(
                from_date=from_date, to_date=to_date, lessons_type=lessons_type
            )["Days"]
        else:
            return self._current_group.get_events(
                from_date=from_date, to_date=to_date, lessons_type=lessons_type
            )["Days"]

    def _parse_event(self, event):
        if not self.is_educator:
            lesson = Lesson().de_json(event)
            for skip in self.hidden_lessons.filter_by(name=lesson.name):
                if lesson.is_skipped_by(skip):
                    return ""
        return nf.create_schedule_answer(event, self.is_full_place)

    def _parse_day_events(self, events, lessons_type=None, is_resit=False):
        """
        This method parses the events data from SPBU API

        :param events: an element of `DayStudyEvents`
        :type events: dict
        :param lessons_type: type of lessons
        :type lessons_type: str
        :param is_resit: is resit required
        :type is_resit: bool
        :return: html safe string
        :rtype: str
        """
        answer = "{0} {1}\n\n".format(
            emoji["calendar"], events["DayString"].capitalize()
        )
        events = nf.delete_cancelled_events(events["DayStudyEvents"])

        if lessons_type in ["Attestation", "Final"] and is_resit:
            events = nf.get_resits_events(events)
        elif lessons_type in ["Attestation", "Final"] and not is_resit:
            events = nf.delete_resits_events(events)

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

    def create_answers_for_interval(self, from_date, to_date=None,
                                    lessons_type=None, is_resit=False):
        """
        Method to create answers for interval. if no `to_date` will return for
        7 days

        :param from_date: the date the events start from
        :type from_date: date
        :param to_date: (Optional) the date the events ends
        :type to_date: date
        :param lessons_type: type of lessons
        :type lessons_type: str
        :param is_resit: is resit required
        :type is_resit: bool
        :return: list of schedule answers
        :rtype: list of str
        """
        answers = []

        if not to_date:
            to_date = from_date + timedelta(days=7)

        events = self._get_events(
            from_date=from_date,
            to_date=to_date,
            lessons_type=lessons_type
        )
        for day_events in events:
            answers.append(
                self._parse_day_events(
                    events=day_events,
                    lessons_type=lessons_type,
                    is_resit=is_resit
                )
            )

        if not len(answers):
            if from_date.isoweekday() == 1 and (to_date - from_date).days == 7:
                answers = [week_off_answer]
            else:
                answers = [nf.create_interval_off_answer(from_date, to_date)]
        return answers

    def get_block_answer(self, for_date, block_num=1):
        """
        Creates block answer number `block_num` for input date

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
        )
        if not events:
            return no_lessons_answer
        else:
            events = events[0]

        blocks = nf.create_events_blocks(events["DayStudyEvents"])
        block = blocks[block_num - 1]

        answer = "<b>" + str(block_num) + " из " + str(len(blocks)) + "</b>\n\n"

        answer += nf.parse_event_time(block[0]) + " <i>(" + nf.get_key_by_value(
            week_day_number, for_date.isoweekday()
        ) + ")</i>" + "\n\n"

        for num, event in enumerate(block, start=1):
            lesson = Lesson().de_json(event)

            hide_mark = ""
            for skip in self.hidden_lessons.filter_by(name=lesson.name):
                if lesson.is_skipped_by(skip):
                    hide_mark = emoji["cross_mark"] + " "
                    break

            answer += str(num) + ". " + hide_mark + nf.parse_event_sub_loc_edu(
                event=event,
                full_place=self.is_full_place
            )
        return answer + hide_lesson_answer

    def get_attestation_months(self, is_resit=False):
        """
        Gets available attestation months dict: keys - number (int),
        values - human-readable string

        :param is_resit: is resit required
        :type is_resit: bool
        :return: attestation months
        :rtype: dict
        """
        events = self._get_events(
            *nf.get_term_dates(), lessons_type="Attestation"
        )
        if is_resit:
            event_filter = nf.get_resits_events
        else:
            event_filter = nf.delete_resits_events

        for day_events in events:
            day_events["DayStudyEvents"] = event_filter(
                day_events["DayStudyEvents"]
            )

        attestation_months = {}
        for day_events in events:
            if day_events["DayStudyEvents"]:
                event_date = datetime.strptime(
                    day_events["Day"], "%Y-%m-%dT%H:%M:%S"
                )
                attestation_months[event_date.month] = "{0} {1}".format(
                    months_date[event_date.month],
                    event_date.year
                )
        return attestation_months

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
        self.clear_groups_templates()
        self.clear_educators_templates()
        self.clear_added_lessons()
        self.clear_hidden_lessons()
        self.clear_chosen_educators()

    def clear_added_lessons(self):
        for lesson in self.added_lessons:
            self.added_lessons.remove(lesson)

    def clear_chosen_educators(self):
        for educator in self.chosen_educators:
            self.chosen_educators.remove(educator)

    def clear_educators_templates(self):
        for educator in self.educators:
            self.educators.remove(educator)

    def clear_groups_templates(self):
        for group in self.groups:
            self.groups.remove(group)

    def clear_hidden_lessons(self):
        for lesson in self.hidden_lessons:
            self.hidden_lessons.remove(lesson)

    def create_lessons_reset_answer(self):
        """
        Method to create lessons reset answer

        :return: answer
        :rtype: str
        """
        if self.hidden_lessons.count():
            answer = hidden_lessons_list_answer
            for lesson in self.hidden_lessons:
                answer += "<b>id: {0}</b>\n".format(lesson.id)
                answer += "<b>Название</b>: {0}\n".format(lesson.name)
                if lesson.types:
                    answer += "<b>Типы</b>: {0}\n".format(lesson.types)
                if lesson.days:
                    answer += "<b>Дни</b>: {0}\n".format(lesson.days)
                if lesson.times:
                    answer += "<b>Время</b>: {0}\n".format(lesson.times)
                if lesson.educators:
                    answer += "<b>Преподаватели</b>: {0}\n".format(
                        lesson.educators
                    )
                answer += "\n"
            return answer + ask_to_select_lesson_answer
        else:
            return no_hidden_lessons_answer

    def create_educators_reset_answer(self):
        """
        Method to create educators reset answer

        :return: answer
        :rtype: str
        """
        if self.chosen_educators.count():
            answer = chosen_educators_list_answer
            for lesson in self.chosen_educators:
                answer += "<b>id: {0}</b>\n".format(lesson.id)
                answer += "<b>Название</b>: {0}\n".format(lesson.name)
                answer += "<b>Преподаватель</b>: {0}\n\n".format(
                    lesson.educators[0]
                )
            return answer + ask_to_select_edu_answer
        else:
            return no_chosen_educators_answer

    def get_selectable_blocks(self):
        """
        Gets selectable blocks: keys - weekday & time, values - event's data.

        :return: selectable blocks
        :rtype: dict
        """
        from_date = nf.get_work_monday()
        week_events = self._get_events(
            from_date=from_date,
            to_date=from_date + timedelta(days=7)
        )
        selectable_blocks = {}
        for day_events in week_events:
            for block in nf.create_events_blocks(
                    nf.delete_cancelled_events(day_events["DayStudyEvents"])
            ):
                if len(block) > 1:
                    key = "{0} {1}".format(
                        day_events["DayString"].split(", ")[0].capitalize(),
                        nf.parse_event_time(block[0])
                    )
                    selectable_blocks[key] = block
        return selectable_blocks

    def parse_selectable_block(self, block):
        """

        :param block:
        :return:
        """
        answer = selectable_block_answer
        for num, event in enumerate(block, start=1):
            subject = nf.parse_event_subject(event)

            lesson = Lesson().de_json(event)

            hide_mark = ""
            for skip in self.hidden_lessons.filter_by(name=lesson.name):
                if lesson.is_skipped_by(skip):
                    hide_mark = " " + emoji["cross_mark"]
                    break

            locations = ""
            for location in event["EventLocations"]:
                locations += nf.parse_event_location(location)
                locations += "\n"

            answer += "<b>{0}. {1}</b>{2}\n{3}\n".format(
                num, subject, hide_mark, locations
            )
        return answer + ask_to_select_block_lesson_answer

    def hide_block_lessons(self, text, chosen_idx):
        """
        Hides all lessons from block (bot's answer) and returns answer
        with chosen lesson

        :param text: bot's text created by `User.parse_selectable_block()`
        :type text: str
        :param chosen_idx: index of chosen lesson
        :type chosen_idx: int
        :return: answer with chosen lesson
        :rtype: str
        """
        # Удаляем все метки скрытых занятий
        bot_message_text = text.replace(" " + emoji["cross_mark"], "")
        # берем список занятий
        lessons = bot_message_text.split("\n\n")[1:-1]

        # Получаем название выбранного занятия
        chosen_lesson_name = emoji["en_dash"].join(
            lessons[chosen_idx].split("\n")[0].split(emoji["en_dash"])[1:]
        ).strip()
        # Сразу преподов не заполняем, так как список может не понадобиться
        chosen_lesson_educators = []

        for lesson in lessons:
            # Парсим каждое занятие, кроме выбранного
            if lessons.index(lesson) == chosen_idx:
                continue

            # Получаем название выбранного занятия
            hide_event_name = emoji["en_dash"].join(
                lesson.split("\n")[0].split(emoji["en_dash"])[1:]
            ).strip()
            # Преподов опять же сразу не заполняем
            hide_educators = []

            # Если несколько одинаковых занятий по названию, то скрываем
            # вместе с преподавателями
            if hide_event_name == chosen_lesson_name:
                # Создаем список преподов оставленного занятия..
                if not chosen_lesson_educators:
                    for place_edu in lessons[chosen_idx].split("\n")[
                                     1:]:
                        pos = place_edu.find("(")
                        # ..если это, конечно, возможно
                        if pos != -1:
                            chosen_lesson_educators.append(
                                place_edu[pos + 1:-1])

                # Получаем список преподов у скрываемого занятия..
                for place_edu in lesson.split("\n")[1:]:
                    pos = place_edu.find("(")
                    # ..если это, конечно, возможно
                    if pos != -1:
                        hide_educators.append(place_edu[pos + 1:-1])

            # И скрываем его
            hidden_lesson = Lesson.add_or_get(
                name=hide_event_name,
                types=[],
                days=[],
                times=[],
                educators=hide_educators,
                locations=[]
            )
            if hidden_lesson not in self.hidden_lessons:
                self.hidden_lessons.append(hidden_lesson)

        return "Выбрано занятие <b>{0}</b> <i>{1}</i>".format(
            chosen_lesson_name, chosen_lesson_educators or ""
        )

    def get_poliedu_lessons(self):
        pass


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

    @staticmethod
    def add_or_get(name, types, days, times, educators, locations):
        """
        Так как из полей типа JSON сделать уникальный индекс нельзя, то
        приходится проверять наличие элемента в базе перед добавлением.
        Будет возвращен либо новый объект, либо уже существующий.
        """
        lesson = Lesson.query.filter_by(name=name, types=types, days=days,
                                        times=times, educators=educators,
                                        locations=locations).first()
        if not lesson:
            lesson = Lesson(name=name, types=types, days=days, times=times,
                            educators=educators, locations=locations)
            db.session.add(lesson)
        return lesson

    def de_json(self, event):
        self.name = event["Subject"].split(", ")[0]
        self.types = [event["Subject"].split(", ")[1]]
        self.days = [nf.get_key_by_value(
            dct=week_day_number,
            val=nf.datetime_from_string(event["Start"]).date().isoweekday()
        )]
        self.times = [nf.parse_event_time(event).split()[1]]
        self.educators = [e["Item2"].split(", ")[0]
                          for e in event["EducatorIds"]]
        self.locations = [p["DisplayName"] for p in event["EventLocations"]]
        return self

    def is_skipped_by(self, skip):
        """

        :param skip:
        :type skip: Lesson
        :return:
        """
        return (
            skip.name == self.name
            and (set(skip.types).issuperset(set(self.types))
                 if skip.types else 1)
            and (set(skip.days).issuperset(set(self.days))
                 if skip.days else 1)
            and (set(skip.times).issuperset(set(self.times))
                 if skip.times else 1)
            and (set(skip.educators).issuperset(set(self.educators))
                 if skip.educators else 1)
            and (set(skip.locations).issuperset(set(self.locations))
                 if skip.locations else 1)
        )

    def __eq__(self, other):
        """

        :param other:
        :type other: Lesson
        :return:
        """
        return (
            self.name == other.name
            and set(self.types or []) == set(other.types or [])
            and set(self.days or []) == set(other.days or [])
            and set(self.times or []) == set(other.times or [])
            and set(self.educators or []) == set(other.educators or [])
            and set(self.locations or []) == set(other.locations or [])
        )
