"""
tac_parse - Parse tac_plus accounting logs.
"""

import datetime
import re

# New
# Feb  2 18:40:47 192.168.0.202   jathan  ttyp1   192.168.0.10    start   task_id=1       service=shell   process*mgd[7741]       cmd=login


# This parses the line above (New)
PAT = (
    r'(?P<timestamp>\w{3}\s+\d{1,2}\s\S+)\s'
     '(?P<device_ip>\S+)\s+'
     '(?P<username>\w+)\s+'
     '(?P<tty>\w+)\s+'
     '(?P<server_ip>\S+)\s+'
     '(?P<start_stop>\w+)\s+'
     'task_id=(?P<task_id>\d)\s+'
     'service=(?P<service>\w+)\s+'
     '(?P<process>\S+)\s+'
     '(?P<av_pairs>.*)'
)


def parse_line(line, pat=PAT):
    m = re.search(pat, line)
    if m: 
        return m.groupdict()
    return None


DATE_FORMAT = '%b %d %H:%M:%S %Y'
def parse_date(ts):
    ts = '%s %s' % (ts, datetime.date.today().year)
    return datetime.datetime.strptime(ts, DATE_FORMAT)
