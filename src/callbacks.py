# Author: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

import sys

def error_handler(exc):
    msg = ' '.join(exc.args)
    print("%s: %s" % (exc.__class__.__name__, msg))

def progress(*args):
    action, arg = args[0], ''
    if len(args) > 1:
        arg = " ".join(args[1:])

    def get_line(action, arg):
        line = "%s %s" % (action, arg)
        return line

    linelen = 78
    space = 1
    padding = 3

    line = get_line(action, arg)
    if len(line) > linelen:
        width = linelen - len(action) - space - padding
        arg = '.'*padding + arg[-width:]
        line = get_line(action, arg)

    line = line.ljust(linelen)

    sys.stdout.write(line + '\r')
    sys.stdout.flush()
