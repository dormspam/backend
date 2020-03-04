from server.models.event import Event
from server.app import db
from datetime import timedelta, datetime
from sqlalchemy import exc


def get_event(eid, token, override=False, user=None):
    event = Event.query.filter_by(eid=eid).first()
    if (user is not None and user.admin_is):
        return event
    if not override and (event is None or event.token != token):
        return None
    return event


def get_events_by_date(from_date):
    to_date = from_date + timedelta(days=1)
    events = get_events().filter(
        Event.time_start.between(from_date, to_date))
    return events


def get_event_children(event):
    events = Event.query.filter_by(
        parent_event_is=True, parent_event=event).all()
    return events


def get_events(search=None, only_future=False):
    if search is not None:
        search = "%" + search + "%"
        q = Event.query.filter_by(approved_is=True).filter(
            Event.description.ilike(search)).order_by(Event.time_start.asc())
        if only_future:
            # TODO(kevinfang) ugly
            today = str(datetime.now()).split(" ")[0]
            q = q.filter(Event.time_start >= today)
        return q
    return Event.query.filter_by(approved_is=True)


def get_all_events():
    return Event.query.yield_per(10)


def create_server_event(title, etype, description, time_start, message_html=None,
                        location=None, time_end=None, link=None, headerInfo=None):
    event = Event(None)
    event.header = headerInfo
    event.title = title
    event.etype = etype
    event.description = description
    event.location = location
    event.description_html = message_html
    if (time_start is None):
        event.time_start = datetime.now()
        event.time_end = datetime.now()
    else:
        event.time_start = time_start
        event.time_end = (time_start +
                          timedelta(hours=1)) if time_end is None else time_end
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


def update_and_publish_event(eid, token, title, etype, description, time_start, time_end=None, link=None, user=None, location=None):
    event = get_event(eid, token, user=user)
    if (event is None):
        return False
    event.published_is = True
    event.title = title
    event.etype = etype
    event.description = description
    if location:
        event.location = location
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
    event.approved_is = not event.approved_is
    db.session.commit()
    return True
