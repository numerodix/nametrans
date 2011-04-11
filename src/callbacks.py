# Author: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

import sys

from src import io

def error_handler(exc):
    msg = ' '.join(exc.args)
    io.writeln("%s: %s" % (exc.__class__.__name__, msg))

def _get_progress_msg(linelen, *args):
    action, arg = args[0], ''
    if len(args) > 1:
        arg = " ".join(args[1:])

    def get_line(action, arg):
        line = "%s %s" % (action, arg)
        return line

    space = 1
    padding = 3

    line = get_line(action, arg)
    if len(line) > linelen:
        width = linelen - len(action) - space - padding
        arg = '.'*padding + arg[-width:]
        line = get_line(action, arg)

    line = line.ljust(linelen)
    return line

def progress(*args):
    line = _get_progress_msg(io.LINEWIDTH, *args)
    io.write(line + '\r')
