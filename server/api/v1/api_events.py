from server.cache import should_cache_function
from flask_restful import Resource, reqparse
from server.controllers.events import *
from server.emails.parse import parse_email, new_parse_dates
from server.emails.parse_dates import parse_dates_possibilities
from server.emails.parse_location import parse_all_locations
from server.api.v1 import return_failure, return_success, require_login
from server.models import update_db, remove_from_db
from datetime import timedelta, datetime
from server.app import app
from typing import cast

SERVER_CREATE_PARSER = reqparse.RequestParser(bundle_errors=True)
SERVER_CREATE_PARSER.add_argument('api_key',
                                  help='Need api_key',
                                  required=True)

SERVER_CREATE_PARSER.add_argument('email',
                                  help='Need email',
                                  required=True)


class ServerCreateEvent(Resource):
    def get(self):
        return {'success': False, 'message': "Please use post requests"}

    def post(self):
        data = SERVER_CREATE_PARSER.parse_args()
        if data["api_key"] != app.config["SERVER_API_KEY"]:
            return return_failure("api key incorrect")
        event = parse_email(data["email"])
        if (event is not None):
            return return_success({'event': event.json()})
        else:
            return return_failure("could not parse email")


PUBLISH_EVENT = reqparse.RequestParser(bundle_errors=True)
PUBLISH_EVENT.add_argument('eid',
                           help='Need eid',
                           required=True)
PUBLISH_EVENT.add_argument('etoken',
                           help='Need token',
                           required=False)
PUBLISH_EVENT.add_argument('title',
                           help='Need title',
                           required=True)
PUBLISH_EVENT.add_argument('description')
PUBLISH_EVENT.add_argument('link')
PUBLISH_EVENT.add_argument('start_date')
PUBLISH_EVENT.add_argument('end_date')
PUBLISH_EVENT.add_argument('location')
PUBLISH_EVENT.add_argument('etype')

DUPLICATE_EVENT = reqparse.RequestParser(bundle_errors=True)
DUPLICATE_EVENT.add_argument('eid',
                             help='Need eid',
                             required=True)
DUPLICATE_EVENT.add_argument('start_date')
DUPLICATE_EVENT.add_argument('end_date')
DUPLICATE_EVENT.add_argument('location')


DELETE_EVENT = reqparse.RequestParser(bundle_errors=True)
DELETE_EVENT.add_argument('eid',
                             help='Need eid',
                             required=True)


class DeleteEvent(Resource):
    @require_login(DELETE_EVENT)
    def post(self, data, user):
        event = get_event(data.eid, "", user=user)
        if event:
            remove_from_db([event])
            return return_success({"message": "deleted event" + data.eid})
        return return_failure("could not get event")


class DuplicateEvent(Resource):
    @require_login(DUPLICATE_EVENT)
    def post(self, data, user):
        event = get_event(data.eid, "", user=user)
        if not event:
            return return_failure("could not get event")
        new_event = create_server_event(event.title, event.etype, event.description, data.start_date, message_html=event.description_html,
                                        location=data.location, time_end=data.end_date, link=event.cta_link, headerInfo=event.header)
        if new_event:
            new_event.parent_event_is = True
            new_event.parent_event = event
            new_event.published_is = True
            new_event.approved_is = True
            update_db()
            return return_success({"message": "published and waiting approval!"})
        return return_failure("could not create event")


class PublishEvent(Resource):
    @require_login(PUBLISH_EVENT)
    def post(self, data, user):
        if (update_and_publish_event(
            data['eid'],
            data['etoken'],
            data['title'],
            data['etype'],
            data['description'],
            data['start_date'],
            data['end_date'],
            data['link'],
            user=user,
            location=data['location']
        )):
            return return_success({"message": "published and waiting approval!"})
        return return_failure("something went wrong")


APPROVE_EVENT = reqparse.RequestParser(bundle_errors=True)
APPROVE_EVENT.add_argument('eid',
                           help='Need eid',
                           required=True)


class ApproveEvent(Resource):
    @require_login(APPROVE_EVENT)
    def post(self, data, user):
        if (not user.admin_is):
            return return_failure("user not admin")
        if(approve_event(data['eid'])):
            return return_success({'message': "approval toggled"})
        return return_failure("could not find event")


GET_EVENTS = reqparse.RequestParser(bundle_errors=True)


# Events should update every 5 mins
@should_cache_function("api_events_get_events_convert", 5 * 60)
def convert_to_json(events):
    return {
        'events': [e.json(fullJSON=0) for e in events]
    }


class GetEvents(Resource):
    # @require_login(GET_EVENTS)
    # def post(self, data, user):
    def post(self):
        events = get_events()
        return return_success(convert_to_json(events))


class GetAllEvents(Resource):
    @require_login(GET_EVENTS)
    def post(self, data, user):
        if (not user.admin_is):
            return return_failure("not admin")
        events = get_all_events()
        return return_success({
            'events': [e.json(fullJSON=0) for e in events]
        })


GET_EVENT = reqparse.RequestParser(bundle_errors=True)
GET_EVENT.add_argument('eid',
                       help='Need eid',
                       required=True)


class GetEvent(Resource):
    @require_login(GET_EVENT)
    def post(self, data, user):
        event = get_event(data['eid'], None, override=True)
        if (event is None):
            return return_failure("could not find event")
        dates = parse_dates_possibilities(event.description)
        if dates is None:
            dates = []
        same_day_events = []
        seen_eids = set()
        seen_eids.add(event.eid)
        for e in get_events_by_date(event.time_start - timedelta(days=1)):
            if e.eid not in seen_eids:
                same_day_events.append(e.json(fullJSON=0))
                seen_eids.add(e.eid)
        for e in get_events_by_date(event.time_start):
            if e.eid not in seen_eids:
                same_day_events.append(e.json(fullJSON=0))
                seen_eids.add(e.eid)

        return return_success({
            'event': {
                **event.json(),
                'alternate_dates': [(x[0], x[1].isoformat() + "Z") for x in dates],
                'alternate_location': parse_all_locations(event.description),
                'alternate_events': [e.json(fullJSON=0) for e in get_event_children(event)],
                'same_day_events': same_day_events
            }
        })
