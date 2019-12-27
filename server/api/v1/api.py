from flask import Blueprint, request, Response
from flask_restful import Api, Resource, reqparse
from server.app import app
from server.api.v1 import api_login
from server.api.v1 import api_events
import json

# NOTE: all the following resources by default start with '/api/v1' so there's
# no need to specify that


class HelloWorld(Resource):
    def get(self):
        return {'success': False, 'message': "Please use post requests"}

    def post(self):
        return {'success': True}


# Blueprint for /api/v1 requests
api = Api(Blueprint('api', __name__))

# Endpoint registration
api.add_resource(HelloWorld, '')  # This would be the default hostname/api/v1

# Events
api.add_resource(api_events.ServerCreateEvent, "/events/server/create")
api.add_resource(api_events.PublishEvent, "/events/publish")
api.add_resource(api_events.ApproveEvent, "/events/approve")

api.add_resource(api_events.GetEvents, "/events")
api.add_resource(api_events.GetAllEvents, "/events/all")
api.add_resource(api_events.GetEvent, "/events/event")

# Login
api.add_resource(api_login.ClientLogin, '/client/login')