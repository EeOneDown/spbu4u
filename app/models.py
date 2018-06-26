from app import db


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
    is_subscribed = db.Column(db.Boolean,default=False, nullable=False)
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


class Group(db.Model):
    __tablename__ = "groups"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    members = db.relationship("User", secondary=users_groups,
                              back_populates="groups", lazy="dynamic")


class Lesson(db.Model):
    __tablename__ = "lessons"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128))
    types = db.Column(db.String)        # mb JSON/ARRAY?
    days = db.Column(db.String)         # mb JSON/ARRAY?
    times = db.Column(db.String)        # mb JSON/ARRAY?
    educators = db.Column(db.String)    # mb JSON/ARRAY?
    __table_args__ = (db.UniqueConstraint("name", "types", "days", "times",
                                          "educators"), )
