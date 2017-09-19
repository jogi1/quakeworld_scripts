#! /usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import struct
import shlex
import pprint
import sys
import json
import time
import argparse

def ip_from_string(s, ip_default=None, port_default=None):
  sp = s.split(':')
  try:
    ip = socket.gethostbyname(sp[0])
    if len(sp) > 1:
      port = int(sp[1])
    else:
      port = port_default
    return (ip, port)
  except:
    return (ip_default, port_default)
  return (ip_default, port_default)


def listen_and_wait(sock, ips, message, timeout):
  send_to = 0
  sock.sendto(message, ips)
  send_to += 1 
  sock.setblocking(0)
  sock.settimeout(timeout)
  replies = []

  last = time.time()

  while True:
    try:
      r = s.recvfrom(1024, 1024)
      replies.append(r)
      now = time.time()

      sock.settimeout(timeout)
      last = now
      send_to -= 1
      if send_to == 0:
        return
    except:
      break
  return replies


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('server')
  parser.add_argument('password')
  parser.add_argument('command', nargs='+')
  parser.add_argument('--port', '-p', default=0, help='bind port if not specified the OS will select one')
  parser.add_argument('--ip', '-i', default='0.0.0.0', help='default bind address: 0.0.0.0')
  parser.add_argument('--timeout', '-t', type=float, default=0.5, help='time in seconds to wait for server reply')
  args = parser.parse_args()

  s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  ip = socket.gethostbyname(args.ip)
  s.bind((ip, args.port))

  ips = ip_from_string(args.server)

  servers = []
  replies = listen_and_wait(s, ips, "\xff\xff\xff\xffrcon %s %s\n" % (args.password, " ".join(args.command)), args.timeout)

  print json.dumps(replies, ensure_ascii=False)

if __name__ == '__main__':
  status = main()
  sys.exit(status)


