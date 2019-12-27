from server.app import app
import requests


def sendPublishEmail(email, eid, etoken):
    # Debug mode we don't actually send the email lol
    if (app.config["APP-DEV"]):
        print(f"{app.config['REACT_APP_SITEURL']}/event/{eid}?etoken={etoken}}")
        return
    return requests.post(
        "https://api.mailgun.net/v3/mail.tenxeng.com/messages",
        auth=("api", app.config['MAILGUN_API']),
        data={
            "from":
            "MIT Events <mailgun@mail.tenxeng.com>",
            "to": [email],
            "bcc": ["kevin21@mit.edu"],
            "reply-to": ["dorm-spam-announce@mit.edu"],
            "subject": "Trying to dormspam?",
            "template":
            "publish",
            "v:publishURL":
            f"{app.config['REACT_APP_SITEURL']}/event/{eid}?etoken={etoken}}"
        })
