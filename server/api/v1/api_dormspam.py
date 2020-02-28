from calendar import monthrange
from datetime import date, datetime, timedelta, timezone
from dateutil.relativedelta import relativedelta
import pytz
from dateutil.parser import parse
from datetime import datetime, timedelta
from server.controllers.events import get_events, get_events_by_date
from server.models.event import Event
from server.emails.parse_type import CATEGORIES
from server.api.v1 import return_failure, return_success, require_login
from server.app import app
from flask import Blueprint, abort, jsonify, request, session
from flask_restful import Api, Resource, reqparse

from flask_cors import cross_origin

mod_users = Blueprint("users", __name__)


@mod_users.route("/login", methods=["POST"])
def login():
    if request.json is None:
        return ("No Request", 200)
    if "kerberos" not in request.json:
        abort(400)

    kerberos = request.json["kerberos"]
    if len(kerberos) == 0 or len(kerberos) > 8:
        abort(400)

    return ("", 200)

# TODO(kevinfang): legacy
@mod_users.route("/verify", methods=["POST"])
def verify():
    if "code" not in request.json or "kerberos" not in request.json:
        abort(401)
    return current_user()

# TODO(kevinfang): legacy
@mod_users.route("/current", methods=["GET"])
def current_user():
    global CATEGORIES
    preset_categories = [CATEGORIES[key][2] for key in CATEGORIES]
    return jsonify({
        'kerberos': "test",
        "settings": {
            "filters": [c["id"] for c in preset_categories],
            "preferences": [c["id"] for c in preset_categories],
            "frequency": 1
        },
        'id': 0,
    })

# TODO(kevinfang): legacy
@mod_users.route("/current", methods=["PUT"])
def update_current_user():
    return current_user()

# TODO(kevinfang): legacy
@mod_users.route("/<user_id>/digest", methods=["POST"])
def send_digest(user_id):
    return ("", 204)

# TODO(kevinfang): legacy
@mod_users.route("/current", methods=["DELETE"])
def logout():
    return ("", 204)


mod_categories = Blueprint("categories", __name__)


@mod_categories.route("", methods=["GET"])
def get_categories():
    global CATEGORIES
    return jsonify([CATEGORIES[key][2] for key in CATEGORIES])


mod_events = Blueprint("events", __name__)


@mod_events.route("", methods=["GET"])
def get_server_events():
    search = request.args.get("q")
    if search is None:
        events = get_events()
    else:
        events = get_events(search=search, only_future=True)
    return jsonify([event.serialize() for event in events])


@mod_events.route("/<query>", methods=["GET"])
def get_events_on(query):
    try:
        from_date = parse(query) + timedelta(hours=5) # moding by GMT + 5
        return jsonify([event.serialize() for event in get_events_by_date(from_date)])
    except:
        event = Event.query.filter_by(eid=query).first()
        if event is None:
            abort(404)
        return jsonify(event.serialize())
    return jsonify([])


@mod_events.route("/frequency/<date_string>", methods=["GET"])
def get_events_frequency(date_string):
    global CATEGORIES
    try:
        param = parse(date_string) + timedelta(hours=5) # moding by GMT + 5
        today = param.replace(day=1, hour=5, minute=0, second=0, microsecond=0)
    except:
        abort(400)

    frequencies = {}
    next_month = today + relativedelta(months=1)
    today_str = today.strftime("%m-%d-%Y")
    next_month_str = next_month.strftime("%m-%d-%Y")

    events = get_events().filter(
        Event.time_start.between(today_str, next_month_str))

    for i in range(monthrange(param.year, param.month)[1]):
        frequencies[date(year=param.year, month=param.month, day=i+1).strftime("%Y-%m-%d")] = {
            CATEGORIES[key][2]['name']: 0 for key in CATEGORIES
        }

    for event in events:
        # Correct for timezone difference
        event_dt = event.time_start - timedelta(hours=5)
        event_key = event_dt.strftime("%Y-%m-%d")
        for key in CATEGORIES:
            val, _, data = CATEGORIES[key]
            if event.etype & val > 0:
                try:
                    frequencies[event_key][data['name']] += 1
                except:
                    pass
                    #TODO KeyError: '2020-02-29'
    return jsonify(frequencies)
