from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from server.models import Base
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

    # Event characteristics
    title = Column(String)
    description = Column(Text, default="")
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
    def json(self):
        return {
            'title': self.title,
            'desc': self.description,
            'start': self.time_start.isoformat(),
            'end': self.time_end.isoformat(), # TODO(kevinfang): ISO UTC
            'type': self.etype,
            'eid': self.eid,
            'link': self.cta_link
        }