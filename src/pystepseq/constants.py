import os

DEFAULT_MIDI_DEVNUM = int(os.getenv("PYSTEPSEQ_MIDI_DEVNUM", "0"))
DEFAULT_MULTICAST_PORT = int(os.getenv("PYSTEPSEQ_MULTICAST_PORT", "8123"))
