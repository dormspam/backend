import React, { useState, useEffect } from "react";
import {
  Container,
  Button,
  Card,
  CardBody,
  CardTitle,
  Input,
  Badge,
  Row
} from "reactstrap";
import useLogin from "../hooks/useLogin";
import ServerHelper, { ServerURL } from "./ServerHelper";
import createAlert, { AlertType } from "./Alert";
import { Event, EventString } from "./CalendarPage";
// TODO(kevinfang): Upgrade to react-table v7
import ReactTable from "react-table-6";
import "react-table-6/react-table.css";

const AdminPage = () => {
  const { getCredentials } = useLogin();
  const [events, setEvents] = useState<Event[]>([]);
  const [filteredEvents, setFilteredEvents] = useState<Event[]>([]);
  const [searchValue, setSearchValue] = useState("");
  const columns = [
    {
      Header: "Title",
      accessor: "title",
      Cell: (row: { original: { eid: string }; value: string }) => (
        <a href={`/event/${row.original.eid}`}>{row.value}</a>
      )
    },
    {
      Header: "Start Date",
      accessor: "start",
      width: 400,
      Cell: (row: { original: { id: string }; value: Date }) => (
        <>{row.value.toDateString()} @{row.value.toLocaleTimeString()}</>
      )
    },
    {
      Header: "Published",
      accessor: "published",
      width: 100,
      Cell: (row: { original: { id: string }; value: boolean }) => (
        <>{row.value ? "PUBLISHED" : ""}</>
      )
    },
    {
      Header: "Approved",
      accessor: "approved",
      width: 100,
      Cell: (row: { original: { id: string }; value: boolean }) => (
        <>{row.value ? "APPROVED" : ""}</>
      )
    }
  ];
  const getData = async () => {
    const res = await ServerHelper.post(
      ServerURL.getAllEvents,
      getCredentials()
    );
    if (res.success) {
      setEvents(
        res.events.map((e: EventString) => {
          return {
            ...e,
            start: new Date(e.start),
            end: new Date(e.end)
          };
        })
      );
    } else {
      createAlert(
        AlertType.Error,
        "Failed to get admin data, are you logged in?"
      );
    }
  };
  useEffect(() => {
    getData();
  }, []);

  useEffect(() => {
    if (searchValue.length === 0) {
      setFilteredEvents(events);
    } else {
      const value = searchValue.toLowerCase();
      // Searchable content
      setFilteredEvents(
        events.filter(
          (obj: Event) =>
            obj.title.toLowerCase().includes(value) ||
            obj.desc.toLowerCase().includes(value) ||
            obj.header.toLowerCase().includes(value)
        )
      );
    }
  }, [events]);

  return (
    <div className="m-4">
      <Card>
        <CardBody>
          <CardTitle>
            <h2>Events</h2>
            {new Date().getTimezoneOffset() / 60 != 5 ? (
              <span>
                <Badge color="danger">NOT IN EASTERN TIME</Badge>
              </span>
            ) : null}
          </CardTitle>
          <Input
            placeholder="search"
            value={searchValue}
            onChange={e => setSearchValue(e.target.value)}
          />
          <ReactTable data={filteredEvents} columns={columns} />
        </CardBody>
      </Card>
    </div>
  );
};

export default AdminPage;
