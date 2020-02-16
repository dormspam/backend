from dateparser.search import search_dates
import re
import calendar
import datetime
from pytz import timezone
from datetime import timedelta
from dateutil import tz

def expand_event_time(text):
    text = text.encode('ascii', 'ignore').decode('ascii')
    # remmove pipelines
    text = re.sub(r'\|', "", text)
    text = re.sub(r"[\[\]\<\>\*\.\,]", " .", text) # Remove stars and punctuation

    # Remove room numbers
    text = re.sub(r"[A-Z0-9]+-[0-9][0-9][0-9]","", text)
    text = re.sub(r"32-G[0-9][0-9][0-9]","", text)
    text = re.sub(r"32-D[0-9][0-9][0-9]","", text)
    text = re.sub(r"LOBBY (1[03]|7)","", text)
    text = re.sub(r"YEARS?", "", text)
    # Remove all greator than 3 numbers
    text = re.sub(r"[0-9]{3,}", "number", text)

    now = datetime.datetime.now()

    # move dates closer to month and force the year to be correct
    for month in calendar.month_name[1:]:
        text = re.sub('{month}\s+'.format(month=month),
                     str(now.year) + " " + month, text, flags=re.IGNORECASE)
        text = re.sub(
            '{month}\s+'.format(month=month[:3]), str(now.year) + " " + month, text, flags=re.IGNORECASE)

    text = re.sub(r"(-?)NOON(-?)", r"\1 12 PM \2", text)
    # crazy specific 10-4 pm edge case
    text = re.sub(r'(9|10|11|12)-([1-5])\s*(pm)',
                  r'\1AM - \2\3', text, flags=re.IGNORECASE)
    # 1 to 3 pm
    text = re.sub(r'(10|11|12|[1-9])\s*(?:to)\s*(10|11|12|[1-9])\s*([ap][m])',
                  r'\1\3 - \2\3', text, flags=re.IGNORECASE)
    # 1-3 pm
    text = re.sub(r'((?:10|11|12|[1-9])(?:\:[0-9]{2})?)\s*-\s*((?:10|11|12|[1-9])(?:\:[0-9]{2})?)\s*([ap][m])',
                  r'\1\3 - \2\3', text, flags=re.IGNORECASE)

    # 1pm-2pm
    text = re.sub(r'((?:10|11|12|[1-9])(?:\:[0-9]{2})?)\s*([ap][m])\s*-\s*((?:10|11|12|[1-9])(?:\:[0-9]{2})?)\s*([ap][m])',
                  r'\1\2 - \3\4', text, flags=re.IGNORECASE)

    # merge ams and pms spaces
    text = re.sub(
        r'((?:10|11|12|[1-9])(?:\:[0-9]{2})?)\s+([ap]m)', r'\1\2', text, flags=re.I)

    # Add minutes
    text = re.sub(r'(10|11|12|[1-9])([ap]m)', r'\1:00\2', text, flags=re.I)
    text = re.sub(r'\n', '.', text)

    return text


def parse_dates(text, time_required=True):
    test_strings = ["AM", "PM", "NOON", "NIGHT"]
    matches = parse_dates_possibilities(text)
    print(matches)
    # Now we need to find the actual dates
    if not matches:
        return None
    # Start by looking forwards and finding the first one with an AM or PM
    i = 0
    start_date = None
    set_time = False
    while i < len(matches):
        matched_string, potential_date = matches[i]
        if (not time_required):
            # Must be a valid full month
            for month in calendar.month_name[1:]:
                if month.lower() in matched_string.lower():
                    start_date = potential_date
                    break
        if (any([t in matched_string for t in test_strings])):
            if start_date:
                return [start_date, potential_date]
            else:
                start_date = potential_date
        i += 1
    if not time_required and start_date:
        if (start_date.replace(tzinfo=tz.gettz('UTC')).astimezone(tz.gettz('US/Eastern')).hour == 0):
            return [start_date, start_date + timedelta(hours=24)]
        else:
            return [start_date]
    if time_required and start_date:
        return [start_date]
    return None


def parse_dates_possibilities(text):
    text = expand_event_time(text.upper())
    try:
        matches = search_dates(text, languages=['en'], settings={'TIMEZONE': 'US/Eastern', 'TO_TIMEZONE': 'UTC'})
    except:
        print("search dates errored out")
        matches = None
    return matches

if __name__ == "__main__":
    f = open("test_dates.txt", "r")
    for l in f.readlines():
        print(l.strip())
        print(parse_dates_possibilities(l.strip()))
        print(parse_dates(l.strip()))
