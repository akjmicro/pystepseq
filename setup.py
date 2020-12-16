import pathlib
from setuptools import setup, find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
    name="pystepseq",
    version="2.0.0",
    description=("A multi-featured commandline interface MIDI step sequencer"),
    long_description=README,
    long_description_content_type="text/markdown",
    author="Aaron Krister Johnson",
    author_email="akjmicro@gmail.com",
    url="https://github.com/akjmicro/pystepseq",
    packages=find_packages(),
    package_data={"": ["LICENSE.txt", "README.md", "share/demo_pickles/*"]},
    entry_points={"console_scripts": ["pystepseq=pystepseq.main:repl"]},
)
