#!/usr/bin/python3 -i
# -*- coding: utf-8 -*-
#
#       pystepseq
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

import pickle
from readline import *  # noqa

# my modules:
from .help import help
from .pystepseq import Pystepseq
from .tempotrigger import Tempotrigger
from pystepseq.lib.pink_noise import fractal_melody
from pystepseq.lib.scales import *  # noqa

# a dict which hosts object instances so we can manipulate
# multiple parameters of multiple instances simultaneously
active_instances = {}


def setup_drums():
    from scales import TR808
    # bass drum sound:
    active_instances['z'] = Pystepseq(10)
    z = active_instances['z']
    z.scl.set_scl(TR808)
    z.scl.set_min_max_trans(36, 60, 0)
    z.len_list = [24]
    z.note_list = [0]
    z.vol_list = [80]
    # other drums:
    active_instances['x'] = Pystepseq(10)
    x = active_instances['x']
    x.scl.set_scl(TR808)
    x.scl.set_min_max_trans(36, 60, 0)
    x.len_list = [6]
    x.randomize_drums()


def change(instances, notes=1, vols=1, lengths=1, gates=1):
    """section(instances, notes=1, vols=1, lengths=1)
    allows for the simultaneous changing of all pystepseq objects parameters
    """
    for i in instances:
        if notes:
            active_instances[i].randomize_notes()
        if vols:
            active_instances[i].randomize_volumes()
        if lengths:
            active_instances[i].randomize_lengths()
        if gates:
            active_instances[i].randomize_gates()


def slot_queue_save(slot):
    for i in active_instances.values():
        i.pickle_slot_save(slot)


def slot_queue_recall(slot):
    for i in active_instances.values():
        i.current_slot = slot


def save_song(filename):
    outfile = open(filename, 'wb')
    pickle.dump(active_instances, outfile)
    outfile.close()
    print("wrote song to %s" % filename)


def load_song(filename):
    infile = open(filename, 'rb')
    active_instances = pickle.load(infile)
    for k in active_instances:
        exec("%s = active_instances['%s']" % (k, k)) in globals()
        active_instances[k].init_midi_port()
    print("loaded song %s" % filename)


def command_parser(phrase):  # noqa
    all_commands = phrase.rstrip().split(';')
    for comm in all_commands:
        if comm[0] == 'h':
            help()
            break
        if comm[0] in '1234567890':
            slot_queue_recall(int(comm))
        elif comm[0] == 'q':
            try:
                slot_queue_save(int(comm[1:]))
            except ValueError:
                print('Error in numerical input')
        elif comm[0:7] == 'zxdrums':
            setup_drums()
        elif comm[0:5] == 'load ':
            load_song(comm[5:])
        elif comm[0:5] == 'save ':
            save_song(comm[5:])
        elif comm[0] == '=':
            if comm[1] == 't':
                print("'t' is a reserved object for tempo, cannot use")
            else:
                if len(comm) == 2:
                    active_instances[comm[1]] = Pystepseq()
                elif len(comm) > 2:
                    active_instances[comm[1]] = Pystepseq(int(comm[2:]))
        elif comm[0] == '-':
            try:
                active_instances[comm[1]].stop(immediately=True)
                del(active_instances[comm[1]])
            except KeyError:
                print('No such active voice')
        elif comm[0] == '`':
            change([i.strip() for i in comm[1:].split(',')])
        elif comm[0:2] == 'tt':
            if len(comm) == 2:
                print(trig.num_triggers_per_qn)
            else:
                try:
                    trig.set_num_triggers(int(comm[2:]))
                except ValueError:
                    print('could not parse the number of triggers')
        elif comm[0] == 't':
            if len(comm) == 1:
                print(trig.tempo)
            elif comm[1] == '/':
                trig.run()
            elif comm[1] == '\\':
                print('Doing trigger stop!')
                trig.stop()
            elif comm[1] == 'c':
                if len(comm) == 2:
                    print(trig.cycle_len)
                else:
                    try:
                        trig.set_cycle_len(int(eval(comm[2:])))
                    except ValueError:
                        print("cannot parse that cycle length count")
            else:
                try:
                    trig.set_tempo(abs(int(comm[1:])))
                except ValueError:
                    print("cannot parse that tempo")
        elif comm[1:3] == 'md':
            current_min = active_instances[comm[0]].scl.min
            current_max = active_instances[comm[0]].scl.max
            delta = int(comm[3:])
            new_min, new_max = current_min + delta, current_max + delta
            active_instances[comm[0]].scl.set_min(new_min)
            active_instances[comm[0]].scl.set_max(new_max)
        elif comm[1:3] == 'vd':
            if len(comm) == 3:
                print(active_instances[comm[0]].vol_depth)
            else:
                try:
                    active_instances[comm[0]].vol_depth = int(comm[3:])
                except ValueError:
                    print('Could not parse the input')
        elif comm[1:3] == 'vn':
            if len(comm) == 3:
                print(active_instances[comm[0]].vol_noise)
            else:
                if comm[3:].rstrip() in ['white', 'brown', 'pink']:
                    active_instances[comm[0]].vol_noise = comm[3:]
                else:
                    print("noise type must be white, brown, or pink")
        elif comm[1:3] == 'nd':
            if len(comm) == 3:
                print(active_instances[comm[0]].note_depth)
            else:
                try:
                    active_instances[comm[0]].note_depth = int(comm[3:])
                except ValueError:
                    print('Could not parse the input value')
        elif comm[1:3] == 'nn':
            if len(comm) == 3:
                print(active_instances[comm[0]].note_noise)
            else:
                if comm[3:].rstrip() in ['white', 'brown', 'pink']:
                    active_instances[comm[0]].note_noise = comm[3:]
                else:
                    print("noise type must be white, brown, or pink")
        elif comm[1:3] == 'nt':
            if len(comm) == 3:
                print(active_instances[comm[0]].note_tie)
            else:
                try:
                    active_instances[comm[0]].note_tie = int(comm[3:])
                except ValueError:
                    print('Could not parse the input value')
        # randomize lengths
        elif comm[1:3] == 'rl':
            choice_list = None
            if len(comm) > 3:
                try:
                    choice_list = eval(comm[3:])
                except SyntaxError:
                    print('Could not parse the given list')
            active_instances[comm[0]].randomize_lengths(
                choice_list=choice_list)
        # randomize lengths
        elif comm[1:3] == 'rg':
            choice_list = None
            if len(comm) > 3:
                try:
                    choice_list = eval(comm[3:])
                except SyntaxError:
                    print('Could not parse the given list')
            active_instances[comm[0]].randomize_gates(
                choice_list=choice_list)
        # randomize volumes
        elif comm[1:3] == 'rv':
            choice_list = None
            if len(comm) > 3:
                try:
                    choice_list = eval(comm[3:])
                except SyntaxError:
                    print('Could not parse the given list')
            active_instances[comm[0]].randomize_volumes(
                choice_list=choice_list)
        # randomize notes
        elif comm[1:3] == 'rn':
            choice_list = None
            if len(comm) > 3:
                try:
                    choice_list = eval(comm[3:])
                except SyntaxError:
                    print('Could not parse the given list')
            active_instances[comm[0]].randomize_notes(
                choice_list=choice_list)
        elif comm[1:3] == 'rd':
            choice_lists = None, None
            if len(comm) > 3:
                try:
                    choice_lists = eval(comm[3:])
                except SyntaxError:
                    print('Could not parse the given lists')
            active_instances[comm[0]].randomize_drums(*choice_lists)
        # stopping and starting voices (and the tempotrigger)
        elif comm[1:3] == r'\\':
            active_instances[comm[0]].stop(immediately=True)
        elif comm[1:3] == '//':
            active_instances[comm[0]].play(immediately=True)
        elif comm[1] == '\\':
            active_instances[comm[0]].stop()
        elif comm[1] == '/':
            active_instances[comm[0]].play()
        # triggers per beat
        elif comm[1:3] == 'bb':
            if len(comm) == 3:
                print(active_instances[comm[0]].triggers_per_beat)
            else:
                active_instances[comm[0]].triggers_per_beat = int(comm[3:])
        # beats per measure
        elif comm[1] == 'b':
            if len(comm) == 2:
                print(active_instances[comm[0]].beats_per_measure)
            else:
                active_instances[comm[0]].beats_per_measure = int(comm[2:])
        # ending note (by count)
        elif comm[1] == 'e':
            if len(comm) == 2:
                print(active_instances[comm[0]].end)
            else:
                active_instances[comm[0]].end = int(comm[2:])
        # lengths
        elif comm[1] == 'l':
            if len(comm) == 2:
                print(active_instances[comm[0]].len_list)
            else:
                if '=' not in comm:
                    active_instances[comm[0]].len_list = eval(comm[2:])
                else:
                    parts = comm[2:].split('=')
                    idx, val = int(parts[0]), int(parts[1])
                    active_instances[comm[0]].len_list[idx] = eval(val)
        # gates
        elif comm[1] == 'g':
            if len(comm) == 2:
                print(active_instances[comm[0]].gate_list)
            else:
                if '=' not in comm:
                    active_instances[comm[0]].gate_list = eval(comm[2:])
                else:
                    parts = comm[2:].split('=')
                    idx, val = int(parts[0]), int(parts[1])
                    active_instances[comm[0]].gate_list[idx] = eval(val)
        # volumns
        elif comm[1] == 'v':
            if len(comm) == 2:
                print(active_instances[comm[0]].vol_list)
            else:
                if '=' not in comm:
                    active_instances[comm[0]].vol_list = eval(comm[2:])
                else:
                    parts = comm[2:].split('=')
                    idx, val = int(parts[0]), int(parts[1])
                    active_instances[comm[0]].vol_list[idx] = eval(val)
        # volume 'space' (how much silence in a pattern)
        elif comm[1] == 'p':
            if len(comm) == 2:
                print(active_instances[comm[0]].sp)
            else:
                active_instances[comm[0]].sp = int(comm[2:])
        # scale type
        elif comm[1] == 's':
            if len(comm) == 2:
                print(active_instances[comm[0]].scl.slave)
            else:
                active_instances[comm[0]].scl.set_scl(eval(comm[2:]))
        # fractal note list
        elif comm[1] == 'f':
            myargs = eval(comm[2:])
            active_instances[comm[0]].note_list = fractal_melody(*myargs)
        # notes
        elif comm[1] == 'n':
            if len(comm) == 2:
                print(active_instances[comm[0]].note_list)
            else:
                if '=' not in comm:
                    active_instances[comm[0]].note_list = eval(comm[2:])
                else:
                    parts = comm[2:].split('=')
                    idx, val = int(parts[0]), int(parts[1])
                    active_instances[comm[0]].note_list[idx] = eval(val)
        # min note, max note, transposition
        elif comm[1] == 'm':
            if len(comm) == 2:
                print(active_instances[comm[0]].scl.min)
            else:
                active_instances[comm[0]].scl.set_min(int(comm[2:]))
        elif comm[1] == 'x':
            if len(comm) == 2:
                print(active_instances[comm[0]].scl.max)
            else:
                active_instances[comm[0]].scl.set_max(int(comm[2:]))
        elif comm[1] == 't':
            if len(comm) == 2:
                print(active_instances[comm[0]].scl.trans)
            else:
                active_instances[comm[0]].scl.set_trans(int(comm[2:]))
        elif comm[1] == 'i':
            if len(comm) == 2:
                print(active_instances[comm[0]].scl.min)
                print(active_instances[comm[0]].scl.max)
                print(active_instances[comm[0]].scl.trans)
            else:
                try:
                    min_max_trans_args = eval(comm[2:])
                    active_instances[comm[0]].scl.set_min_max_trans(
                        *min_max_trans_args)
                except TypeError:
                    print('Cannot parse the arguments for min_max_trans')
        else:
            print("command not understood, or not implemented yet")


# set up the global tempo sequencer object that 'ticks' the grid time:
trig = Tempotrigger(24)  # 24 is the number of triggers per beat
trig.set_tempo(120)  # 120 BPM default


def repl():
    trig.run()
    while True:
        try:
            phrase = input('pystepseq(\'h\' for help)--> ')
            if len(phrase) == 0:
                continue
            command_parser(phrase)
        except (TypeError, KeyError, ValueError, IndexError, SyntaxError,
                NameError) as e:
            print('Error due to malformed input: %s Please try again.' % e)
        except (EOFError, KeyboardInterrupt):
            banner = '''
Debugging shell called with keyboard interrupt.
You can get back by hitting CTRL-D
To quit, write "quit()"'''
            from code import InteractiveConsole
            import readline
            import rlcompleter
            context = globals().copy()
            context.update(locals())
            readline.set_completer(rlcompleter.Completer(context).complete)
            readline.parse_and_bind("tab: complete")
            ic = InteractiveConsole(context)
            try:
                ic.interact(banner)
            except (EOFError):
                pass


if __name__ == '__main__':
    repl()
