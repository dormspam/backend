import React, { useState, useEffect, Fragment } from "react";
import {
  Container,
  Button,
  Card,
  Row,
  Col,
  Input,
  InputGroup,
  InputGroupAddon,
  Badge,
  CardBody,
  Label,
  FormGroup
} from "reactstrap";
import useLogin from "../hooks/useLogin";
import ServerHelper, { ServerURL } from "./ServerHelper";
import { RouteComponentProps } from "react-router";
import { Event, getColorNames } from "./CalendarPage";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import useViewer, { Query } from "../hooks/useViewer";
import createAlert, { AlertType } from "./Alert";
import moment from "moment";

interface Callback {
  eid: string;
  token: string;
}

const EventPage = (props: RouteComponentProps<Callback>) => {
  const search = new URLSearchParams(props.location.search);
  const etoken = search.get("etoken");
  const { getCredentials, redirectToDopeAuth } = useLogin();
  const { isLoggedIn, viewer } = useViewer();
  const [event, setEvent] = useState<Event | null>(null);
  const [eventTitle, setEventTitle] = useState("");
  const [eventStart, setEventStart] = useState<Date | null>(new Date());
  const [eventEnd, setEventEnd] = useState<Date | null>(new Date());
  const [eventDesc, setEventDesc] = useState("");
  const [eventLink, setEventLink] = useState("");
  const [eventRoom, setEventRoom] = useState("");
  const [eventType, setEventType] = useState(0);
  const [eventDupStart, setEventDupStart] = useState(new Date());
  const [eventDupEnd, setEventDupEnd] = useState(new Date());
  const [eventDupLocation, setEventDupLocation] = useState("");

  const getEvent = async () => {
    const res = await ServerHelper.post(ServerURL.getEvent, {
      ...getCredentials(),
      eid: props.match.params.eid
    });
    if (res.success) {
      setEvent({
        ...res.event,
        start: new Date(res.event.start),
        end: new Date(res.event.end)
      });
    } else {
      setEvent(null);
      createAlert(AlertType.Error, "Could not load event");
    }
  };
  useEffect(() => {
    getEvent();
  }, []);
  useEffect(() => {
    if (event != null) {
      setEventTitle(event.title);
      setEventStart(event.start);
      setEventEnd(event.end);
      setEventLink(event.link);
      setEventDesc(event.desc);
      setEventType(event.type);
      setEventRoom(event.location);
    }
  }, [event]);
  if (!isLoggedIn) {
    return (
      <Container>
        <h1>You need to log in to edit this event</h1>
        <br />
        <Button
          onClick={() =>
            redirectToDopeAuth([
              ["eid", props.match.params.eid],
              ["etoken", etoken || ""]
            ])
          }
          color="primary"
          size="lg"
        >
          Login with email
        </Button>
      </Container>
    );
  }
  if (event == null) {
    return <p>Loading event...</p>;
  }
  return (
    <div className="m-4">
      <Row>
        <Col lg="12" xl="6">
          <Card body>
            <h3>{event.title}</h3>
            <h5>
              {event.start.toDateString()} @ {event.start.toLocaleTimeString()}
            </h5>
            <p> Type: {getColorNames(event.type)} </p>
            <Button href={event.link}>Link: {event.link}</Button>
            <br />
            <div dangerouslySetInnerHTML={{ __html: event.desc_html }} />
            <code style={{ whiteSpace: "pre-wrap" }}>{event.desc}</code>
          </Card>
        </Col>
        <Col lg="12" xl="6">
          <Card body>
            {viewer(Query.admin) === "true" ||
            (etoken != null && etoken.length > 0) ? (
              <>
                <h2>
                  Proposed{" "}
                  {event.parent_id != 0 ? (
                    <Button href={"/event/" + event.parent_id} color="warning">
                      Goto Parent Event
                    </Button>
                  ) : null}
                </h2>
                <p>
                  This email was sent by: {event.header.split("|")[0]} on{" "}
                  {moment(new Date(event.header.split("|")[1])).format(
                    "MMMM D, YYYY h:mmA"
                  )}
                </p>
                <Row>
                  <Col>
                    <InputGroup>
                      <InputGroupAddon addonType="prepend">
                        Event Title:
                      </InputGroupAddon>
                      <Input
                        value={eventTitle}
                        onChange={e => setEventTitle(e.target.value)}
                      />
                    </InputGroup>
                    <InputGroup>
                      <DatePicker
                        selected={eventStart}
                        onChange={date => setEventStart(date)}
                        selectsStart
                        showTimeSelect
                        startDate={eventStart}
                        endDate={eventEnd}
                        timeFormat="h:mm aa"
                        timeIntervals={30}
                        timeCaption="time"
                        dateFormat="M/d/yy h:mm aa"
                        className="form-control"
                      />
                      <DatePicker
                        selected={eventEnd}
                        onChange={date => setEventEnd(date)}
                        showTimeSelect
                        selectsEnd
                        startDate={eventStart}
                        endDate={eventEnd}
                        timeFormat="h:mm aa"
                        timeIntervals={30}
                        timeCaption="time"
                        dateFormat="M/d/yy h:mm aa"
                        className="form-control"
                      />
                      {new Date().getTimezoneOffset() / 60 != 5 ? (
                        <span>
                          <Badge color="danger">NOT IN EASTERN TIME</Badge>
                        </span>
                      ) : null}
                    </InputGroup>
                    <InputGroup>
                      <InputGroupAddon addonType="prepend">
                        Link:
                      </InputGroupAddon>
                      <Input
                        value={eventLink}
                        onChange={e => setEventLink(e.target.value)}
                      />
                    </InputGroup>
                    <InputGroup>
                      <InputGroupAddon addonType="prepend">
                        Room:
                      </InputGroupAddon>
                      <Input
                        value={eventRoom}
                        onChange={e => setEventRoom(e.target.value)}
                      />
                    </InputGroup>
                  </Col>
                  <Col>
                    <Button
                      color="primary"
                      size="lg"
                      onClick={async () => {
                        const res = await ServerHelper.post(
                          ServerURL.publishEvent,
                          {
                            ...getCredentials(),
                            eid: props.match.params.eid,
                            etoken: etoken || "",
                            title: eventTitle,
                            description: eventDesc,
                            etype: "" + eventType,
                            link: eventLink,
                            location: eventRoom,
                            start_date: eventStart && eventStart.toISOString(),
                            end_date: eventEnd && eventEnd.toISOString()
                          }
                        );
                        if (res.success) {
                          getEvent();
                          createAlert(AlertType.Success, "Published!");
                        } else {
                          createAlert(AlertType.Error, "Could not publish");
                        }
                      }}
                    >
                      {event.published ? "Update Event" : "Confirm Event"}
                    </Button>
                    <br />
                    {viewer(Query.admin) === "true" ? (
                      <Button
                        size="lg"
                        onClick={async () => {
                          const res = await ServerHelper.post(
                            ServerURL.approveEvent,
                            {
                              ...getCredentials(),
                              eid: props.match.params.eid
                            }
                          );
                          if (res.success) {
                            getEvent();
                            createAlert(AlertType.Success, "Toggled Approval");
                          } else {
                            createAlert(AlertType.Error, "Could not approve");
                          }
                        }}
                        color={event.approved ? "success" : "primary"}
                      >
                        (Admin) {event.approved ? "Unapprove" : "Approve"}
                      </Button>
                    ) : null}
                  </Col>
                </Row>
              </>
            ) : (
              <h2>You need to have the correct link to edit this event</h2>
            )}
            <br />
            {viewer(Query.admin) === "true" && event.parent_id == 0 ? (
              <Fragment>
                Duplicated Events:
                <Row>
                  {event.alternate_events.map((e, i) => {
                    return (
                      <Fragment key={e.start.toString() + " dd" + i}>
                        <Button href={"/event/" + e.eid} color="info">
                          {moment(e.start).format("M/D/YY h:mmA")} to{" "}
                          {moment(e.end).format("h:mmA")} @ {e.location}
                        </Button>
                      </Fragment>
                    );
                  })}
                </Row>
                <br />
                <Button
                  onClick={async () => {
                    if (window.confirm("Are you sure?")) {
                      const res = await ServerHelper.post(
                        ServerURL.duplicateEvent,
                        {
                          ...getCredentials(),
                          eid: props.match.params.eid,
                          location: eventDupLocation,
                          start_date:
                            eventDupStart && eventDupStart.toISOString(),
                          end_date: eventDupEnd && eventDupEnd.toISOString()
                        }
                      );
                      if (res.success) {
                        getEvent();
                        createAlert(AlertType.Success, "Duplicated Event");
                      } else {
                        createAlert(AlertType.Error, "Could not duplicate");
                      }
                    }
                  }}
                >
                  Dup
                </Button>
                <p>
                  start:{" "}
                  <b>{moment(eventDupStart).format("dddd M/D/YY h:mmA")}</b> to{" "}
                  <b>{moment(eventDupEnd).format("dddd M/D/YY h:mmA")}</b> @{" "}
                  <b>{eventDupLocation.toString()}</b> <br />
                  <DatePicker
                    selected={eventDupStart}
                    onChange={date =>
                      setEventDupStart(date ? date : eventDupStart)
                    }
                    selectsStart
                    showTimeSelect
                    startDate={eventDupStart}
                    endDate={eventDupEnd}
                    timeFormat="h:mm aa"
                    timeIntervals={30}
                    timeCaption="time"
                    dateFormat="M/d/yy h:mm aa"
                    className="form-control"
                  />
                  <DatePicker
                    selected={eventDupEnd}
                    onChange={date => setEventDupEnd(date ? date : eventDupEnd)}
                    showTimeSelect
                    selectsEnd
                    startDate={eventDupStart}
                    endDate={eventDupEnd}
                    timeFormat="h:mm aa"
                    timeIntervals={30}
                    timeCaption="time"
                    dateFormat="M/d/yy h:mm aa"
                    className="form-control"
                  />
                </p>
                <Row className="m-2">
                  <Col>
                    Start Date
                    {event.alternate_dates.map((e, i) => {
                      return (
                        <Fragment key={e[1] + " " + i}>
                          <FormGroup check>
                            <Label check>
                              <Input
                                type="radio"
                                name="alternative_date_start"
                                onChange={r => setEventDupStart(new Date(e[1]))}
                              />
                              {e[0]}{" "}
                              {moment(new Date(e[1])).format("M/D/YY h:mmA")}
                            </Label>
                          </FormGroup>
                        </Fragment>
                      );
                    })}
                  </Col>
                  <Col>
                    End Date
                    {event.alternate_dates.map((e, i) => {
                      return (
                        <Fragment key={e[1] + " m" + i}>
                          <FormGroup check>
                            <Label check>
                              <Input
                                type="radio"
                                name="alternative_date_end"
                                onChange={r => setEventDupEnd(new Date(e[1]))}
                              />
                              {moment(new Date(e[1])).format("M/D/YY h:mmA")}
                            </Label>
                          </FormGroup>
                        </Fragment>
                      );
                    })}
                  </Col>
                  <Col>
                    Location
                    {event.alternate_location.map((e, i) => {
                      return (
                        <Fragment key={e + " " + i}>
                          <FormGroup check>
                            <Label check>
                              <Input
                                type="radio"
                                name="alternative_location"
                                onChange={r => setEventDupLocation(e.trim())}
                              />
                              {e}
                            </Label>
                          </FormGroup>
                        </Fragment>
                      );
                    })}
                  </Col>
                </Row>
              </Fragment>
            ) : null}
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default EventPage;
