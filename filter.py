import requests
from ics import Calendar
from datetime import datetime, timedelta
import pytz
import re
from rich.console import Console

console = Console()

configs = [
    # {
    #     'start_days': 10,
    #     'end_days': 60,
    #     'exclude_regex': [
    #         "break",
    #         "no school",
    #         "Roundtable",
    #     ],
    #     'remove_substring': [],
    #     'include_regex': [],
    #     'exclude_multi_day': True,
    #     'excluded_ids': [],
    #     'force_included_ids': [],
    #     'max_name_length': 30,
    #     'url': 'https://scoutbook.scouting.org/ics/44935.D37B9.ics',
    #     'outgoing_filename': 'filtered_troop_150.ics'
    # },
    {
        'start_days': 10,
        'end_days': 120,
        'exclude_regex': [],
        'remove_substring': [
            ' - Spring 2023 Practice'
        ],
        'include_regex': [],
        'exclude_multi_day': True,
        'excluded_ids': [],
        'force_included_ids': [],
        'max_name_length': 30,
        'url': 'https://sportsplus.app/my/sports-life/schedule/member/icalendar-subscribe/81807/MySchedule.ics',
        'outgoing_filename': 'braves_spring_2023.ics'
    }
]

for config in configs:

    # FILTER OPTIONS

    # Date range
    NOW = datetime.utcnow().replace(tzinfo=pytz.timezone('US/Central'))
    START_DATE = NOW - timedelta(days=config['start_days'])
    END_DATE = NOW + timedelta(days=config['end_days'])

    r = requests.get(config['url'], headers={'User-Agent': 'ics_filter'}
    )

    c = Calendar(r.text)

    events = []
    for e in sorted(c.events):
        append = True
        force_append = False

        if not (e.begin > START_DATE and e.begin < END_DATE):
            append = False

        for r in config['exclude_regex']:
            result = re.search(r, e.name, re.IGNORECASE)
            if result:
                append = False

        for r in config['include_regex']:
            result = re.search(r, e.name, re.IGNORECASE)
            if result:
                force_append = True

        for id in config['excluded_ids']:
            if id == e.uid:
                append = False

        for id in config['force_included_ids']:
            if id == e.uid:
                force_append = True

        if config['exclude_multi_day']:
            if e.duration > timedelta(hours=24):
                append = False

        if append or force_append:

            for substring in config['remove_substring']:
                e.name = e.name.replace(substring, '')
                console.print(e.begin.strftime('%m/%d/%y'), e.name, style="black on orange")

            if len(e.name) > config['max_name_length']:
                e.name = e.name[0:config['max_name_length']]
                console.print(e.begin.strftime('%m/%d/%y'), e.name, style="black on yellow")
            else:
                console.print(e.begin.strftime('%m/%d/%y'), e.name, style="white on green")

            events.append(e)
        else:
            console.print(e.begin.strftime('%m/%d/%y'), e.name, style="white on red")


    new_c = Calendar(events=events)

    open(config['outgoing_filename'], 'w').writelines(new_c)
