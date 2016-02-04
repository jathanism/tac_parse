# tac_parse
Tacacs+ (tac_plus) accounting log event parser

# Example

Given these lines:

```
Thu Jan 21 19:25:41 2016    10.242.4.218    jathan  ttyp0   10.160.161.189 stop task_id=9   service=shell   process*mgd[90940]  cmd=show lldp remote-global-statistics <cr>
Thu Jan 21 19:25:48 2016    10.242.4.218    jathan  ttyp0   10.160.161.189 stop task_id=10  service=shell   process*mgd[90940]  cmd=show lldp detail <cr> Thu Jan 21 19:25:54 2016    10.242.4.218    jathan  ttyp0   10.160.161.189 stop
task_id=11  service=shell   process*mgd[90940]  cmd=show lldp detail | display xml <cr>
Thu Jan 21 19:26:36 2016    10.242.4.218    jathan  ttyp0   10.160.161.189 stop task_id=12  service=shell   process*mgd[90940]  cmd=show snmp mib walk ascii LLDP-MIB::lldpRemPortId <cr>
Thu Jan 21 19:26:48 2016    10.242.4.218    jathan  ttyp0   10.160.161.189 stop task_id=13  service=shell   process*mgd[90940]  cmd=show lldp statistics <cr>
```

Parse into these:

```python
>>> import tac_parse
>>> for line in lines:
...     print tac_parse.parse_line(line)
 {'av_pairs': {'cmd': 'show lldp remote-global-statistics <cr>',
   'process': 'mgd[90940]',
   'service': 'shell'},
  'device_ip': '10.242.4.218',
  'server_ip': '10.160.161.189',
  'start_stop': 'stop',
  'task_id': '9',
  'timestamp': 'Thu Jan 21 19:25:41 2016',
  'tty': 'ttyp0',
  'username': 'jathan'},
 {'av_pairs': {'cmd': 'show lldp detail <cr>',
   'process': 'mgd[90940]',
   'service': 'shell'},
  'device_ip': '10.242.4.218',
  'server_ip': '10.160.161.189',
  'start_stop': 'stop',
  'task_id': '10',
  'timestamp': 'Thu Jan 21 19:25:48 2016',
  'tty': 'ttyp0',
  'username': 'jathan'},
 {'av_pairs': {'cmd': 'show lldp detail | display xml <cr>',
   'process': 'mgd[90940]',
   'service': 'shell'},
  'device_ip': '10.242.4.218',
  'server_ip': '10.160.161.189',
  'start_stop': 'stop',
  'task_id': '11',
  'timestamp': 'Thu Jan 21 19:25:54 2016',
  'tty': 'ttyp0',
  'username': 'jathan'},
 {'av_pairs': {'cmd': 'show snmp mib walk ascii LLDP-MIB::lldpRemPortId <cr>',
   'process': 'mgd[90940]',
   'service': 'shell'},
  'device_ip': '10.242.4.218',
  'server_ip': '10.160.161.189',
  'start_stop': 'stop',
  'task_id': '12',
  'timestamp': 'Thu Jan 21 19:26:36 2016',
  'tty': 'ttyp0',
  'username': 'jathan'},
 {'av_pairs': {'cmd': 'show lldp statistics <cr>',
   'process': 'mgd[90940]',
   'service': 'shell'},
  'device_ip': '10.242.4.218',
  'server_ip': '10.160.161.189',
  'start_stop': 'stop',
  'task_id': '13',
  'timestamp': 'Thu Jan 21 19:26:48 2016',
  'tty': 'ttyp0',
  'username': 'jathan'}
```
