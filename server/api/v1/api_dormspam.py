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

@mod_users.route("/verify", methods=["POST"])
def verify():
    if "code" not in request.json or "kerberos" not in request.json:
        abort(401)
    return jsonify({
        'kerberos': "test",
        "settings": {},
        'id': 0,
    })

mod_categories = Blueprint("categories", __name__)

@mod_categories.route("", methods=["GET"])
def get_categories():
    categories = [
    {
        "name": "Boba",
        "id": "boba",
        "description": "Mouthwatering, scrumptious goodness",
        "color": "#F6B957"
    },
    {
        "name": "Food",
        "id": "food",
        "description": "Breakfast, lunch, and dinner served",
        "color": "#EE6F6F"
    },
    {
        "name": "Tech",
        "id": "tech",
        "description": "Computer science, hackathons, and everything in between",
        "color": "#A16EE5"
    },
    {
        "name": "EECS-jobs-announce",
        "id": "eecs",
        "description": "All events from the EECS-jobs-announce mailing list",
        "color": "#5A56EF"
    },
    {
        "name": "Recruiting",
        "id": "recruiting",
        "description": "Recruiting events held by companies on campus",
        "color": "#459AF6"
    },
    {
        "name": "Social",
        "id": "social",
        "description": "Parties, karaoke nights, and food related outings",
        "color": "#25C8D3"
    },
    {
        "name": "Performance Groups",
        "id": "performance",
        "description": "Dance, music, a capella, and other concerts and performances",
        "color": "#12DAA4"
    },
    {
        "name": "Talks",
        "id": "talks",
        "description": "Talks and short classes about anything you can imagine!",
        "color": "#73F23A"
    }
]
    return jsonify(categories)

from server.models.event import Event
from datetime import datetime, timedelta
from dateutil.parser import parse

mod_events = Blueprint("events", __name__)

@mod_events.route("", methods=["GET"])
def get_events():
    search = request.args.get("q")

    if search is None:
        events = Event.query.all()
    else:
        filter = "%" + search + "%"
        today = str(datetime.now()).split(" ")[0]
        events = Event.query.filter(Event.description.ilike(filter)).order_by(Event.time_start.asc()).all()
    # TODO(kevinfang) Filter
    return jsonify([event.serialize() for event in events])

@mod_events.route("/<query>", methods=["GET"])
def get_events_on(query):
    print("QUERY DATE")
    try:
        param = parse(query)
    except:
        event = Event.query.filter_by(eid=query).first()

        if event is None:
            abort(404)

        return jsonify(event.serialize())

    # TODO(kevinfang) What is this timezone crap 
    from_date = param
    to_date = from_date + timedelta(days=1)

    events = Event.query.filter(Event.time_start.between(from_date, to_date)).all()
    return jsonify([event.serialize() for event in events])

import pytz
from dateutil.relativedelta import relativedelta
from datetime import date, datetime, timedelta, timezone
from calendar import monthrange

@mod_events.route("/frequency/<date_string>", methods=["GET"])
def get_events_frequency(date_string):
    print(date_string)
    try:
        param = parse(date_string)
    except:
        abort(400)

    frequencies = {}
    #param = param #- timedelta(hours=5)
    param = param.replace(tzinfo=pytz.timezone("America/New_York"))
    utcparam = param.astimezone(pytz.timezone("UTC"))
    print(f"UTC: {utcparam}")
    today = param.replace(day=1, hour=5, minute=0, second=0, microsecond=0)# + timedelta(hours=5)

    #today = (utcparam - timedelta(days=utcparam.day - 1)).replace(hour=0, minute=0, second=0, microsecond=0)
    print(f"FIRST DAY OF MONTH: {today}")
    next_month = today + relativedelta(months=1) 
    print(f"NEXT_MONTH: {next_month}")
    today_str = today.strftime("%m-%d-%Y")
    next_month_str = next_month.strftime("%m-%d-%Y")
    
    events = Event.query.filter(Event.time_start.between(today_str, next_month_str)).all()

    # CATEGORIES = {
    #     'FOOD': (1 << 2, ["cookie", "food", "eat", "study break", "boba", "bubble tea", "chicken", "bonchon", "bon chon", "bertucci",
    #                     "pizza", "sandwich", "leftover", "salad", "burrito", "dinner provided", "lunch provided", "breakfast provided",
    #                     "dinner included", "lunch included", "ramen", "kbbq", "dumplings", "waffles", "csc",
    #                     "aaa", "ats", "dim sum", "drink"]),
    #     'CAREER': (1 << 3, ["career", "summer plans", "internship", "xfair", "recruiting"]),
    #     'FUNDRAISING': (1 << 4, ["donate"]),
    #     'APPLICATION': (1 << 5, ["apply", "deadline", "sign up", "audition", "join", "application"]),
    #     'PERFORMANCE': (1 << 6, ["orchestra", "shakespeare", "theatre", "theater", "tryout",
    #                             "audition", "muses", "serenade", "syncopasian", "ohms", "logarhythms", "chorallaries",
    #                             "symphony", "choir", "concert", "ensemble", "jazz", "resonance", "a capella", "toons",
    #                             "sing", "centrifugues", "dancetroupe", "adt", "asian dance team", "mocha moves",
    #                             "ridonkulous", "donk", "fixation", "bhangra", "roadkill", "vagina monologues", "24 hour show", "acappella", "admission", "ticket"]),
    #     'BOBA': (1 << 7, ["boba", "bubble tea", "kung fu tea", "kft", "teado", "tea do"]),
    #     'TALKS': (1 << 8, ["discussion", "q&a", "tech talk", "recruiting", "info session", "information session"
    #                     "infosession", "workshop", "research"]),
    #     'EECS-jobs-announce': (1 << 9, ["eecs-jobs-announce"]),
    # }
    
    #param = param.astimezone(pytz.timezone("America/New_York"))
    print(f"EST: {param}")
    for i in range(monthrange(param.year, param.month)[1]):
        frequencies[date(year=param.year, month=param.month, day=i+1).strftime("%Y-%m-%d")] = {
            "Boba": 0,
            "Food": 0,
            "Tech": 0,
            "EECS-jobs-announce": 0,
            "Recruiting": 0,
            "Social": 0,
            "Performance Groups": 0,
            "Talks": 0,
            "Other": 0
        }
    print(frequencies.keys())
    for event in events:
        print(event)
        event_dt = event.time_start - timedelta(hours=5)
        event_key = event_dt.strftime("%Y-%m-%d")
        KEYS= {
            1 << 2: 'Food',
            1 << 3: 'Recruiting' 
        }
        for key in KEYS:
            if event.etype & key > 0:
                frequencies[event_key][KEYS[key]] += 1
        
    print(param, frequencies)
    #raise(Exception)
    return jsonify(frequencies)
