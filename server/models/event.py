from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.orm import deferred
from server.models import Base
from server.emails.parse_type import CATEGORIES
from server.helpers import *
import datetime
import secrets


class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True,
                unique=True, autoincrement=True)

    # User that claims the event (can be only one!)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User")

    # Email header information
    header = Column(String, default="")
    club = Column(String, default="")

    # Event characteristics
    title = Column(String)
    location = Column(String, default="")
    description = deferred(Column(Text, default=""))
    description_html = deferred(Column(Text, default=""))

    cta_link = Column(String)
    time_start = Column(DateTime)
    time_end = Column(DateTime)
    etype = Column(Integer, default=0)

    # Published and approved?
    published_is = Column(Boolean, default=False)
    approved_is = Column(Boolean, default=False)

    # Parent events
    parent_event_is = Column(Boolean)
    parent_event_id = Column(Integer, ForeignKey("events.id"))
    parent_event = relationship("Event", remote_side=[id])

    # Unique event id
    eid = Column(String, unique=True)

    # Unique event authstring
    token = Column(String)

    date_created = Column(DateTime, default=datetime.datetime.now)
    date_updated = Column(DateTime, default=datetime.datetime.now)

    def __init__(self, user=None):
        self.user = user
        self.generateUniques()

    def generateUniques(self):
        self.eid = random_number_string(10)
        self.token = random_id_string(6)

    # Client side
    # type Event = {
    #   start: Date;
    #   end: Date;
    #   title: string;
    #   type: number;
    #   desc: string;
    # };
    def json(self, fullJSON=2):
        additionalJSON = {}
        if (fullJSON == 2):
            additionalJSON = {
                'desc': self.description,
                'desc_html': self.description_html
            }
        elif (fullJSON == 1):
            additionalJSON = {
                'desc': self.description[:100] + "..." if self.description else ""
            }


        return {
            'title': self.title,
            'start': self.time_start.isoformat() + "Z",
            'end': self.time_end.isoformat() + "Z",
            'location': self.location,
            'type': self.etype,
            'eid': self.eid,
            'link': self.cta_link,
            'approved': self.approved_is,
            'published': self.published_is,
            'header': self.header,
            'id': self.id,
            **additionalJSON
        }

    def serialize(self):
        global CATEGORIES
        cats = []
        for key in CATEGORIES:
            val, _, data = CATEGORIES[key]
            if self.etype & val > 0:
                cats.append(data['name'])
        return {
            "uid": self.eid,
            "name": self.title,
            "location": self.location,
            "start_time": self.time_start.isoformat() + "Z",
            "end_time": self.time_end.isoformat() + "Z",
            "host": "MIT", #TODO(kevinfang): Host not implemented
            "description": self.description_html if self.description_html else self.description,
            "description_text": self.description,
            "categories": "," + ",".join(cats) + ",",
            "sent_from": "Sent by: " + self.header.replace("|", " on ")
        }
