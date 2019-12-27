import React from "react";
import { RouteComponentProps } from "react-router";
import useLogin from "../hooks/useLogin";
import useViewer from "../hooks/useViewer";

enum Status {
  start,
  loading,
  failed,
  succeed
}

const LoginCallback = (props: RouteComponentProps) => {
  const { isLoggedIn } = useViewer();
  const [loginStatus, setLoginStatus] = React.useState<Status>(
    isLoggedIn ? Status.succeed : Status.start
  );
  const search = new URLSearchParams(props.location.search);
  const { login } = useLogin();
  React.useEffect(() => {
    const id = search.get("uid");
    const token = search.get("token");
    const email = search.get("email");
    const etoken = search.get("etoken");
    const eid = search.get("eid");
    if (loginStatus === Status.succeed) {
      if (eid != null) {
        if (etoken == null) {
          window.location.replace(`/event/${eid}`);
        } else {
          window.location.replace(`/event/${eid}?etoken=${etoken}`);
        }
        return;
      }
      window.location.replace("/");
      return;
    }
    if (
      id != null &&
      token != null &&
      email != null &&
      loginStatus === Status.start
    ) {
      setLoginStatus(0);
      login(id, email, token).then((success: Boolean) => {
        setLoginStatus(success ? Status.succeed : Status.failed);
      });
    } else if (loginStatus === Status.start) {
      setLoginStatus(Status.failed);
    }
    // eslint-disable-next-line
  }, [loginStatus]);

  if (loginStatus === Status.start || loginStatus === Status.loading) {
    return <div>Attempting to login</div>;
  } else if (loginStatus === Status.succeed) {
    return <div>Successful Login</div>;
  } else {
    return <div>Login Failed</div>;
  }
};

export default LoginCallback;
