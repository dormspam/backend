from flask import abort, request
from functools import wraps
import json

from app import app

def lambda_only(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if request.json is None:
            abort(403)

        if "lambda_key" not in request.json:
            abort(403)

        if request.json["lambda_key"] != app.config["LAMBDA_KEY"]:
            abort(403)

        return func(*args, **kwargs)

    return decorated_view
