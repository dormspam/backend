# import json
# from datetime import datetime, timedelta
# from flask import Blueprint, abort, jsonify, request, session
# from flask_login import current_user, login_required, login_user, logout_user
# from random import randint

# from app import app, db
# from app.mod_events import Event
# from app.mod_users import User
# from app.utils import Template, send_email

# mod_users = Blueprint("users", __name__)

# @mod_users.route("/current", methods=["GET"])
# @login_required
# def get_current_user():
#     return jsonify(current_user.serialize(True))

# @mod_users.route("/login", methods=["POST"])
# def login():
#     if "kerberos" not in request.json:
#         abort(400)

#     kerberos = request.json["kerberos"]

#     if len(kerberos) == 0 or len(kerberos) > 8:
#         abort(400)

#     user = User.query.filter_by(kerberos=kerberos).first()
#     code = "%04d" % randint(0, 9999)

#     if user is None:
#         user = User(kerberos)
#         db.session.add(user)

#     user.login_code = code
#     user.login_code_time = datetime.utcnow()
#     db.session.commit()

#     send_email(Template.VERIFY, kerberos + "@mit.edu", {"code": code})

#     return ("", 204)

# @mod_users.route("/verify", methods=["POST"])
# def verify():
#     if "code" not in request.json or "kerberos" not in request.json:
#         abort(401)

#     code = request.json["code"]
#     kerberos = request.json["kerberos"]

#     user = User.query \
#                .filter_by(kerberos=kerberos) \
#                .filter_by(login_code=code) \
#                .first()

#     # Make sure user exists and tried to log in within last 10 minutes
#     if user is None:
#         abort(401)
#     elif datetime.utcnow() - timedelta(minutes=10) > user.login_code_time:
#         abort(401)

#     user.login_code = None
#     db.session.commit()

#     login_user(user, remember=True)
#     return jsonify(user.serialize(True))

# @mod_users.route("/current", methods=["PUT"])
# @login_required
# def update_current_user():
#     def update_key(key):
#         if key in request.json:
#             settings = json.loads(current_user.settings)
#             settings[key] = request.json[key]
#             current_user.settings = json.dumps(settings)

#     update_key("frequency")
#     update_key("preferences")
#     update_key("filters")
#     db.session.commit()

#     return get_current_user()

# @mod_users.route("/<user_id>/digest", methods=["POST"])
# def send_digest(user_id):
#     # Find user with this id
#     user = User.query.filter_by(id=user_id).first()

#     # Find events to fill digest email
#     events = Event.query.filter(Event.start_time.between("2019-01-01", "2019-01-31")).all()
#     links = []

#     for event in events:
#         links.append({
#             "name": event.name
#         })

#     categories = [{
#         "name": "Technology",
#         "links": links
#     }]

#     # Send email to user
#     send_email(Template.DIGEST, user.kerberos + "@mit.edu", {"categories": categories})

#     return ("", 204)

# @mod_users.route("/current", methods=["DELETE"])
# @login_required
# def logout():
#     logout_user()
#     return ("", 204)
