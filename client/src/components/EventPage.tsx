import React, { useState, useEffect } from "react";
import { Container, Button } from "reactstrap";
import useLogin from "../hooks/useLogin";
import ServerHelper, { ServerURL } from "./ServerHelper";
import { RouteComponentProps } from "react-router";
import { Event, getColorNames } from "./CalendarPage";
import { ENETDOWN } from "constants";

interface Callback {
  eid: string;
  token: string;
}

const EventPage = (props: RouteComponentProps<Callback>) => {
  const { getCredentials } = useLogin();
  const [event, setEvent] = useState<Event | null>(null);

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
    }
  };
  useEffect(() => {
    getEvent();
  }, []);
  if (event == null) {
    return null;
  }
  return (
    <Container>
      <Button onClick={async () => {
        const res = await ServerHelper.post(ServerURL.approveEvent, {
          ...getCredentials(),
          eid: props.match.params.eid
        });
        if (res.success) {
          alert(res.message);
        }
      }
      } color="primary">
        {event.approved ? "Unapprove" : "Approve"}
      </Button>
      <h1>Event Title: {event.title}</h1>
      <h4>{event.start.toDateString()} @ {event.start.toLocaleTimeString()}</h4>
      <p> Type: {getColorNames(event.type)} </p>
      <Button href={event.link}>Link: {event.link}</Button>

      <br />

      <code style={{whiteSpace: "pre-wrap"}}>{event.desc}</code>

    </Container>
  );
};

export default EventPage;
