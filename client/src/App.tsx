import React, { Fragment } from "react";
import "./App.css";
import { CookiesProvider } from "react-cookie";
import { BrowserRouter as Router, Route, Switch } from "react-router-dom";

import AppHeader from "./AppHeader";
import LandingPage from "./components/LandingPage";
import LoginCallback from "./components/LoginCallback";

import Alert from "react-s-alert";

import "react-s-alert/dist/s-alert-default.css";
import "react-s-alert/dist/s-alert-css-effects/slide.css";
import CalendarPage from "./components/CalendarPage";
import EventPage from "./components/EventPage";

const App: React.FC = () => {
  document.title = process.env.REACT_APP_NAME || "";
  return (
    <Fragment>
      <Router>
        <CookiesProvider>
          <div className="App">
            <AppHeader />
            <Switch>
              <Route exact path="/login/auth" component={LoginCallback} />
              <Route path="/event/:eid/:token" component={EventPage} />
              <Route path="/event/:eid" component={EventPage} />
              <Route path="/login" component={LandingPage} />
              <Route path="/" component={CalendarPage} />
            </Switch>
          </div>
        </CookiesProvider>
      </Router>
      <Alert stack={{ limit: 3 }} />
    </Fragment>
  );
};

export default App;
