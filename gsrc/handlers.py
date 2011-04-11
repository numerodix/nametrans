# Author: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

import clr

clr.AddReference('gtk-sharp'); import Gtk
clr.AddReference('gdk-sharp'); import Gdk

from lib import ansicolor

import src.callbacks

def get_error_handler_gui(buf, nametrans=False):
    def append_func(s):
        Gdk.Threads.Enter()
        rit = clr.Reference[Gtk.TextIter](buf.EndIter)
        buf.Insert(rit, s)
        Gdk.Threads.Leave()

    def join_nonempty(sep, *args):
        args = filter(lambda s: s != '', args)
        return sep.join(args)

    if nametrans:
        def error_handler_gui(exc):
            msg = ' '.join(exc.args)
            s = "<em>%s: %s</em>\n" % (exc.__class__.__name__, msg.strip())
            append_func(s)
        return error_handler_gui

    else:
        def error_handler_gui(args):
            exc = args.ExceptionObject.InnerException
            st = '' # exc.StackTrace   # XXX omit
            msg = "<em>Error: %s</em>" % exc.Message
            s = '%s\n' % join_nonempty('\n', st.strip(), msg.strip())
            append_func(s)
        return error_handler_gui

def get_progress_handler_gui(label):
    linelen = 50
    def progress_handler_gui(*args):
        msg = src.callbacks._get_progress_msg(linelen, *args)
        Gdk.Threads.Enter()
        label.Text = msg
        Gdk.Threads.Leave()
    return progress_handler_gui

def error_handler_terminal(args):
    exc = args.ExceptionObject.InnerException
    st = exc.StackTrace
    msg = "Error: %s" % exc.Message
    msg = ansicolor.red(msg)
    s = "%s\n%s" % (st, msg)
    print(s)


