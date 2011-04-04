# <Init>

# runtime bootstrap
import clr
import System

# py modules provided by runtime
import sys

# set up path to import pylib
def get_path_of_executable():
    path = System.IO.Path.GetDirectoryName(
        System.Reflection.Assembly.GetExecutingAssembly().GetName().CodeBase)[5:]
    if path.startswith('\\'):
        path = path[1:]
    return path

path = get_path_of_executable()
for d in ['.', 'pylib']:
    sys.path.append(System.IO.Path.Combine(path, d))

# </Init>

clr.AddReference('gtk-sharp')
import Gtk
clr.AddReference('glade-sharp')
import Glade
clr.AddReference('gdk-sharp')
import Gdk
clr.AddReference('glib-sharp')
import GLib

import os
import re

sys.version = 'ironpython' # is unset when python is hosted on .NET
import nametrans
from src import nametransformer
from src.nametransformer import NameTransformer


def pygladeAutoconnect(gxml, target):
#    def _connect(handler_name, event_obj, signal_name, *args):
#        name = ''.join([frag.title() for frag in signal_name.split('_')])
#        event = getattr(event_obj, name)
#        event += getattr(target, handler_name)

    # add all widgets
    for widget in gxml.GetWidgetPrefix(''):
        setattr(target, gxml.GetWidgetName(widget), widget)

    # connect all signals
#    gxml.SignalAutoconnectFull(_connect)

class Application:
    def __init__(self):
        mypath = os.path.dirname(__file__)
        gxml = Glade.XML(os.path.join(mypath, "gui.glade"), "mainwindow", None)
        pygladeAutoconnect(gxml, self)

        window_x = 500

        self.mainwindow.SetDefaultSize(window_x, 360)

        # events that trigger application exit
        self.mainwindow.DeleteEvent += self.onWindowDelete
        self.button_quit.Clicked += self.onWindowDelete

        # events that trigger re-scanning files
        self.mainwindow.Realized += self.do_compute # XXX
        self.selector_path.CurrentFolderChanged += self.do_compute

        self.button_compute.Clicked += self.do_compute

        self.button_apply.Clicked += self.do_apply

        self.fileview.Reorderable = False
        self.fileview.AppendColumn("From", Gtk.CellRendererText(),
                                   "text", 0, "background", 2)
        self.fileview.AppendColumn("To", Gtk.CellRendererText(),
                                   "text", 1, "background", 3)
        for col in self.fileview.Columns:
            col.MinWidth = window_x / 2

        self.options, _, _ = nametransformer.get_opt_parse([])
        self.program = None
        self.items = []

        self.mainwindow.ShowAll()

    def onWindowDelete(self, o, args):
        Gtk.Application.Quit()

    def set_file_list(self, items):
        store = Gtk.ListStore(str, str, str, str)
        for item in items:
            col_f, col_g = "white", "white"
            if item.invalid:
                col_f = "#fd7f7f"
                col_g = col_f
            store.AppendValues(item.f, item.g, col_f, col_g)
        self.fileview.Model = store

    def do_compute(self, o, args):
        self.options.flag_recursive = True
        self.options.flag_neater = True

        selected_path = self.selector_path.CurrentFolder
        os.chdir(selected_path)
        self.program = nametrans.Program(self.options)

        items = self.program.nameTransformer.scan_fs()
        items = self.program.nameTransformer.process_items(items)
        self.items = items

        self.set_file_list(self.items)

    def do_apply(self, o, args):
        self.program.perform_renames(self.items)


if __name__ == '__main__' or True:
    print("Python armed. Executing %s" % __file__)

    def f(args):
        print args.ExceptionObject
    GLib.ExceptionManager.UnhandledException += f

    Gtk.Application.Init()
    app = Application()
    Gtk.Application.Run()
