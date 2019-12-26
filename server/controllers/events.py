from server.models.event import Event
from server.app import db
from datetime import timedelta
from sqlalchemy import exc


def get_event(eid, token, override = True):
    event = Event.query.filter_by(eid=eid).first()
    if not override and (event is None or event.token != token):
        return None
    return event

def get_events():
    return Event.query.filter_by(approved_is=True)

def create_server_event(title, etype, descrition, time_start, time_end=None, link=None, headerInfo=None):
    event = Event(None)
    event.header = headerInfo
    event.title = title
    event.etype = etype
    event.description = descrition
    event.time_start = time_start
    event.time_end = time_start + \
        timedelta(hours=1) if time_end is None else time_end
    event.cta_link = link

    retry = 10
    committed = False
    while (not committed and retry > 0):
        try:
            db.session.add(event)
            db.session.commit()
        except exc.IntegrityError:
            db.session.rollback()
            event.generateUniques()
            retry -= 1
        else:
            committed = True
    if not committed:
        return None
    return event

def update_and_publish_event(eid, token, title, etype, descrition, time_start, time_end=None, link=None):
    event = get_event(eid, token)
    if (event is None):
        return False
    event.published_is = True
    event.title = title
    event.etype = etype
    event.description = descrition
    event.time_start = time_start
    event.time_end = time_start + \
        timedelta(hours=1) if time_end is None else time_end
    event.cta_link = link
    db.session.commit()
    return True

def approve_event(eid):
    event = get_event(eid, None, override=True)
    if event is None:
        return False
    event.approved_is = True
    db.session.commit()
    return True