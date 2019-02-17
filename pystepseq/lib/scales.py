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

perc_scales = [perc, tabla, GMKit, TR808, HardElectro]


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
        global perc_scales
        if vectors not in perc_scales:
            self.master_scale = create_scale(vectors)
            self.set_min_max_trans(min, max, trans)
        else:
            self.master_scale = vectors
            self.slave = vectors

    def _update_slave(self):
        if (self.min > self.max):
            self.min = 48
            self.max = 72
        self.slave = [n for n in self.master_scale if n >= self.min and
                      n <= self.max]
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
        if vectors not in perc_scales:
            self.master_scale = create_scale(vectors)
            self._update_slave()
        else:
            self.master_scale = vectors
            self.smmt(36, 60, 0)

    def ss(self, vectors):
        # alias
        self.set_scl(vectors)

    def get_note(self, input_int):
        outnote = self.slave[see_saw(input_int, self.size - 1)] + self.trans
        if outnote < 0:
            outnote = 0
        elif outnote > 127:
            outnote = 127
        return outnote
