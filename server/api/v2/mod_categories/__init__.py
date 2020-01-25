from .models import Category
from app import db

preset_categories = [
    {
        "name": "Boba",
        "id": "boba",
        "description": "Mouthwatering, scrumptious goodness",
        "color": "#F6B957"
    },
    {
        "name": "Food",
        "id": "food",
        "description": "Breakfast, lunch, and dinner served",
        "color": "#EE6F6F"
    },
    {
        "name": "Tech",
        "id": "tech",
        "description": "Computer science, hackathons, and everything in between",
        "color": "#A16EE5"
    },
    {
        "name": "EECS-jobs-announce",
        "id": "eecs",
        "description": "All events from the EECS-jobs-announce mailing list",
        "color": "#5A56EF"
    },
    {
        "name": "Recruiting",
        "id": "recruiting",
        "description": "Recruiting events held by companies on campus",
        "color": "#459AF6"
    },
    {
        "name": "Social",
        "id": "social",
        "description": "Parties, karaoke nights, and food related outings",
        "color": "#25C8D3"
    },
    {
        "name": "Performance Groups",
        "id": "performance",
        "description": "Dance, music, a capella, and other concerts and performances",
        "color": "#12DAA4"
    },
    {
        "name": "Talks",
        "id": "talks",
        "description": "Talks and short classes about anything you can imagine!",
        "color": "#73F23A"
    }
]

def load_default_categories():
    if Category.query.first() is None:
        db.session.bulk_insert_mappings(Category, preset_categories)
        db.session.commit()
