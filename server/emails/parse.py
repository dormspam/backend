import email
if __name__ == "__main__":
    from parse_dates import parse_dates
    from parse_urls import parse_urls
    from parse_type import parse_type
    def  create_server_event (title, etype, descrition, time_start, time_end=None, link=None, headerInfo=None):
        print(title)
        print(etype)
        print(descrition)
        print(time_start)
        print(time_end)
else:
    from server.emails.parse_dates import parse_dates
    from server.emails.parse_urls import parse_urls
    from server.emails.parse_type import parse_type
    from server.controllers.events import create_server_event

import re


def remove_forwards(text):
    if "-----" in text and "From:" in text and "Subject:" in text:
        # Forwarded message
        texts = re.split(r'\r?\n\r?\n', text, 1, re.I)
        return texts[1]
    return text


def parse_email(email_text):
    b = email.message_from_string(email_text)
    def find_plain_txt(p):
        message_body = b""
        if p.is_multipart():
            for payload in p.get_payload():
                if (payload.is_multipart()):
                    message_body += find_plain_txt(payload)
                else:
                    if (payload.get_content_type() == "text/plain"):
                        message_body += payload.get_payload(decode=True)

        else:
            if (p.get_content_type() == "text/plain"):
                message_body += p.get_payload(decode=True)
        return message_body
    
    message_body = find_plain_txt(b)
    message_clean = remove_forwards(message_body.decode("utf-8"))

    title = b.get("subject").replace("Fwd: ","").replace("Re: ","")
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
                        message_clean,
                        date_start,
                        time_end=date_end,
                        link=urls,
                        headerInfo=header
                        )
    return None

if __name__ == "__main__":
    f = open("test_email","r")
    parse_email(f.read())