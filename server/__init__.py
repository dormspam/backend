from server.app import app
from server.api.v1.api import api
from server.api.v1.api_dormspam import mod_users, mod_categories, mod_events
from flask import Flask
from flask_cors import CORS
from flask_restful import Api
import sys

app.register_blueprint(api.blueprint, url_prefix='/api/v1')
app.register_blueprint(mod_users, url_prefix="/users")
app.register_blueprint(mod_categories, url_prefix="/categories")
app.register_blueprint(mod_events, url_prefix="/events")
cors = CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}}, supports_credentials=True)
cors = CORS(app, resources={r"/events/frequency/*": {"origins": "http://localhost:3000"}}, supports_credentials=True)
print(app.blueprints.keys())