# Copyright: Martin Matusiak <numerodix@gmail.com>

from __future__ import absolute_import

from nametrans import io


class RenameException(Exception):
    pass

class RegularExpressionError(Exception):
    pass


def error_handler(exc):
    msg = ' '.join(exc.args)
    io.writeln("%s: %s" % (exc.__class__.__name__, msg))

def _get_progress_line(*args):
    action, arg = args[0], ''
    if len(args) > 1:
        arg = " ".join(args[1:])

    def get_line(action, arg):
        line = "%s %s" % (action, arg)
        return line

    linelen = io.LINEWIDTH
    space = 1
    padding = 3

    line = get_line(action, arg)
    if len(line) > linelen:
        width = linelen - len(action) - space - padding
        arg = '.' * padding + arg[-width:]
        line = get_line(action, arg)

    line = line.ljust(linelen)
    return line

def progress(*args):
    line = _get_progress_line(*args)
    io.write(line + '\r')
