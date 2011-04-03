import sys
sys.path.append('pylib')

import re
import os

import clr
clr.AddReference('gtk-sharp')
import Gtk
clr.AddReference('glade-sharp')
import Glade

def PyGladeAutoconnect(gxml, target):
    def _connect(handler_name, event_obj, signal_name, *args):
        name = ''.join([frag.title() for frag in signal_name.split('_')])
        event = getattr(event_obj, name)
        event += getattr(target, handler_name)

    # add all widgets
    for widget in gxml.GetWidgetPrefix(''):
        setattr(target, gxml.GetWidgetName(widget), widget)
    # connect all signals
    gxml.SignalAutoconnectFull(_connect)

class Application:
    def __init__(self):
        gxml = Glade.XML("gui.glade", "window1", None)
        PyGladeAutoconnect(gxml, self)
        # window1 comes from glade file
        self.window1.ShowAll()

    def onWindowDelete(self, o, args):
        # connected via glade file definition
        Gtk.Application.Quit()


if __name__ == '__main__' or True:
    print("Python running: %s" % __file__)

    Gtk.Application.Init()
    app = Application()
    Gtk.Application.Run()
