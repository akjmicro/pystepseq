def help():
    helpstring = '''commands:

=t   # create a tempotrigger thread
t/   # run a tempotrigger thread
t\   # stop a temportrigger thread (immediately with 't\\\\')
tt48 # change the default number of ticks per beat to 48 (default 24)
     # can be any number
t114   # set tempo to Q=114
=a   # adds a new voice, 'a'
=a4  # adds a new voice called 'a', but on MIDI channel 4 (0-15)
-a   # stops and deletes 'a'
zxdrums  # sets up two drum voices, 'z' for bass drum and 'x' for everything
         # else percussive. Must coordinate these against MIDI drum instruments,
         # e.g. Hydrogen or some program triggering drum sounds at a given
         # MIDI channel
##########################################################################
# The following examples assuming you are targeting a voice called 'a'   #
# if you are NOT, and it's 'b' (or something else), you'd make the first #
# charcter 'b', e.g. 'bm48' (from the example below listed as 'am48')    #
##########################################################################
a\     # silence 'a' (immediate with 'a\\\\')
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
ap30     # on next 'rv' call, 30% of notes are rests
avnpink  # a's volume noise type (brown, white, pink)
avd16    # a's random volumn depth is now 16
arl[6,6,12,24]       # randomize lengths, choosing from the attached list
af12,[1,5,6,7,3],3   # fractal noise, takes 3 params:
                     # length of result, initial seed list, num. of layers
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
'''
    print(helpstring)
