#!/usr/bin/env python
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
  for ip in ips:
    sock.sendto(message, ip)
    send_to += 1 
  sock.setblocking(0)
  sock.settimeout(timeout)
  replies = []

  last = time.time()

  while True:
    try:
      r = sock.recvfrom(1024, 1024)
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


def query_masterservers(servers, sock, timeout):
  sock.setblocking(0)
  send_to = 0
  for server in servers:
    ipp = ip_from_string(server, port_default=27000)
    sock.settimeout(1)
    sock.sendto("c\n", ipp)
    send_to += 1
  
  sock.settimeout(timeout)
  bucket = []
  while True:
    try:
      data = sock.recvfrom(1024*1024)
      bucket.append(data)
      send_to -= 1
      if send_to == 0:
        break
    except:
      break

  out = ""
  server_ips = []
  for data in bucket:
    ips = data[0][6:]
    n = 6
    for ip in [ips[i:i+n] for i in xrange(0, len(ips), n)]:
        server_ips.append((".".join(str(x) for x in struct.unpack("!BBBB", ip[:4])), struct.unpack("!H", ip[4:])[0]))
  server_ips = list(set(server_ips))
  return server_ips



def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('server', nargs='+')
  parser.add_argument('--port', '-p', default=0, help='bind port if not specified the OS will select one')
  parser.add_argument('--ip', '-i', default='0.0.0.0', help='default bind address: 0.0.0.0')
  parser.add_argument('--timeout', '-t', type=float, default=0.5, help='time in seconds to wait for server reply')
  args = parser.parse_args()

  s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  ip = socket.gethostbyname(args.ip)
  s.bind((ip, args.port))

  ips = query_masterservers(args.server, s, 1)

  servers = []
  replies = listen_and_wait(s, ips, "\xff\xff\xff\xffstatus 23\n", args.timeout)
  for reply in replies:
    server = {}
    server['players'] = []
    server['ip'] = str(reply[1][0]) + ":" + str(reply[1][1])
    info_string = reply[0][6:-2]
    info_string = info_string.split("\n")
    players = info_string[1:-1]
    info_string = info_string[0].split("\\")
    for info in zip(info_string, info_string[1:])[::2]:
      server[info[0]] = info[1]
    for player in players:
      p = shlex.split(player)
      server['players'].append(p)
    servers.append(server)

  print json.dumps(servers, ensure_ascii=False)


if __name__ == '__main__':
  status = main()
  sys.exit(status)

