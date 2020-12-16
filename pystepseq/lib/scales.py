"""This module contains code for generating common musical scales
for use with MIDI."""

from math import log2

from pystepseq.lib.midi_functions import see_saw


perc_list = list(range(28, 52))
perc_list.extend([54, 58, 59, 61, 67, 68, 69, 70, 73, 74, 75, 77, 78, 79, 80])
perc_list.remove(49)


# gaps between neighboring ascending notes, '0' is an assumed starting point.
scale_vectors = {
    "chromatic": [1],
    "whole_tone": [2],
    "octatonic": [2, 1],
    "modal": [2, 2, 1, 2, 2, 2, 1],
    "pentatonic": [2, 3, 2, 2, 3],
    "gypsy": [1, 3, 1, 2, 1, 3, 1],
    "overtone": [2, 2, 2, 1, 2, 1, 2],
    "equable": [1, 2, 2, 2, 1, 2, 2],
    "perc": perc_list,
    "tabla": [41, 42, 43, 44, 45, 46, 47, 50],
    "GMKit": [36, 37, 38, 42, 44, 46, 48],
    "TR808": [36, 37, 38, 44, 45, 46, 47],
    "HardElectro": list(range(36, 52, 1)),
}

# nicknames:
for name, nickname in [
    ("pent", "pentatonic"),
    ("octa", "octatonic"),
    ("overt", "overtone"),
    ("wht", "whole_tone"),
    ("chrom", "chromatic"),
]:
    scale_vectors[name] = scale_vectors[nickname]

# our percussion scales:
perc_scales = ["perc", "tabla", "GMKit", "TR808", "HardElectro"]

######################
# microtonal scales: #
######################
# helper function
def note_and_bend(mycents, middle_note=60):
    """Take a cent value and return a MIDI note and bend.

    Scale to '0 cents = middle-C' if middle_c=True.
    """
    note, remain = divmod(mycents + 50, 100.0)
    note = int(note + middle_note)
    bend = 8192 + int(round((remain - 50) * 40.96))
    return note, bend


def cents(x):
    return log2(x) * 1200.00


microtonal_vectors = {}

microtonal_vectors["edo5"] = [note_and_bend(x / 5.0 * 1200.0) for x in range(-15, 20)]

microtonal_vectors["otonal"] = [
    note_and_bend(x)
    for x in [
        cents(y)
        for y in [
            1 / 4.0,
            1 / 3.0,
            3 / 8.0,
            1 / 2.0,
            2 / 3.0,
            3 / 4.0,
            1,
            5 / 4.0,
            3 / 2.0,
            7 / 4.0,
            2,
            9 / 4.0,
            5 / 2.0,
            11 / 4.0,
            3,
            13 / 4.0,
            14 / 4.0,
            15 / 4.0,
            4.0,
        ]
    ]
]

microtonal_vectors["utonal"] = [
    note_and_bend(x)
    for x in [
        cents(y)
        for y in [
            1 / 4.0,
            1 / 3.0,
            3 / 8.0,
            1 / 2.0,
            2 / 3.0,
            3 / 4.0,
            1,
            6 / 5.0,
            3 / 2.0,
            12 / 7.0,
            2,
            24 / 11.0,
            12 / 5.0,
            8 / 3.0,
            3,
            16 / 5.0,
            24 / 7.0,
            24 / 13.0,
            4.0,
        ]
    ]
]


# an "overtone" scale that is based on 21\34-edo 8-note scale,
# distributed freq-wise ala an overtone series.
microtonal_vectors["fibotonal"] = [
    note_and_bend(x)
    for x in [
        cents(y)
        for y in [
            0.125,
            0.25,
            0.3835926703400558,
            0.5,
            0.6256941028120465,
            0.7671853406801116,
            0.90308968739698,
            1.0,
            1.1771466939089177,
            1.251388205624093,
            1.3856743389806951,
            1.5343706813602231,
            1.6311419669655505,
            1.80617937479396,
            2.0,
            2.1261380796451856,
            2.3542933878178354,
            2.502776411248185,
            2.7713486779613903,
            3.0687413627204454,
            3.262283933931101,
            3.6123587495879192,
            4.0,
            4.252276159290371,
            4.708586775635671,
            5.00555282249637,
            5.542697355922781,
            6.137482725440891,
            6.524567867862202,
            7.2247174991758385,
            8.0,
        ]
    ]
]


# a place to keep our microtonal scales:
microtonal_scales = ["edo5", "otonal", "utonal", "fibotonal"]
#############################
# end microtonal scale code #
#############################


def create_scale(vectors_str, min=0, max=127):
    """Create a full-range scale in MIDI note numbers
    from a vector set and a range"""
    notes = [min]
    cur = min
    while cur <= max:
        for v in scale_vectors[vectors_str]:
            cur += v
            notes.append(cur)
    return notes


class MidiScale:
    """Create a master scale object so we don't have to worry about range
    issues.  Folds in the bounce method, mode and transposition, etc.
    """

    def __init__(self, vectors_str="pent", min=48, max=72, trans=0):
        global perc_scales, microtonal_scales
        self.min = min if min >= 0 else 0
        self.max = max if max <= 127 else 127
        self.trans = trans
        self.set_scl(vectors_str)

    def set_scl(self, vectors_str):
        if vectors_str in perc_scales:
            self.master_scale = scale_vectors[vectors_str]
            self.slave = scale_vectors[vectors_str]
            self.size = len(self.slave)
            self.get_note = self._get_regular_note
        elif vectors_str in microtonal_scales:
            self.master_scale = microtonal_vectors[vectors_str]
            self.slave = microtonal_vectors[vectors_str]
            self.size = len(self.slave)
            self.min = self.slave[0][0]
            self.max = self.slave[-1][0]
            self.get_note = self._get_microtonal_note
        else:
            self.master_scale = create_scale(vectors_str)
            self.get_note = self._get_regular_note
            self._update_slave()

    def set_min_max_trans(self, min, max, trans):
        if min < 0:
            min = 0
        if max > 127:
            max = 127
        self.min = min
        self.max = max
        self.trans = trans
        self._update_slave()

    def set_min(self, min):
        if min < 0:
            min = 0
        self.min = min
        self._update_slave()

    def set_max(self, max):
        if max > 127:
            max = 127
        self.max = max
        self._update_slave()

    def set_trans(self, trans):
        self.trans = trans
        self._update_slave()

    def _update_slave(self):
        if self.min > self.max:
            self.min = 48
            self.max = 72
        if self.get_note != self._get_microtonal_note:
            self.slave = [n for n in self.master_scale if self.min <= n <= self.max]
        else:
            self.slave = [n for n in self.master_scale if self.min <= n[0] <= self.max]
        self.size = len(self.slave)

    def _get_microtonal_note(self, input_int):
        outnote, outbend = self.slave[see_saw(input_int, self.size - 1)]
        outnote = outnote + self.trans
        if outnote < 0:
            outnote = 0
        elif outnote > 127:
            outnote = 127
        return outnote, outbend

    def _get_regular_note(self, input_int):
        outnote = self.slave[see_saw(input_int, self.size - 1)] + self.trans
        if outnote < 0:
            outnote = 0
        elif outnote > 127:
            outnote = 127
        return outnote
