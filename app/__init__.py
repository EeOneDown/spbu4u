# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import flask
from os import path

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
# from flask_sslify import SSLify

basedir = path.abspath(path.dirname(__file__))

app = flask.Flask(__name__)
app.config.update(
    dict(
        SECRET_KEY="powerful-secretkey",
        WTF_CSRF_SECRET_KEY="a-csrf-secret-key",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_DATABASE_URI="mysql+pymysql://<user>:<password>@<host>:<port>/<db_name>"
    )
)

# sslify = SSLify(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)


from app import routes

