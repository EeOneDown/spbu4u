# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from flask import Blueprint

bp = Blueprint('main', __name__)

from app.main import routes
