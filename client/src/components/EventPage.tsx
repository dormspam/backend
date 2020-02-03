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
  CardBody
} from "reactstrap";
import useLogin from "../hooks/useLogin";
import ServerHelper, { ServerURL } from "./ServerHelper";
import { RouteComponentProps } from "react-router";
import { Event, getColorNames } from "./CalendarPage";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import useViewer, { Query } from "../hooks/useViewer";
import createAlert, { AlertType } from "./Alert";

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
  const [eventType, setEventType] = useState(0);

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
            <code style={{ whiteSpace: "pre-wrap" }}>{event.desc}</code>
          </Card>
        </Col>
        <Col lg="12" xl="6">
          <Card body>
            {viewer(Query.admin) === "true" ||
            (etoken != null && etoken.length > 0) ? (
              <>
                <h2>Proposed</h2>
            <p>This email was sent by: {event.header.split("|")[0]} on {new Date(event.header.split("|")[1]).toString()}</p>
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
                  <InputGroupAddon addonType="prepend">
                    Start End Time
                  </InputGroupAddon>
                  <DatePicker
                    selected={eventStart}
                    onChange={date => setEventStart(date)}
                    showTimeSelect
                    timeFormat="HH:mm"
                    timeIntervals={30}
                    timeCaption="time"
                    dateFormat="MMMM d, yyyy h:mm aa"
                    className="form-control"
                  />
                  <DatePicker
                    selected={eventEnd}
                    onChange={date => setEventEnd(date)}
                    showTimeSelect
                    timeFormat="HH:mm"
                    timeIntervals={30}
                    timeCaption="time"
                    dateFormat="MMMM d, yyyy h:mm aa"
                    className="form-control"
                  />
                  {new Date().getTimezoneOffset() / 60 != 5 ? (
                    <span>
                      <Badge color="danger">NOT IN EASTERN TIME</Badge>
                    </span>
                  ) : null}
                </InputGroup>
                <InputGroup>
                  <InputGroupAddon addonType="prepend">Link:</InputGroupAddon>
                  <Input
                    value={eventLink}
                    onChange={e => setEventLink(e.target.value)}
                  />
                </InputGroup>
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
              </>
            ) : (
              <h2>You need to have the correct link to edit this event</h2>
            )}
            <br />
            {viewer(Query.admin) === "true" ? (
              <Button
                onClick={async () => {
                  const res = await ServerHelper.post(ServerURL.approveEvent, {
                    ...getCredentials(),
                    eid: props.match.params.eid
                  });
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
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default EventPage;
