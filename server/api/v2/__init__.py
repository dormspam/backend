from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager
from flask_sslify import SSLify
from flask_sqlalchemy import SQLAlchemy

import os

app = None
db = None

def create_app():
    global app, db

    # Create the main flask app
    app = Flask(__name__)

    # Load .env or environment variables into app.config
    env = {}

    try:
        with open(".env", "r") as f:
            for line in f.readlines():
                if "=" in line:
                    env[line.split("=")[0]] = line.split("=")[1].replace("\"", "").replace("\n", "")
    except:
        pass

    def load_variable(key):
        if key in os.environ:
            app.config[key] = os.environ[key]
        elif key in env:
            app.config[key] = env[key]
        else:
            pass

    variables = [
        "AWS_SES_ACCESS_KEY_ID",
        "AWS_SES_SECRET_ACCESS_KEY",
        "LAMBDA_KEY",
        "SECRET_KEY",
        "SQLALCHEMY_DATABASE_URI",
        "SQLALCHEMY_TRACK_MODIFICATIONS"
    ]

    for key in variables:
        load_variable(key)

    # Load other variables from config.py
    app.config.from_object("config")

    # Set up CORS and database
    cors = CORS(app, supports_credentials=True)
    db = SQLAlchemy(app)
    ssl = SSLify(app, permanent=True)

    # Set up login manager to keep track of sessions
    login_manager = LoginManager()
    login_manager.init_app(app)

    from app.mod_users import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.filter_by(id=user_id).first()

    # Register routes
    from app.mod_users.controllers import mod_users
    app.register_blueprint(mod_users)

    from app.mod_events.controllers import mod_events
    app.register_blueprint(mod_events)

    from app.mod_categories.controllers import mod_categories
    app.register_blueprint(mod_categories)

    # Create database tables
    db.create_all()

    # Populate categories
    from app.mod_categories import load_default_categories
    load_default_categories()

    return app
