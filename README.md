## pystepseq

A commandline musical step-sequencer with some advanced features.

### TO INSTALL:
____________

* Make sure you have Python installed

* Choose as install method, *pip* or *git* (pip is recommended if you have it)

**From pip:**
```
    pip install pystepseq
```
__________________________________

**From git:**

Either download from the 'dist' directory here, or:
```
    git clone https://github.com/akjmicro/pystepseq
```
Once downloaded, in the 'pystepseq' directory:
```
    python setup.py install
```
___________________________________

* Files will be installed into a Python lib directory on your system. E.G.,
on a Linux system, something like `/usr/local/lib/Python3.8`

* Set an environment variable called `PYSTEPSEQ_MIDI_PORT` for a default midi device/port.
  For example, in Linux, using the `bash` shell, you could add the following to your `~/.bashrc`:

```
    export PYSTEPSEQ_MIDI_PORT=/dev/snd/midiC1D0
```

Use a tool like `amidi -l` to find which particular device on your system should be the target of
`pystepseq`'s output. For example, `hw:1,0` would correspond to `/dev/snd/midiC1D0`


* You may also want to edit the variables at the top of the 'constants.py'
These will reflect what MIDI port you are using (e.g., on Linux, 
'/dev/snd/midiC1D0') and also the multicast port you will be broadcasting
the metronome on (and the listeners listening on). Default is 8123.

### Post-install SETUP:

* YOU NEED TO SETUP YOUR COMPUTER FOR MULTICASTING VIA LOOPBACK.

Here's how it's done on Linux (I don't know about anywhere else, sorry):

```
    route add -net 224.0.0.0 netmask 240.0.0.0 dev lo
```

IF YOU DON'T DO THE ABOVE STEP, NO MIDI NOTES WILL BE TRIGGERED! The
metronome (tempotrigger.py) is dependant on the network multicasting for
functionality.

* YOU NEED TO MAKE SURE YOUR MIDI INSTRUMENTS ARE RECEIVING.

Of course, set up your software (or hardware) synths to be listening on the
same MIDI port you have set up pystepseq to push MIDI messages to. It is
beyond the scope of this help to show you how to do that, since all synths
differ. But as an example, you might set qjackctl to take the output of a
virtual MIDI port (e.g. '/dev/snd/midiC1D0', which will show up in a tool
like qjackctl as 'Virtual Raw Midi 1-0') and patch it to the MIDI input of
the synth/sampler of your choice.


### Running:

You should be fine simply starting the script and using the online help.

To start pystepseq, do the following from the commandline:

```
    pystepseq
```

You will see a prompt:

```
    pystepseq('h' for help)-->
```

This will create a new voice called 'a' if you type what is after the prompt:

```
    pystepseq('h' for help)--> =a
```

This will start 'a' playing after a brief pause until the clock is lined up
to a certain beat start:

```
    pystepseq('h' for help)--> a/
```

This will stop 'a' playing after all its current cycle is exhausted:

```
    pystepseq('h' for help)--> a\
```

The online help will give you a hang of the rest of the commands. The system
is designed to be succint, in that all the commands have been designed to
minimize typing, and are usually a single character, or two-character
mnemonic. So for instance, "Take voice 'a' and randomize its volume
sequence" would be:

```
    pystepseq('h' for help)--> arv
```

...which stands for " 'a' random volumes "

Much more sense will be had once you play with it via the online help.

Enjoy!

Aaron Krister Johnson

Please report bugs and successes to akjmicro@gmail.com
