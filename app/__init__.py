# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import flask

# from flask_sslify import SSLify
from flask_bootstrap import Bootstrap

app = flask.Flask(__name__)
# sslify = SSLify(app)
bootstrap = Bootstrap(app)


from app import routes

