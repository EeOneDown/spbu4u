from flask import render_template, current_app

from app.main import bp
from app.models import User


@bp.route("/")
@bp.route("/index")
def index():
    from requests import get

    url = "https://api.rasp.yandex.net/v3.0/copyright/"
    params = {"apikey": current_app.config['YANDEX_API_KEY'], "format": "json"}

    data = get(url, params=params).json()["copyright"]

    return render_template("index.html", bot_name="Spbu4UBot", url=data["url"],
                           text=data["text"])


@bp.route("/<tg_id>/<idate>/<n>")
def schedule(tg_id, idate, n):
    from datetime import date
    user = User.query.filter_by(tg_id=tg_id).first()
    answers = user.create_answers_for_interval(
        from_date=date(2018, 6, int(idate)),
        to_date=date(2018, 6, int(idate) + int(n)))
    return render_template("schedule.html", answers=answers)
