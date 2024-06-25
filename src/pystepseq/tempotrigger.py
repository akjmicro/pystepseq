#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#       tempotrigger.py
#
#       Copyright 2013-2018 Aaron Krister Johnson <akjmicro@gmail.com>
#
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

# modules needed:
import socket
import struct
import _thread
import time

# my modules:
from . import constants


class Tempotrigger:
    def __init__(self, num_triggers_per_qn=24, cycle_len=24 * 8):
        self.runstate = 0
        self.num_triggers_per_qn = num_triggers_per_qn
        self.cycle_len = cycle_len
        self.cycle_len_flag = self.cycle_len - 1
        self.tempo = 120
        self.sleep_time = 60.0 / (self.tempo * self.num_triggers_per_qn)
        # mcast sender stuff (for sending sync timestamps):
        self.MYPORT = constants.DEFAULT_MULTICAST_PORT
        self.MYGROUP = "225.0.0.250"
        self.sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.mygroup = self.MYGROUP
        self.ttl = struct.pack("b", 1)  # Time-to-live
        self.sender.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, self.ttl)

    def set_num_triggers(self, numtriggers):
        self.num_triggers_per_qn = numtriggers
        self.sleep_time = 60.0 / float(self.tempo * self.num_triggers_per_qn)

    def set_tempo(self, tempo):
        self.tempo = tempo
        self.sleep_time = 60.0 / float(tempo * self.num_triggers_per_qn)

    def set_cycle_len(self, cycle_len):
        self.cycle_len = cycle_len
        self.cycle_len_flag = self.cycle_len - 1

    def trigger(self):
        self.cycle_idx = self.cycle_len_flag  # just before 0
        while self.runstate == 1:
            self.target = time.time() + self.sleep_time
            self.cycle_idx = (self.cycle_idx + 1) % self.cycle_len
            self.sender.sendto(
                bytes(
                    "".join(
                        [repr(self.cycle_idx).zfill(4), "|", repr(self.cycle_len)]
                    ).zfill(4),
                    "ascii",
                ),
                (self.mygroup, self.MYPORT),
            )
            time.sleep(self.sleep_time - 0.006)
            # accuracy tweak loop:
            nowtime = time.time()  # starting point
            while nowtime < self.target:  # while not within 1ms
                time.sleep(0.0001)
                nowtime = time.time()  # get new moving point

    def run(self):
        if self.runstate == 0:
            self.runstate = 1
            _thread.start_new_thread(self.trigger, ())

    def stop(self):
        if self.runstate == 1:
            self.runstate = 0


def openmcastsock(group, port):
    """create a network mcast connection for our rhythmic metronome pulse"""
    # Import modules used only here
    import struct

    # Create a socket
    socket_obj = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Allow multiple copies of this program on one machine
    # (not strictly needed)
    socket_obj.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

    # Bind it to the port
    socket_obj.bind(("", port))

    # Look up multicast group address in name server
    # (doesn't hurt if it is already in ddd.ddd.ddd.ddd format)
    group = socket.gethostbyname(group)

    # Construct binary group address
    bytes = map(int, group.split("."))
    grpaddr = 0
    for byte in bytes:
        grpaddr = (grpaddr << 8) | byte

    # Construct struct mreq from grpaddr and ifaddr
    ifaddr = socket.INADDR_ANY
    mreq = struct.pack("LL", socket.htonl(grpaddr), socket.htonl(ifaddr))

    # Add group membership
    socket_obj.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    return socket_obj
