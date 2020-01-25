from datetime import date, datetime, timedelta, timezone
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from flask import Blueprint, abort, jsonify, request
from calendar import monthrange
from flask_login import login_required
import pytz

from server.app import db
from server.models import Event
# from server.api.v2.utils import lambda_only

import json

mod_events = Blueprint("events", __name__)

@mod_events.route("", methods=["GET"])
@login_required
def get_events():
    search = request.args.get("q")

    if search is None:
        events = Event.query.all()
    else:
        filter = "%" + search + "%"
        today = str(datetime.now()).split(" ")[0]
        events = Event.query.filter((Event.description.ilike(filter) | Event.host.ilike(filter) | Event.name.ilike(filter)) & (Event.start_time >= today)).order_by(Event.start_time.asc()).all()

    return jsonify([event.serialize() for event in events])

@mod_events.route("", methods=["POST"])
# @lambda_only
def create_event():
    event = Event(request.json)
    db.session.add(event)
    db.session.commit()

    return ("", 204)

@mod_events.route("/<query>", methods=["GET"])
@login_required
def get_events_on(query):
    try:
        param = parse(query)
    except:
        event = Event.query.filter_by(eid=query).first()

        if event is None:
            abort(404)

        return jsonify(event.serialize())

    from_date = param + timedelta(hours=5)
    to_date = from_date + timedelta(days=1)

    events = Event.query.filter(Event.time_start.between(from_date, to_date)).all()
    return jsonify([event.serialize() for event in events])

@mod_events.route("/frequency/<date_string>", methods=["GET"])
@login_required
def get_events_frequency(date_string):
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
    
    events = Event.query.filter(Event.time_start.between(today_str, next_month_str)).with_entities(Event.time_start, Event.etype).all()

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
        event_dt = event[0] - timedelta(hours=5)#.replace(tzinfo=timezone.utc) #- timedelta(hours=5)
        #event_dt = event_dt.astimezone(pytz.timezone("America/New_York"))
        event_key = event_dt.strftime("%Y-%m-%d")
        event_categories = list(map(lambda x: x.replace('"', ''), event[1][1:-1].split(",")))
        for category in event_categories:
            if len(category) > 0:
                try:
                    frequencies[event_key][category] += 1
                except KeyError:
                    print(f'EST: {param}, UTC: {utcparam}')
                    print(f'EVENT_KEY: {event_key}')
    print(param, frequencies)
    #raise(Exception)
    return jsonify(frequencies)
