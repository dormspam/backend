from flask import Blueprint, jsonify

from app import db
from server.api.v2.mod_categories import Category

mod_categories = Blueprint("categories", __name__)

@mod_categories.route("", methods=["GET"])
def get_categories():
    categories = Category.query.all()
    return jsonify([category.serialize() for category in categories])
