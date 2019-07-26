"""This module contains code for generating common musical scales
for use with MIDI."""

from pystepseq.lib.midi_functions import see_saw

# gaps between neighboring ascending notes, '0' is an assumed starting point.
chromatic = [1]
whole_tone = [2]
octatonic = [2, 1]
modal = [2, 2, 1, 2, 2, 2, 1]
pentatonic = [2, 3, 2, 2, 3]
gypsy = [1, 3, 1, 2, 1, 3, 1]
overtone = [2, 2, 2, 1, 2, 1, 2]
equable = [1, 2, 2, 2, 1, 2, 2]

# nicknames:
pent = pentatonic
octa = octatonic
overt = overtone
wht = whole_tone
chrom = chromatic

# percussion scales:
perc = list(range(28, 52))
perc.extend([54, 58, 59, 61, 67, 68, 69, 70, 73, 74, 75, 77, 78, 79, 80])
perc.remove(49)
tabla = [41, 42, 43, 44, 45, 46, 47, 50]
GMKit = [36, 37, 38, 42, 44, 46, 48]
TR808 = [36, 37, 38, 44, 45, 46, 47]
HardElectro = list(range(36, 52, 1))


######################
# microtonal scales: #
######################
# helper function
def note_and_bend(mycents, middle_c=True):
    """Take a cent value and return a MIDI note and bend.

    Scale to '0 cents = middle-C' if middle_c=True.
    """
    note, remain = divmod(mycents + 50, 100.0)
    if middle_c:
        note = int(note + 60)  # 0 = "MIDI middle-C"
    else:
        note = int(note)
    bend = 8192 + int(round((remain - 50) * 40.96))
    return note, bend


edo5 = [note_and_bend(x / 5. * 1200.0) for x in range(-15, 20)]

perc_scales = [perc, tabla, GMKit, TR808, HardElectro]

microtonal_scales = [edo5]


def create_scale(vectors, min=0, max=127):
    """Create a full-range scale in MIDI note numbers
    from a vector set and a range"""
    notes = [min]
    cur = min
    while cur <= max:
        for v in vectors:
            cur += v
            notes.append(cur)
    return notes


class MidiScale:
    """Create a master scale object so we don't have to worry about range
    issues.  Folds in the bounce method, mode and transposition, etc.
    """
    def __init__(self, vectors=pent, min=48, max=72, trans=0):
        global perc_scales, microtonal_scales
        self.min = 48
        self.max = 72
        self.trans = 0
        self.set_scl(vectors)

    def _update_slave(self):
        if (self.min > self.max):
            self.min = 48
            self.max = 72
        self.slave = [
            n for n in self.master_scale if self.min <= n <= self.max
        ]
        self.size = len(self.slave)

    def set_min_max_trans(self, min, max, trans):
        if min < 0:
            min = 0
        if max > 127:
            max = 127
        self.min = min
        self.max = max
        self.trans = trans
        self._update_slave()

    def smmt(self, min, max, trans):
        # alias
        self.set_min_max_trans(min, max, trans)

    def set_min(self, min):
        if min < 0:
            min = 0
        self.min = min
        self._update_slave()

    def sm(self, min):
        # alias
        self.set_min(min)

    def set_max(self, max):
        if max > 127:
            max = 127
        self.max = max
        self._update_slave()

    def sx(self, max):
        # alias
        self.set_max(max)

    def set_trans(self, trans):
        self.trans = trans
        self._update_slave()

    def st(self, trans):
        # alias
        self.set_trans(trans)

    def set_scl(self, vectors):
        if vectors in perc_scales:
            self.master_scale = vectors
            self.slave = vectors
            self.size = len(self.slave)
            self.get_note = self._get_regular_note
        elif vectors in microtonal_scales:
            self.master_scale = vectors
            self.slave = vectors
            self.size = len(self.slave)
            self.get_note = self._get_microtonal_note
        else:
            self.master_scale = create_scale(vectors)
            self.get_note = self._get_regular_note
            self._update_slave()

    def ss(self, vectors):
        # alias
        self.set_scl(vectors)

    def _get_microtonal_note(self, input_int):
        outnote, outbend = self.slave[see_saw(input_int + self.trans,
                                              self.size - 1)]
        return outnote, outbend

    def _get_regular_note(self, input_int):
        outnote = self.slave[see_saw(input_int, self.size - 1)] + self.trans
        if outnote < 0:
            outnote = 0
        elif outnote > 127:
            outnote = 127
        return outnote
