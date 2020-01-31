"""
Extract a datetime from the body of an email.
get_datetime is the main export from this file.
"""
import re
import os
import sys
from datetime import datetime, date, timedelta
import pytz
from parse_dates import parse_dates

month_lookup = {
    'jan': 1,
    'feb': 2,
    'mar': 3,
    'apr': 4,
    'may': 5,
    'jun': 6,
    'jul': 7,
    'aug': 8,
    'sep': 9,
    'oct': 10,
    'nov': 11,
    'dec': 12
}


def join_regexes(regexes):
  """ Utility function, takes in a list of regexes and outputs their OR """
  result = r''
  for reg in regexes:
    result = result + '('
    result = result + reg
    result = result + ')|'
  return result[:-1]


def send_date_to_datetime(send_date):
  """ Send date in the database is a string, so make it a Python datetime """
  words = send_date.split(' ')
  day = words[1]
  month = month_lookup[words[2][:3].lower()]
  year = words[3]
  hour, minute = words[4].split(':')[:2]
  return datetime(int(year), int(month), int(day), int(hour), int(minute))

def utc(dt):
  """ Convert Eastern time to UTC """
  local_zone = pytz.timezone ("America/New_York")
  local_datetime = local_zone.localize(dt, is_dst=None)
  utc_datetime = local_datetime.astimezone(pytz.utc)
  return utc_datetime


def clean_chain(text):
  # Takes out stuff like "On date at time, so-and-so wrote..."
  regex = r'(\nOn .*? at .*? wrote:\n)|(From:.*?\nSent:.*?\nCc:.*?\n)'
  chain_re = re.compile(regex)
  match = re.search(chain_re, text)
  return re.sub(chain_re, '\n[CHAINTEXT]\n', text)

def abs_date_from_phrase(text):
    """
    Identify the first absolute date in text
    Returns ((month, day), start, end) or None
    Doesn't currently support British dates (e.g. '28 February')
    """
    dates = set()
    months = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september',
              'october', 'november', 'december', 'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 
              'aug', 'sep', 'sept', 'oct', 'nov', 'dec']

    if type(text) != type("asdf"):
     text = str(text, 'utf-8')
    for month in months:
        if month in ('february', 'feb'):
          day_range = r'(([1-2][0-9])|([1-9]))'
        elif month in ('september', 'sep', 'april', 'apr', 'june', 'jun', 'november', 'nov'):
          day_range = r'(([1-2][0-9])|([1-9])|(30))'
        else:
          day_range = day_range = r'(([1-2][0-9])|([1-9])|(3[01]))'
        regex = r'\b(' + month + r'.? |((0?[1-9]|10|11|12)[/]))(the )?' + day_range + r'(\b|st|nd|rd|th)'
        date_re = re.compile(regex)
        result = re.search(date_re, text.lower())
        if result:
          dates.add((get_date(result), result.start(0), result.end(0)))

    return list(dates)

def rel_date_from_phrase(text, send_date):
    """
    Identify the first relative date in the text
    Returns ((month, day), start, end) or None
    send_date fresh from the database
    uses regexes instead of normal substring matching for type uniformity
    """
    dates = set()

    sdt = send_date_to_datetime(send_date)
    today = re.search(r'today|tonight', text.lower())
    if today:
      dates.add(((sdt.month, sdt.day), today.start(0), today.end(0)))
    tomorrow = re.search('tomorrow', text.lower())
    if tomorrow:
      tmrw = sdt + timedelta(days=1)
      dates.add(((tmrw.month, tmrw.day), tomorrow.start(0), tomorrow.end(0)))

    return list(dates)

def get_date(match):
    """
    Convert from a raw regex match to a (month, day) object
    Returns (month, day)
    """
    text = match.group()
    split = [word for word in re.split(r'[ ./-]+', text) if word.lower() != 'the']
    raw_month = split[0]
    raw_day = re.sub(r'\D', '', split[1])
    try:
        month = int(raw_month) # This works if month is already in number form
    except:
        month = month_lookup[raw_month.lower()[:3]]
    day = int(raw_day)

    return month, day


def make_time_re():
  """ Make a union regex to identify times. """
  regex0 = r'(10|11|12|[1-9])([:.][0-5][0-9]) ?([ap].? ?m.?)' # e.g., 2:30 PM
  regex1 = r'(10|11|12|[1-9]) ?([ap].? ?m.?)' # e.g., 2 PM
  regex2 = r'(10|11|12|[1-9])([:.][0-5][0-9])' # e.g., 2:30
  noon = r'noon'
  return join_regexes([regex0, regex1, regex2, noon])


def time_from_phrase(text):
    """
    Identify the first time in text
    Returns ()
    Doesn't currently support written out times like "six o'clock"
    Also doesn't support military (24-hour) time
    """
    regex0 = r'(10|11|12|[1-9])([:.][0-5][0-9]) ?([ap].? ?m.?)' # e.g., 2:30 PM
    regex1 = r'(10|11|12|[1-9]) ?([ap].? ?m.?)' # e.g., 2 PM
    regex2 = r'(10|11|12|[1-9])([:.][0-5][0-9])' # e.g., 2:30
    time_re = re.compile(make_time_re())
    result = re.search(time_re, text.lower())
    return get_time(result) if result else result


def start_end_time_from_phrase(text):
  time_re = make_time_re()
  # number dash time, time dash time
  startend_re = r'(\b([0-9]|10|11|12) ?([-–]|to) ?(' + time_re + r'))|((' + time_re + r') ?([-–]|to) ?(' + time_re + r'))'
  result = re.search(re.compile(startend_re), text.lower())
  if result:
    split = re.split(r'[-–]|to', result.group(0))
    split = [re.sub(r' ', '', x) for x in split]
    end = get_time(re.search(split[1], split[1])) # super hacky
    ampm = 'am' if end[0] < 12 else 'pm'
    start = get_time(re.search(split[0], split[0]), ampm) # types are hard
    return start, end
  return None


def get_time(match, ampm_override=None):
    # Convert from a raw regex match to an (hour, minute) tuple
    text = match.group()
    
    if text == 'noon': # Special case
      hour, minute, ampm = (12, 0, 'pm')
    else:
      hour = int(re.search(r'^\d+(?=(?:[:.ap ]|$))', text).group(0))

      raw_minute = re.search(r'(?<=[:.])\d+', text)
      minute = int(raw_minute.group(0)) if raw_minute else 0

      raw_ampm = re.search(r'[ap].*', text)
      if raw_ampm:
          ampm = re.sub(r'[^apm]', '', raw_ampm.group(0).lower())
      elif ampm_override: # This is for stuff like '7' in '7-10pm'
          ampm = ampm_override
      else:
          if hour in (10, 11):
              ampm = 'am'
          else:
              ampm = 'pm'

    dt_hour = hour
    if ampm == 'pm' and hour != 12:
        dt_hour += 12
    elif ampm == 'am' and hour == 12:
        dt_hour = 0

    return (dt_hour, minute)


def new_parse_dates(raw_text):
    print("...getting datetime")
    """ Extract full datetime object from text """
    text = clean_chain(raw_text)
    OFFSET = 40

    send_datetime = datetime.now()

    abs_dates = sorted(abs_date_from_phrase(text), key=lambda x: x[2])
    rel_dates = []#sorted(rel_date_from_phrase(text, send_date), key=lambda x: x[1])
    dates = abs_dates + rel_dates
    for date in dates:
      nearby_text = text[max(0, date[1] - OFFSET) : date[2] + OFFSET]
      #print(nearby_text)
      startend = start_end_time_from_phrase(nearby_text)
      if startend:
        (start_hour, start_minute), (end_hour, end_minute) = startend
        month, day = date[0]
        year = send_datetime.year if send_datetime.month <= month else send_datetime.year + 1
        start = utc(datetime(year, month, day, start_hour, start_minute))
        end = utc(datetime(year, month, day, end_hour, end_minute))
        return start, end

    for date in dates:
      nearby_text = text[max(0, date[1] - OFFSET) : date[2] + OFFSET]
      start_time = time_from_phrase(nearby_text)
      if start_time:
        start_hour, start_minute = start_time
        month, day = date[0]
        year = send_datetime.year if send_datetime.month <= month else send_datetime.year + 1
        start = utc(datetime(year, month, day, start_hour, start_minute))
        return start, None

    # raise ValueError('No datetime found.')
    
    second_attempt = parse_dates(raw_text)
    if second_attempt is None:
      print("No Datetime Found")
    return second_attempt

if __name__ == "__main__":
    f = open("test_dates.txt", "r")
    for l in f.readlines():
        print(l.strip())
        print(new_parse_dates(l.strip(), None))
