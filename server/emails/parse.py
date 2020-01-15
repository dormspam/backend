import re
import email
from email import policy
import lxml
from lxml.html.clean import Cleaner

if __name__ == "__main__":
    from parse_dates import parse_dates
    from parse_urls import parse_urls
    from parse_type import parse_type
    from parse_location import parse_location

    def create_server_event(title, etype, description, time_start,
                                   message_html=None,
                                   location=None, 
                                   time_end=None, link=None, headerInfo=None):
        print("TITLE:", title)
        print("TYPE:", etype)
        open("test_email_output.html","w").write(message_html)
        print("LOCATION:", location)
        print("START:", time_start)
        print(time_end)
else:
    from server.emails.parse_dates import parse_dates
    from server.emails.parse_urls import parse_urls
    from server.emails.parse_type import parse_type
    from server.emails.parse_location import parse_location
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

def clean_and_update_html(html, images):
    cleaner = Cleaner()
    cleaner.javascript = True
    html = lxml.html.tostring(cleaner.clean_html(lxml.html.fragment_fromstring(html)), method='html', encoding='unicode',
                  doctype='<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"'
                          ' "http://www.w3.org/TR/html4/strict.dtd">')
    # forwarding
    if "\n\n\n\n" in html:
        html = re.split("\n\n\n\n",html, 1, re.I)[1]

    block = re.findall("<img[^<]*src[^<]*>", html)
    for answer in block:
        start_quote = answer.index("src=")
        indices = [] #start/end indices of the link
        for i in range(start_quote, len(answer)):
            if (answer[i] == '"'):
                indices.append(i)
        website = answer[indices[0]+1:indices[1]]
        if "cid:" in website:
            # Attachment!
            cid = website.split(":")[1]
            if (cid in images):
                html = html.replace(website, f"data:{images[cid].get_content_type()};base64,{images[cid].get_payload()}")
            else:
                html = html.replace(website, '')
        elif 'http' not in website:
            html = html.replace(answer, '')

    return html

def parse_email(email_text):
    b = email.message_from_string(email_text, policy=policy.default)
    def find_plain_txt(p):
        message_body = b""
        if p.is_multipart():
            for payload in p.get_payload():
                message_body += find_plain_txt(payload)
        elif (p.get_content_type() == "text/plain"):
            message_body += p.get_payload(decode=True)
        return message_body

    def find_html_txt(p):
        message_body = b""
        if p.is_multipart():
            for payload in p.get_payload():
                message_body += find_html_txt(payload)
        elif (p.get_content_type() == "text/html"):
            message_body += p.get_payload(decode=True)
        return message_body
    
    def find_images(p):
        images = {}
        for payload in p.walk():
            if (payload.get_content_maintype() == "image"):
                images[payload.get("Content-ID").replace("<","").replace(">","")] = payload
        return images

    message_body = find_plain_txt(b)
    html_message = clean_and_update_html(find_html_txt(b).decode("utf-8", "ignore"), find_images(b))
    message_clean = remove_forwards(message_body.decode("utf-8", "ignore"))

    remove_strings = ["Fwd: ", "Re: ", "[Castle-Talk]", "BAKER-FORUM: ", "Cc: ", "RE: ", "FW: ", "[TONIGHT] ", "[TOMORROW] ", "[HAPPENING NOW] ", "[ACTION REQUIRED] ",
                     "[TODAY] ", "Bump: ", "Action Required: ", "Reminder: ", " next week", " today",
                     " this week", " this Monday", " this Tuesday", " this Wednesday", " this Thursday",
                     " this Friday", " this Saturday", "this Sunday"]

    messy_title = b.get("subject").replace("\n", "")
    title = messy_title
    for rs in remove_strings:
        title = title.replace(rs, "")
    title = title.strip()
    print("Parsing email:", title)
    etype = parse_type(message_clean)
    location = parse_location(message_clean)
    # use precleaned data for date extraction
    dates = parse_dates(messy_title + "\n" + message_clean)
    if not dates and ((etype & (1 << 5)) > 0):
        dates = parse_dates(messy_title + "\n" + message_clean,
                        time_required=False)
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
    # dates that are nonexistant are automatically not created
    if date_start is not None:
        return create_server_event(title,
                                   etype,
                                   message_clean,
                                   date_start,
                                   message_html=html_message,
                                   location=location,
                                   time_end=date_end,
                                   link=urls,
                                   headerInfo=header
                                   )
    else:
        print("Could not classify event or determine time", etype, date_start)
    return None


if __name__ == "__main__":
    f = open("test_email", "r")
    parse_email(f.read())
