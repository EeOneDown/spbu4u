from flask import Blueprint

bp = Blueprint('tg', __name__)

from app.tg import routes
