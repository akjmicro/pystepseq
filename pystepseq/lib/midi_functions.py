#!/usr/bin/python3

from operator import xor

_port = None


def open_port(dummy_arg):
    global _port
    _port = open(dummy_arg, "wb")
    if _port:
        print("Open successful")
    else:
        print("Open failed")


# only for Linux, to make the Mac-style simplecoremidi API work:
def send_midi(input_tuple):
    global _port
    _port.write(
        bytes("%c%c%c" % (input_tuple[0], input_tuple[1], input_tuple[2]), "latin-1")
    )
    _port.flush()


def pitch_bend(channel, bend):
    low_byte = bend & 127
    high_byte = bend >> 7
    send_midi((0xE0 + channel, low_byte, high_byte))


def pb(channel, bend):
    #   bend = int((bend - 8192.0)/128)
    send_midi((0xE0 + channel, 0x00, (bend % 128)))


def note_on(channel, note, volume):
    send_midi((0x90 + channel, note, volume))


def note_off(channel, note):
    send_midi((0x90 + channel, note, 0))


def program_change(channel, program):
    send_midi((0xC0 + channel, program % 127, 0))


def control(channel, controller, value):
    send_midi((0xB0 + channel, controller, value))


def all_notes_off():
    for channel in range(16):
        send_midi((0xB0 + channel, 123, 0))


def sysex_tuning_dump_12(tuning, bank, preset, name):
    """sysex_tuning_dump_12(tuning, bank, preset, name)
send F0 7E <device ID> 08 06 bb tt <tuning name> [xx yy] ... chksum F7
MIDI SYSEX message to the open device"""
    data = [0xF0, 0x7E, 0x7F, 8, 6, bank, preset]
    for c in name:
        data.append(ord(c))
    for n in tuning:
        n = int(round((n + 100) * 81.92))
        least_significant = n & 0x7F
        most_significant = n >> 7
        data.append(most_significant)
        data.append(least_significant)
    chksum = 0x7E
    for d in data[2:]:
        chksum = xor(chksum, d)
    data.append(chksum & 0x7F)
    data.append(0xF7)
    for d in data:
        send_midi("%c" % d)
    print(data)


def close_port():
    _port.close()


# standard midi file functions:


def read_var_length(fp):
    """ take a file pointer that will presumably read characters from the
    pointed-to file, and return a numeric value. """

    # set the variable to which we will add:
    output = 0

    # read the first byte
    inbyte = ord(fp.read(1))

    # its real value is really only the lowest 7 bits, so mask it
    # against 0x7f via logical AND.
    output = inbyte & 0x7F

    # if the highest bit is set, move on to the next bit
    while inbyte & 0x80 == 0x80:
        inbyte = ord(fp.read(1))
        # shift left 7 bits, and add the next masked value to it.
        output = (output << 7) + (inbyte & 0x7F)

    # this output value will be a numeric type:
    return output


def write_var_length(var):
    """ Take a numerical value, and convert it to a 7-bit packed string
    with high bit of each byte set as a flag to indicate to the reader that
    the value that follows in the following byte is to be consumed as well.
    """
    # Result goes into an array. Since we are starting with the least
    # significant byte, we will eventually have to reverse this to correctly
    # order the output character bytes:
    result_array = []

    # We have at least one value, right? :
    result_array.append(var & 0x7F)
    var >>= 7  # shift right

    # If 'var' still has any value greater than 0, 'and' it with 0x7f and
    # then 'or' with 0x80, then put it out to result.  Then we shift right
    # for the next iteration:
    while var > 0x0:
        result_array.append((var & 0x7F) | 0x80)
        var >>= 7

    # Reverse the array, after all, we *did* put the least significant byte
    # in their first!
    result_array.reverse()

    # Make an empty list of to gather the values appended as characters.
    # Return the string-joined array:
    hex_string_array = []
    for n in result_array:
        hex_string_array.append(chr(n))
    return "".join(hex_string_array)


# range protection functions:


def bounce(index, max):
    a, b = divmod(index, max)
    if a % 2 == 1:
        b = (max - 1) - b
    return b


def see_saw(index, max):
    index, max = int(index), int(max)
    f = index % (max * 2)
    if f >= max:
        return max - (index % max)
    return f


# t2mf functions


def midi_text_open(file, midi_file_type, num_channels, resolution):
    global text_file
    text_file = open(file, "w")
    text_file.write(
        "MFile %i %i %i\nMTrk\n" % (midi_file_type, num_channels, resolution)
    )


def midi_text_close():
    global text_file
    text_file.close()


def midi_text_new_channel():
    global text_file
    text_file.write("TrkEnd\nMTrk\n")


def midi_text_final_trkend():
    global text_file
    text_file.write("TrkEnd\n")


def midi_text_pitch_bend(time, channel, bend):
    global text_file
    text_file.write("%i Pb ch=%i v=%i\n" % (time, channel + 1, bend))


def midi_text_note_on(time, channel, note, volume):
    global text_file
    text_file.write("%i On ch=%i n=%i v=%i\n" % (time, channel + 1, note, volume))


def midi_text_note_off(time, channel, note):
    global text_file
    text_file.write("%i Off ch=%i n=%i v=0\n" % (time, channel + 1, note))


def midi_text_tempo(time, tempo):
    global text_file
    tempo = int((60.0 / tempo) * 1000000)
    text_file.write("%i Tempo %i\n" % (time, tempo))


def midi_text_program_change(time, channel, program):
    global text_file
    text_file.write("%i PrCh ch=%i p=%i\n" % (time, channel + 1, program))


def midi_text_controller(time, channel, parameter, value):
    global text_file
    text_file.write("%i Par ch=%i c=%i v=%i\n" % (time, channel + 1, parameter, value))


# END
