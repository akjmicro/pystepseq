def _pager(long_string):
    count = 0
    for l in long_string.splitlines():
        count += 1
        print(l)
        if count == 22:
            input("hit enter for more...")
            count = 0


def help():
    helpstring = """commands:

=t   # create a tempotrigger thread
t/   # run a tempotrigger thread
t\\   # stop a tempotrigger thread (immediately with 't\\\\')
tt48 # change the default number of ticks per beat to 48 (default 24)
     # can be any number
t114   # set tempo to QN=114
=a   # adds a new voice, 'a'
=a4  # adds a new voice called 'a', but on MIDI channel 4 (0-15)
-a   # stops and deletes 'a'
zxdrums  # sets up two drum voices, 'z' for bass drum and 'x' for everything
         # else percussive. Must coordinate these against MIDI drum
         # instruments, e.g. Hydrogen or some program triggering drum sounds
         # at a given MIDI channel
##########################################################################
# The following examples assuming you are targeting a voice called 'a'   #
# if you are NOT, and it's 'b' (or something else), you'd make the first #
# charcter 'b', e.g. 'bm48' (from the example below listed as 'am48')    #
##########################################################################
a\\     # silence 'a' (immediate with 'a\\\\')
a/     # bring in a (immediate with 'a//')
z/     # if you've established a bass drum voice, bring it in
x/     # if you've established an 'everything else percussion voice', bring
       # it in
`a,b,c # call 'change' on the listed voices
asBLAH # set a voice's scale to BLAH (pent, modal, chroma[tic], etc.)
am48   # minimum note on voice 'a' is 48
ax62   # maximum note on voice 'a' is 62
at-12  # transposition of voice 'a' is -12
amd4   # modal transposition of voice a is 4 scale steps
ai48,62,-12 # min max and transposition all at once
arn      # randomize notes
annbrown # a's note noise type (brown, white, pink)
and5     # a's random note depth is now 5
arv      # randomize volumes
arg      # randomize gates (% of rhythm length that holds, for articulation)
ap30     # on next 'rv' call, 30% of notes are rests
avnpink  # a's volume noise type (brown, white, pink)
avd16    # a's random volumn depth is now 16
abb48    # reset the number of trigger events that represent a 'beat'
         # this example now executes changing the 'atomic unit' to 1/48th of a 'quarter note'
         # (assuming we call our beat a 'quarter note')
ab5      # change the number of beats in a 'measure' e.g. 5 quarter notes
arl[6,6,12,24]       # randomize lengths, choosing from the attached list
                     # in this example, if there are 24 pulses in a 'quarter note', we have
                     # two 16th notes, an 8th note, and a quarter note.
af[1,5,6,7,3],3,12,0  # fractal noise, takes 3 params:
                      # initial seed list, # layers, length of result, transposition
an[x^17 - 34 for x in range(32)] # evaluate math to populate an list
                                 # must end up being integers....
ae12     # loop back the cycle after the 12th note.
##################################
# riff and song save and recall: #
##################################
q4   # save what's going on to slot 4
4    # replace what's playing with the contents of slot 4
load mysong # replace all slots with the contents of the file 'mysong'
save mysong # save all slots to the file 'mysong'

To quit pystepseq, hit CTRL-C, then type quit()
"""
    _pager(helpstring)
