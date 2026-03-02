# Copyright: Martin Matusiak <numerodix@gmail.com>

from __future__ import absolute_import

import sys


LINEWIDTH = 78

def write(s: str) -> None:
    sys.stdout.write(s)
    sys.stdout.flush()

def writeln(s: str) -> None:
    clear_line()
    write(s + '\n')

def clear_line() -> None:
    write(LINEWIDTH * ' ' + '\r')
