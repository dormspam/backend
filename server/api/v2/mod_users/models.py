from enum import Enum
from flask_login import UserMixin
import json

from app import db
from app.mod_categories import preset_categories

default_settings = {
    "filters": [c["id"] for c in preset_categories],
    "preferences": [c["id"] for c in preset_categories],
    "frequency": 1
}

class User(db.Model, UserMixin):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    kerberos = db.Column(db.String(8), nullable=False)
    login_code = db.Column(db.String(4), nullable=True)
    login_code_time = db.Column(db.DateTime, nullable=True)
    settings = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def __init__(self, kerberos):
        global default_settings

        self.kerberos = kerberos
        self.settings = json.dumps(default_settings)

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def get_settings(self):
        settings = {}

        try:
            settings = json.loads(self.settings)
        except:
            pass

        return settings

    def serialize(self, full=False):
        data = {
            "id": self.id,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

        if full:
            data["kerberos"] = self.kerberos
            data["settings"] = self.get_settings()

        return data
