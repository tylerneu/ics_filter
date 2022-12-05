# 

import requests
from ics import Calendar
from datetime import datetime, timedelta
import pytz
import re

# FILTER OPTIONS

# Date range
NOW = datetime.utcnow().replace(tzinfo=pytz.timezone('US/Central'))
START_DATE = NOW - timedelta(days=10) 
END_DATE = NOW + timedelta(days=60)

# Name match
EXCLUDE_REGEX = [
    "break",
    "no school",
]

FORCE_INCLUDE_REGEX = []

EXCLUDE_MULTI_DAY = True

EXCLUDED_IDS = []
FORCE_INCLUDED_IDS = []

r = requests.get(
    'https://scoutbook.scouting.org/ics/44935.D37B9.ics',
    headers={'User-Agent': ''}
)

c = Calendar(r.text)

events = []
for e in sorted(c.events):
    append = True
    force_append = False

    if not (e.begin > START_DATE and e.begin < END_DATE):
        append = False

    for r in EXCLUDE_REGEX:
        result = re.search(r, e.name, re.IGNORECASE)
        if result:
            append = False

    for r in FORCE_INCLUDE_REGEX:
        result = re.search(r, e.name, re.IGNORECASE)
        if result:
            force_append = True

    for id in EXCLUDED_IDS:
        if id == e.uid:
            append = False

    for id in FORCE_INCLUDED_IDS:
        if id == e.uid:
            force_append = True

    if EXCLUDE_MULTI_DAY:
        if e.duration > timedelta(hours=24):
            append = False

    if append or force_append:
        events.append(e)


new_c = Calendar(events=events)

open('filtered_troop_150.ics', 'w').writelines(new_c)