from typing import List

# Import all commands in the folder here
from lib.command import Command
from .start import StartCommand
from .help import HelpCommand
from .count import CountCommand
from .generate import GenerateCommand
from .jpeg import JpegCommand
from .demotivate import DemotivateCommand

COMMANDS: List[Command] = [
    StartCommand,
    HelpCommand,
    CountCommand,
    GenerateCommand,
    JpegCommand,
    DemotivateCommand
]
