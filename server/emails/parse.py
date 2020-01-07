import re
import email
if __name__ == "__main__":
    from parse_dates import parse_dates
    from parse_urls import parse_urls
    from parse_type import parse_type

    def create_server_event(title, etype, descrition, time_start, time_end=None, link=None, headerInfo=None):
        print(title)
        print(etype)
        # print(descrition)
        print(time_start)
        print(time_end)
else:
    from server.emails.parse_dates import parse_dates
    from server.emails.parse_urls import parse_urls
    from server.emails.parse_type import parse_type
    from server.controllers.events import create_server_event

def remove_forwards(text):
    # Remove masseeh talk
    if "______________" in text and "maseeh-talk mailing list" in text:
        text = re.split(r'_{8,}\r?\nmaseeh\-talk', text, 1, re.I)[0]

    # Remove baker forum
    if "______________" in text and "baker-forum mailing list" in text:
        text = re.split(r'_{8,}\r?\nbaker\-forum', text, 1, re.I)[0]

    while (("-----" in text or "____________" in text) and "From:" in text and "Subject:" in text):
        # Forwarded message
        text = re.split(r'\r?\n\r?\n', text.split("Subject:",maxsplit=1)[1], 1, re.I)[1]

    return text


def parse_email(email_text):
    b = email.message_from_string(email_text)

    def find_plain_txt(p):
        message_body = b""
        if p.is_multipart():
            for payload in p.get_payload():
                message_body += find_plain_txt(payload)
        elif (p.get_content_type() == "text/plain"):
            message_body += p.get_payload(decode=True)
        return message_body

    message_body = find_plain_txt(b)
    message_clean = remove_forwards(message_body.decode("utf-8", "ignore"))

    remove_strings = ["Fwd: ", "Re: ", "[Castle-Talk]", "BAKER-FORUM: "]
    title = b.get("subject")
    for rs in remove_strings:
        title = title.replace(rs, "")
    title = title.strip()
    print("Parsing email:", title)
    etype = parse_type(message_clean)
    dates = parse_dates(title + "\n" + message_clean,
                        time_required=not ((etype & (1 << 5)) > 0))
    urls = parse_urls(message_clean)
    header = b.get("from") + "|" + b.get("date")
    if dates:
        date_start = dates[0]
    else:
        date_start = None
    if dates and len(dates) > 1:
        date_end = dates[1]
    else:
        date_end = None
    if etype > 0 and date_start is not None:
        return create_server_event(title,
                                   etype,
                                   message_clean,
                                   date_start,
                                   time_end=date_end,
                                   link=urls,
                                   headerInfo=header
                                   )
    else:
        print("Could not classify event or determine time")
    return None


if __name__ == "__main__":
    f = open("test_email", "r")
    parse_email(f.read())
