#!/usr/bin/python

from setuptools import setup, find_packages

setup(
    name="pystepseq",
    version="2019.0217a1",
    description=('A multi-featured commandline interface MIDI step sequencer'),
    author='Aaron Krister Johnson',
    author_email='akjmicro@gmail.com',
    url='https://github.com/akjmicro/pystepseq',
    packages=find_packages(),
    package_data={
        '': ['LICENSE.txt', 'README.md', 'README.rst',
             'share/demo_pickles/*']
    },
    entry_points={
        'console_scripts': [
            'pystepseq=pystepseq.main:repl',
        ],
    }
)
