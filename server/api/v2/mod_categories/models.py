from app import db

class Category(db.Model):

    __tablename__ = "categories"

    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String)
    color = db.Column(db.String)

    def serialize(self):
        return {
            "name": self.name,
            "id": self.id,
            "description": self.description,
            "color": self.color
        }
