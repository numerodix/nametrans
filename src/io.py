# Author: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

import sys

LINEWIDTH = 78

def write(s):
    sys.stdout.write(s)
    sys.stdout.flush()

def writeln(s):
    write(s+'\n')

def clear_line():
    write(LINEWIDTH*" "+"\r")

