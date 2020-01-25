# from datetime import datetime
# from dateutil.parser import parse

# from server.app import db

# class Event(db.Model):

#     __tablename__ = "events"

#     uid = db.Column(db.String, primary_key=True)
#     name = db.Column(db.String)
#     location = db.Column(db.String)
#     start_time = db.Column(db.DateTime)
#     end_time = db.Column(db.DateTime)
#     host = db.Column(db.String)
#     description = db.Column(db.String)
#     description_text = db.Column(db.String)
#     categories = db.Column(db.String)
#     sent_from = db.Column(db.String)

#     def __init__(self, data):
#         self.uid = data["uid"]
#         self.name = data["name"]
#         self.location = data["location"]

#         try:
#             self.start_time = parse(data["start_time"])
#         except:
#             self.start_time = datetime.now()

#         try:
#             self.end_time = parse(data["end_time"])
#         except:
#             self.end_time = datetime.now()

#         self.host = data["host"]
#         self.description = data["description"]
#         self.description_text = data["description_text"]
#         self.categories = data["categories"]
#         self.sent_from = data["sent_from"]

#     def serialize(self):
#         return {
#             "uid": self.uid,
#             "name": self.name,
#             "location": self.location,
#             "start_time": self.start_time,
#             "end_time": self.end_time,
#             "host": self.host,
#             "description": self.description,
#             "description_text": self.description_text,
#             "categories": self.categories,
#             "sent_from": self.sent_from
#         }
