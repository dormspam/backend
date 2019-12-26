import React, { useState, useEffect } from "react";
import { Calendar, momentLocalizer } from "react-big-calendar";
import moment from "moment";
import "react-big-calendar/lib/css/react-big-calendar.css";
import {
  Container,
  Button,
  Row,
  Col,
  Card,
  CardTitle,
  CardText,
  Dropdown,
  DropdownToggle,
  DropdownMenu,
  DropdownItem,
  Badge
} from "reactstrap";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faCircle } from "@fortawesome/free-solid-svg-icons";
import ServerHelper, { ServerURL } from "./ServerHelper";
import createAlert, { AlertType } from "./Alert";
import useLogin from "../hooks/useLogin";

// Also update parse_type.py
enum SortType {
  ALL = 0,
  FUNDRAISING = 1 << 1,
  FOOD = 1 << 2,
  CAREER = 1 << 3,
  CLUB = 1 << 4,
  APPLICATION = 1 << 5,
  PERFORMANCE = 1 << 6
}
const SortTypeValues = [
  { type: SortType.ALL, name: "All Events", color: null },
  { type: SortType.FUNDRAISING, name: "Fundraising", color: "lightblue" },
  { type: SortType.FOOD, name: "Food", color: "green" },
  { type: SortType.CAREER, name: "Career", color: "orange" },
  { type: SortType.CLUB, name: "Club Events", color: "purple" },
  { type: SortType.APPLICATION, name: "Application Deadlines", color: "gold" },
  { type: SortType.PERFORMANCE, name: "Performance", color: "pink" }
];

type SortTypeObj = {
  type: SortType;
  name: string;
  color: string | null;
};

const getObject = (t: number) => {
  let ret: SortTypeObj = {
    type: SortType.ALL,
    name: "All Events",
    color: null
  };
  SortTypeValues.forEach(function(val) {
    if (val.type & t) {
      ret = val;
    }
  });
  return ret;
};

const getColors = (t: number) => {
  let ret = SortTypeValues.map(function(val) {
    const color = val.color;
    if (color == null) {
      return null;
    }
    if (val.type & t) {
      return (
        <FontAwesomeIcon
          key={val.type}
          className="mx-2"
          icon={faCircle}
          color={color}
        />
      );
    }
  });
  return ret;
};

export const getColorNames = (t: number) => {
  let ret = SortTypeValues.map(function(val) {
    const color = val.color;
    if (color == null) {
      return null;
    }
    if (val.type & t) {
      return (
        <Badge key={val.type} className="mx-2" 
        style={{backgroundColor:color}}>
          {val.name}
        </Badge>
      );
    }
  });
  return ret;
};

type EventString = {
  start: string;
  end: string;
  title: string;
  type: number;
  desc: string;
};
export type Event = {
  start: Date;
  end: Date;
  title: string;
  type: number;
  desc: string;
  link: string;
  approved: string;
};

const CalendarPage = () => {
  const { getCredentials } = useLogin();
  const localizer = momentLocalizer(moment);
  const [allEvents, setAllEvents] = useState<Event[]>([]);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [sortType, setSortType] = useState(getObject(SortType.ALL));
  const [selectedEvent, setSelectedEvent] = useState<null | Event>(null);
  const [events, setEvents] = useState<Event[]>([]);

  const getEvents = async () => {
    const res = await ServerHelper.post(ServerURL.getEvents, {});
    if (res.success) {
      setAllEvents(
        res.events.map((e: EventString) => {
          return {
            ...e,
            start: new Date(e.start),
            end: new Date(e.end)
          };
        })
      );
    } else {
      setAllEvents([]);
    }
  };

  useEffect(() => {
    setEvents(
      allEvents.filter(
        event => event.type == sortType.type || sortType.type == SortType.ALL
      )
    );
    console.log(allEvents);
  }, [sortType, allEvents]);

  useEffect(() => {
    getEvents();
  }, []);

  return (
    <>
      <Container className="mb-4">
        {/* <Button>Create Event</Button>
        <Button>Edit Your Events</Button> TODO(kevinfang): add these options*/}
      </Container>
      <Row className="m-1">
        <Col xl="6">
          <Card body>
            <CardTitle>
              <h1>Events</h1>
              <Dropdown
                isOpen={isDropdownOpen}
                toggle={() => setIsDropdownOpen(d => !d)}
              >
                <DropdownToggle
                  caret
                  style={{ backgroundColor: sortType.color || "" }}
                >
                  Sorting by: {sortType.name}
                </DropdownToggle>
                <DropdownMenu>
                  <DropdownItem header>Sort by:</DropdownItem>
                  {SortTypeValues.map(val => {
                    const color = val.color;
                    return (
                      <DropdownItem
                        key={val.type}
                        onClick={() => setSortType(val)}
                      >
                        {getColors(val.type)}
                        {val.name}
                      </DropdownItem>
                    );
                  })}
                </DropdownMenu>
              </Dropdown>
              {selectedEvent ? (
                <Card body className="m-2">
                  <CardTitle>
                    {selectedEvent.title}
                    {getColorNames(selectedEvent.type)}
                  </CardTitle>
                  <h4>
                    {selectedEvent.start.toDateString()} @{" "}
                    {selectedEvent.start.toLocaleTimeString()}
                  </h4>
                  <code style={{ whiteSpace: "pre-wrap" }}>
                    {selectedEvent.desc}
                  </code>
                </Card>
              ) : null}
            </CardTitle>
          </Card>
        </Col>
        <Col xl="6">
          <Calendar
            popup
            localizer={localizer}
            defaultDate={new Date()}
            defaultView="month"
            events={events}
            className="calendar"
            onSelectEvent={e => setSelectedEvent(e)}
            components={{
              event: e => {
                return (
                  <span>
                    {e.event.title}
                    {getColors(e.event.type)}
                  </span>
                );
              }
            }}
          />
        </Col>
      </Row>
    </>
  );
};

export default CalendarPage;
