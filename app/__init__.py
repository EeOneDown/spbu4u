# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import flask

# from flask_sslify import SSLify

app = flask.Flask(__name__)
# sslify = SSLify(app)

from app import routes

