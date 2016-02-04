#!/usr/bin/env python

"""
tac_parse - Parse tac_plus accounting logs.
"""

__version__ = '0.4.1'


import re


############
# Patterns #
############

# Regex patterns for timestamps preceding log events that are used to parse
# into epoch time.
TIMESTAMP_PATTERNS = (
    # Jun 29 14:56:24
    # r'(?P<timestamp>\w{3}\s+\d{1,2}\s\S+)\s*',

    # Jun 29 14:56:24
    # Tue Jan 26 22:50:21 2016
    # r'(?P<timestamp>\w{3}\s\w{3}\s+\d{1,2}\s\S+\s\d{4})\s*',

    # Jun 29 14:56:24
    # Tue Jan 26 22:50:21 2016
    r'(?P<timestamp>(?:\w{3}\s)?\w{3}\s+\d{1,2}\s\S+\s*(?:\d{4})?)\s*',
)

# This pattern captures the following timestamp formats:
#
# - Jun 29 14:56:24 ('%b %d %H:%M:%S %Y')
# - Tue Jan 26 22:50:21 2016 ('%b %d %H:%M:%S %Y')
RE_TIMESTAMP = r'(?P<timestamp>(?:\w{3}\s)?\w{3}\s+\d{1,2}\s\S+\s*(?:\d{4})?)\s*'

# Juniper device (timestamp has no weekday or year)
"""
Feb  2 18:40:47 192.168.0.202   jathan  ttyp1   192.168.0.10    start task_id=1       service=shell   process*mgd[7741]       cmd=login
"""

# Juniper devices (interactive-commands)
"""
Thu Jan 21 19:25:41 2016    10.242.4.218    jathan  ttyp0   10.160.161.189 stop    task_id=9   service=shell   process*mgd[90940]  cmd=show lldp remote-global-statistics <cr>
Thu Jan 21 19:25:48 2016    10.242.4.218    jathan  ttyp0   10.160.161.189 stop    task_id=10  service=shell   process*mgd[90940]  cmd=show lldp detail <cr>
Thu Jan 21 19:25:54 2016    10.242.4.218    jathan  ttyp0   10.160.161.189 stop    task_id=11  service=shell   process*mgd[90940]  cmd=show lldp detail | display xml <cr>
Thu Jan 21 19:26:36 2016    10.242.4.218    jathan  ttyp0   10.160.161.189 stop    task_id=12  service=shell   process*mgd[90940]  cmd=show snmp mib walk ascii LLDP-MIB::lldpRemPortId <cr>
Thu Jan 21 19:26:48 2016    10.242.4.218    jathan  ttyp0   10.160.161.189 stop    task_id=13  service=shell   process*mgd[90940]  cmd=show lldp statistics <cr>
"""

# Juniper too?
# The "session_pid = n" thing needs to be normalized.
"""
Tue Jan 26 18:38:49 2016    10.160.164.56  rancid  non-tty 10.160.165.116 start   task_id=1   service=shell   session_pid = 46420 cmd=login
Tue Jan 26 18:38:49 2016    10.160.164.56  rancid  non-tty 10.160.165.116 stop    task_id=2   service=shell   session_pid = 46420 cmd=show chassis alarms <cr>
Tue Jan 26 18:38:49 2016    10.160.164.56  rancid  non-tty 10.160.165.116 stop    task_id=1   service=shell   session_pid = 46420 elapsed_time=0  cmd=logout
"""

# Juniper Junoscript/NETCONF tab-separated (why?!)
# Also server_ip is 'Unknown host - no-tty'
"""
'Feb  4 15:20:45\t192.168.0.202\troot\tnon-tty\tUnknown host - non-tty\tstart\ttask_id=1\tservice=shell\tprocess*mgd[10580]\tcmd=login'
"""

# And then this one with a messed up task_id
"""
Wed Jan 27 20:22:24 2016\t10.34.201.64\trancid\t0\t10.16.2.149\tstop\ttask_id=10.16.2.149@pts/0\tstart_time=1453926144\ttimezone=PST\tstop_time=1453926144\tservice=none
"""

# Cisco 4948E (exec start-stop only)
"""
Tue Jan 26 22:50:21 2016    10.13.137.9 jathan  tty1    10.16.2.149 start   task_id=88947   timezone=UTC    service=shell   start_time=1453848621
Tue Jan 26 22:53:19 2016    10.13.137.9 jathan  tty1    10.16.2.149 stop    task_id=88947   timezone=UTC    service=shell   start_time=1453848621   disc-cause=1    disc-cause-ext=9    pre-session-time=2  elapsed_time=17 stop_time=1453848799
"""

# Line patterns
RE_LINE_COMMAND = (
    RE_TIMESTAMP +
    r'(?P<device_ip>\S+)[\t\s]+'
    r'(?P<username>\w+)[\t\s]+'
    r'(?P<tty>\S+)[\t\s]+'
    r'(?P<server_ip>(?:Unknown host - non-tty|\S+))[\t\s]+'
    r'(?P<start_stop>\w+)[\t\s]+'
    r'task_id=(?P<task_id>\S*)[\t\s]+'  # task_id is sometimes empty
    r'(?P<av_pairs>.*)'             # A/V pairs are always at the end
)

# All of the default patterns in order from most-to-least common.
LINE_PATTERNS = [
    re.compile(RE_LINE_COMMAND),
]

# This is used to capture and split an A/V pair into a list of strings
RE_AV_PAIR = re.compile(r'([^\s]*)[ ]{2,}')


def cleanup_av_pairs(av_pairs, pattern=None):
    if pattern is None:
        pattern = RE_AV_PAIR

    # Generic cleanup
    av_pairs = av_pairs.replace('\t', '  ')  # tabs to spaces
    av_pairs = av_pairs.replace(' = ', '=')  # cleanup '='
    av_pairs = av_pairs.replace('process*', 'process=') # '*' => '='

    # Non-commands don't have spaces and can simply be .split()
    if 'cmd=' not in av_pairs:
        pairs = av_pairs.split()

    # Commands can have spaces so process them w/ regex.
    else:
        pairs = [av for av in pattern.split(av_pairs) if av]  # Skip ''

    return dict(p.split('=') for p in pairs)


def parse_line(line, patterns=None):
    """Parse a ```line`` based against a list of ``patterns``."""
    if patterns is None:
        patterns = LINE_PATTERNS

    for line_re in patterns:
        match = line_re.match(line)
        if match:
            data = match.groupdict()
            av_pairs = data['av_pairs']
            # data['av_pairs'] = av_pairs.replace('\t', '  ')
            data['av_pairs'] = cleanup_av_pairs(av_pairs)
            return data

    return None
