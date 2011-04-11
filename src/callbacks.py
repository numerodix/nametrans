# Author: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

def error_handler(exc):
    msg = ' '.join(exc.args)
    print("%s: %s" % (exc.__class__.__name__, msg))

