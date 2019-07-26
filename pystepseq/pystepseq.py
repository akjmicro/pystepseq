#!/usr/bin/python3 -i
# -*- coding: utf-8 -*-
#
#       pystepseq.py
#
#       Copyright 2013-2019 Aaron Krister Johnson <akjmicro@gmail.com>
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
import _thread
import pickle

from math import ceil, log
from random import randint, choice

# my modules:
from pystepseq.lib.midi_functions import (close_port, note_off, note_on,
                                          open_port, pitch_bend)
from pystepseq.lib.scales import *  # noqa
from pystepseq.lib.pink_noise import pink_noise


class Pystepseq:
    """The Pystepseq object defines a MIDI voice that will be triggered
    to sound by a multicast network Tempotrigger object.
    """
    def __init__(self, chn=0):
        from . import constants
        from .tempotrigger import openmcastsock
        self.chn = chn
        self.step = -1
        self.end = 16  # num of note events, distinguished from beats
        self.triggers_per_beat = 24
        self.beats_per_measure = 4  # total number of beats in a measure
        self.triggers_per_measure = (self.triggers_per_beat *
                                     self.beats_per_measure)
        self.scl = MidiScale(modal)  # noqa
        self.runstate = 0
        self.len_list = []
        self.vol_list = []
        self.gate_list = []
        self.note_list = []
        self.note_noise = 'white'  # can be brown or pink, too
        self.note_depth = 5
        self.note_repeat = 0
        self.note_tie = 0
        self.vol_noise = 'white'
        self.vol_depth = 20
        self.sp = 0
        self.MYGROUP = '225.0.0.250'
        self.MYPORT = constants.DEFAULT_MULTICAST_PORT
        self.receiver = openmcastsock(self.MYGROUP, self.MYPORT)
        self.open_port_exists = False
        # automatic init:
        # on a Mac, the variable is a dummy...
        self.init_midi_port(constants.DEFAULT_MIDI_PORT)
        self.initlists()
        self._pickle_slots = [None for x in range(16)]
        for x in range(16):
            self.pickle_slot_save(x)
        self.current_slot = 0
        self.old_slot = 0

    def pickle_slot_save(self, num):
        slot_dict = {}
        for att in ['chn', 'end', 'scl', 'note_list', 'vol_list', 'len_list']:
            slot_dict[att] = pickle.dumps(getattr(self, att))
        self._pickle_slots[num] = slot_dict

    def pickle_slot_recall(self, num):
        in_slot_dict = self._pickle_slots[num]
        for k in in_slot_dict.keys():
            setattr(self, k, pickle.loads(in_slot_dict[k]))

    def init_midi_port(self, midiport=None):
        if self.open_port_exists:
            close_port()
        open_port(midiport)
        self.open_port_exists = True

    # randomize functions:
    def _note_white(self, start, finish=None):
        """create white noise shaped note contour"""
        if finish is None:
            finish = len(self.len_list)
        var = self.note_depth
        chance_repeat = self.note_repeat
        chance_tie = self.note_tie
        scale_midpoint = self.scl.size // 2
        for blah in range(start, finish):
            randnum = scale_midpoint + randint(-var, var)
            if (randnum > self.scl.size):
                randnum = self.scl.size - (randnum - self.scl.size)
            if (randnum < 0):
                randnum = abs(randnum)
            if (chance_repeat >= randint(1, 100)):  # for repeat
                if (chance_tie >= randint(1, 100)):  # for space
                    randnum = -1
                else:
                    randnum = self.note_list[(blah - 1) % self.end]
            try:
                self.note_list[blah] = randnum
            except IndexError:
                self.note_list.append(randnum)

    def _note_brown(self, start, finish=None):
        """create brown noise shaped note contour"""
        if finish is None:
            finish = len(self.len_list)
        var = self.note_depth
        chance_repeat = self.note_repeat
        chance_tie = self.note_tie
        if start == 0 and finish == 1:
            start = 1
            finish = 2
        for blah in range(start, finish + 1):
            offset = randint(-var, var)
            current = self.note_list[blah - 1]
            new = (current + offset)
            if (new > self.scl.size):
                new = (current - offset)
            if (new < 0):
                new = abs(new)
            if (chance_repeat >= randint(1, 100)):  # for repeat
                if (chance_tie >= randint(1, 100)):  # for tie
                    new = -1
                else:
                    new = self.note_list[(blah - 1) % self.end]
            try:
                self.note_list[blah] = new
            except IndexError:
                self.note_list.append(new)

    def _note_pink(self, start, finish=None):
        """create pink noise shaped note contour"""
        if finish is None:
            finish = len(self.len_list)
        var = self.note_depth
        chance_repeat = self.note_repeat
        chance_tie = self.note_tie
        scale_midpoint = self.scl.size // 2
        finish_pow = int(ceil(log(finish, 2)))
        result_list = pink_noise(finish_pow, var)
        offset = -1 * (max(result_list) // 2)
        for blah in range(start, finish):
            randnum = scale_midpoint + (result_list[blah - 1] + offset)
            if (randnum > self.scl.size):
                randnum = self.scl.size - (randnum - self.scl.size)
            if (randnum < 0):
                randnum = abs(randnum)
            if (chance_repeat >= randint(1, 100)):  # for repeat
                if (chance_tie >= randint(1, 100)):  # for tie
                    randnum = -1
                else:
                    randnum = self.note_list[(blah - 1) % self.end]
            try:
                self.note_list[blah] = randnum
            except IndexError:
                self.note_list.append(randnum)

    def _vol_white(self, start, finish=None):
        """create white noise shaped volume contour"""
        if finish is None:
            finish = len(self.len_list)
        var = self.vol_depth
        chance = self.sp
        for blah in range(start, finish):
            randnum = 64 + randint(-var, var)  # 64 is half of 127
            if (randnum > 127):
                randnum = 127 - (randnum - 127)
            if (randnum < 0):
                randnum = abs(randnum)
            if (chance >= randint(1, 100)):  # for space
                randnum = 0
            try:
                self.vol_list[blah] = randnum
            except IndexError:
                self.vol_list.append(randnum)

    def _vol_brown(self, start, finish=None):
        """create brown noise shaped volume contour"""
        if finish is None:
            finish = len(self.len_list)
        var = self.vol_depth
        chance = self.sp
        if start == 0 and finish == 1:
            start = 1
            finish = 2
        for blah in range(start, finish):
            offset = randint(-var, var)
            current = self.vol_list[blah - 1]
            if (chance >= randint(1, 100)):
                new = 0
            else:
                new = (current + offset)
            if (new > 127):
                new = (current - offset)
            if (new < 0):
                new = (current - offset)
            try:
                self.vol_list[blah] = new
            except IndexError:
                self.vol_list.append(blah)

    def _vol_pink(self, start, finish=None):
        """create pink noise shaped volume contour"""
        if finish is None:
            finish = len(self.len_list)
        var = self.vol_depth
        chance = self.sp
        result_list = pink_noise(5, var)
        offset = -1 * (max(result_list) // 2)
        for blah in range(start, finish):
            randnum = 64 + (result_list[blah - 1] + offset)
            if (randnum > 127):
                randnum = 127 - (randnum - 127)
            if (randnum < 0):
                randnum = abs(randnum)
            if (chance >= randint(1, 100)):  # for space
                randnum = 0
            try:
                self.vol_list[blah] = randnum
            except IndexError:
                self.vol_list.append(randnum)

    def randomize_lengths(self, choice_list=None):
        """randomize lengths"""
        # give a sensible default if none is given:
        if choice_list is None:
            choice_list = [6, 6, 6, 6, 6, 6, 6, 6, 12, 12, 12, 18, 18, 24]
        outarr = []
        total = 0

        # re-calc the measure length:
        self.triggers_per_measure = (self.triggers_per_beat *
                                     self.beats_per_measure)

        # do this while we are below the beat count:
        while total < self.triggers_per_measure:
            leftover = self.triggers_per_measure - total
            # filter the choices by what won't go over:
            choice_list = list(filter(lambda x: x <= leftover, choice_list))
            if not choice_list:
                pick = leftover
            else:
                pick = choice(choice_list)
            outarr.append(pick)
            total += pick
        # we now have a replacement rhythm list. Set it!
        self.len_list = outarr
        # set the endpoint
        self.end = len(self.len_list)

    def randomize_gates(self, choice_list=None):
        """randomize gate lengths"""
        if choice_list is None:
            self.gate_list = [100 for x in self.len_list]
        else:
            self.gate_list = [choice(choice_list) for i in self.len_list]

    def randomize_volumes(self, choice_list=None):
        """randomize volumes"""
        if choice_list is None:
            start = 1 if self.vol_noise == 'brown' else 0
            finish = len(self.len_list)
            getattr(self, '_vol_%s' % self.vol_noise)(start, finish)
        else:
            self.vol_list = [choice(choice_list) for i in self.len_list]

    def randomize_notes(self, choice_list=None):
        """randomize notes"""
        if choice_list is None:
            start = 1 if self.note_noise == 'brown' else 0
            finish = len(self.len_list)
            getattr(self, '_note_%s' % self.note_noise)(start, finish)
        else:
            self.note_list = [choice(choice_list) for i in self.len_list]

    def randomize_drums(self, notes=None, vols=None):
        """special method for drum sounds (snare, cymbals, etc.)"""

        if notes is None:
            notes = [2, 3, 4, 5]
        if vols is None:
            vols = [25, 30, 40, 50, 60, 70, 80, 50, 40]
        self.note_list = [choice(notes) for x in range(32)]
        self.vol_list = [choice(vols) for x in range(32)]

    def initlists(self):
        self.randomize_lengths()
        self.randomize_gates()
        self.randomize_volumes()
        self.randomize_notes()

    def looper(self):
        """The looper is the heart of the sequencer"""
        trigger = 0
        self.trigger_count = 0
        self.step = -1
        self.cycle_idx = -1
        self.note_autocounter = 0
        self.vol_autocounter = 0
        self.old_note = 60  # dummy
        self.bend = 8192
        self.sounding = 0
        self.note_length = 24  # init dummy
        while (self.runstate == 1) or (self.cycle_idx != 0):
            trigger = self.receiver.recv(9)
            triggernum, cyclen = trigger.split(b'|')
            # proceed if it's the first of a note length, and we're running
            if (self.trigger_count == 0):
                self.step = (self.step + 1) % self.end
                # do we have to change slots?
                if (self.current_slot != self.old_slot) and \
                        (self.step == 0):
                    self.pickle_slot_recall(self.current_slot)
                    self.old_slot = self.current_slot
                #####
                self.note_length = int(self.len_list[self.step %
                                                     len(self.len_list)])
                self.vol = self.vol_list[self.step % len(self.vol_list)]
                self.gate = self.gate_list[self.step % len(self.gate_list)]
                self.gate_cutoff = int(
                    round(self.note_length * (self.gate / 100)))
                self.note_index = self.note_list[self.step %
                                                 len(self.note_list)]
                # protect against < 0
                if self.note_length < 1:
                    self.note_length = 1
                note_off(int(self.chn), int(self.old_note))
                self.note = self.scl.get_note(self.note_index)
                if isinstance(self.note, tuple):
                    self.note, self.bend = self.note[0], self.note[1]
                    if self.vol > 0:
                        pitch_bend(int(self.chn), int(self.bend))
                    note_on(int(self.chn), int(self.note), int(self.vol))
                else:
                    if self.bend != 8192:
                        pitch_bend(int(self.chn), int(self.bend))
                        self.bend = 8192
                    note_on(int(self.chn), int(self.note), int(self.vol))
                self.old_note = self.note
            # turn note off if the gate value indicates:
            elif self.trigger_count == self.gate_cutoff:
                note_off(int(), int(self.old_note))
            self.trigger_count = (self.trigger_count + 1) % self.note_length
            self.cycle_idx = (self.cycle_idx + 1) % int(cyclen)

        # upon receiving a kill signal:
        note_off(self.chn, self.old_note)
        self.step = -1

    def play(self, immediately=False):
        if self.runstate == 0:
            self.runstate = 1
            if not immediately:
                while True:
                    packet = self.receiver.recv(9)
                    num, cyclen = packet.split(b'|')
                    if int(num) == int(cyclen) - 1:
                        break
            _thread.start_new_thread(self.looper, ())

    def stop(self, immediately=False):
        if self.runstate == 0:
            return
        if not immediately:
            self.runstate = 0
        else:
            self.runstate = 0
            self.cycle_idx = -1
