from flask_restful import Resource, reqparse
from server.controllers.events import *
from server.emails.parse import parse_email
from server.api.v1 import return_failure, return_success, require_login
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
        parse_email(data["email"])
        return return_success({"message":"created event"})


PUBLISH_EVENT = reqparse.RequestParser(bundle_errors=True)
PUBLISH_EVENT.add_argument('eid',
                           help='Need eid',
                           required=True)
PUBLISH_EVENT.add_argument('etoken',
                           help='Need token',
                           required=True)
PUBLISH_EVENT.add_argument('title',
                                  help='Need title',
                                  required=True)
PUBLISH_EVENT.add_argument('description')
PUBLISH_EVENT.add_argument('link')
PUBLISH_EVENT.add_argument('start_date')
PUBLISH_EVENT.add_argument('end_date')
PUBLISH_EVENT.add_argument('etype')

class PublishEvent(Resource):
    @require_login(PUBLISH_EVENT)
    def post(self, data, user):
        if (update_and_publish_event(data['eid'], data['etoken'], data['title'], data['etype'], data['description'],
                            data['start_date'], data['end_date'], data['link'])):
            return return_success({"message":"published and waiting approval!"})
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
            return return_success()
        return return_failure("could not find event")

GET_EVENTS = reqparse.RequestParser(bundle_errors=True)
class GetEvents(Resource):
    # @require_login(GET_EVENTS)
    # def post(self, data, user):
    def post(self):
        events = get_events()
        return return_success({
            'events': [e.json() for e in events]
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
        return return_success({
            'event': event.json()
        })
