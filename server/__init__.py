from server.app import app
from server.api.v1.api import api
# from server.api.v2 import mod_users, mod_events, mod_categories
from flask import Flask
from flask_restful import Api
import sys

from server.api.v2.mod_events import mod_events


# app.register_blueprint(api.blueprint, url_prefix='/api/v1')

# app.register_blueprint(mod_users, url_prefix='/api/v2/categories')
app.register_blueprint(mod_events, url_prefix='/api/v2/events')
# app.register_blueprint(mod_categories, url_prefix='/api/v2/users')