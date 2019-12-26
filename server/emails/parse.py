import email
from server.emails.parse_dates import parse_dates
from server.emails.parse_urls import parse_urls
from server.emails.parse_type import parse_type
from server.controllers.events import create_server_event
import re


def remove_tags(text):
    TAG_RE = re.compile(r'<[^>]+>')
    return TAG_RE.sub('', text)


def parse_email(email_text):
    b = email.message_from_string(email_text)
    message_body = b""
    if b.is_multipart():
        for payload in b.get_payload():
            # if payload.is_multipart(): ...
            message_body += payload.get_payload(decode=True)
            break
            # TODO(kevinfang): only looking at first MIME part
    else:
        message_body += (b.get_payload(decode=True))

    message_clean = remove_tags(message_body.decode("utf-8"))

    title = b.get("subject")
    dates = parse_dates(message_clean)
    urls = parse_urls(message_clean)
    etype = parse_type(message_clean)
    header = b.get("from") + "|" + b.get("date")

    if dates:
        date_start = dates[0]
    else:
        date_start = None
    if dates and len(dates) > 1:
        date_end = dates[1]
    else:
        date_end = None
    if etype > 0:
        return create_server_event(title,
                        etype,
                        message_body.decode("utf-8"),
                        date_start,
                        time_end=date_end,
                        link=urls,
                        headerInfo=header
                        )
    return None
