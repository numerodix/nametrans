# Author: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

### <Init>

print("Python armed. Executing %s" % __file__)

# runtime bootstrap
import clr
import System

# py modules provided by runtime
import sys

# set sys.argv from variable set in hosting runtime
if hasattr(sys.modules[__name__], '__SYS_ARGV'):
    sys.argv = []
    for i in __SYS_ARGV:
        sys.argv.append(i)
    del(__SYS_ARGV)

    # check that sys.argv[0] == __file__
    if len(sys.argv) == 0 or sys.argv[0] != __file__:
        sys.argv.insert(0, __file__)

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
del(path)

### </Init>

clr.AddReference('glade-sharp'); import Glade
clr.AddReference('gtk-sharp'); import Gtk
clr.AddReference('gdk-sharp'); import Gdk
clr.AddReference('glib-sharp'); import GLib

import os
import re

sys.version = 'ironpython' # is unset when python is hosted on .NET
import nametrans
from src import nametransformer
from src.nametransformer import NameTransformer

from guisrc.gtkhelper import GtkHelper


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

class Application(object):
    def __init__(self):
        self.gtkhelper = GtkHelper()

        self.error_color_fg = "#ff0000"
        self.error_color_bg = "#fd7f7f"

        self.init_model()
        self.init_glade()
        self.init_signals()
        self.init_gui()
        self.run_gui()

    def init_glade(self):
        mypath = os.path.dirname(__file__)
        gxml = Glade.XML(os.path.join(mypath, "gui.glade"), "mainwindow", None)
        pygladeAutoconnect(gxml, self)

    def init_model(self):
        self.options, _, _ = nametransformer.get_opt_parse(sys.argv)
        self.program = None
        self.items = []

    def init_signals(self):
        # events that trigger application exit
        self.mainwindow.DeleteEvent += self.onWindowDelete
        self.button_quit.Clicked += self.onWindowDelete

        # events that trigger updating the path
        self.mainwindow.Realized += self.onPathChange
        self.selector_path.CurrentFolderChanged += self.onPathChange
        self.text_path.Activated += self.onPathChange
        self.text_path.FocusOutEvent += self.onPathChange

        self.button_compute.Clicked += self.do_compute

        self.button_apply.Clicked += self.do_apply

    def init_gui(self):
        window_x = 500
        window_y = 360

        self.mainwindow.SetDefaultSize(window_x, window_y)

        self.fileview.Reorderable = False
        self.fileview.AppendColumn("From", Gtk.CellRendererText(),
                                   "text", 0, "background", 2)
        self.fileview.AppendColumn("To", Gtk.CellRendererText(),
                                   "text", 1, "background", 3)
        for col in self.fileview.Columns:
            col.MinWidth = window_x / 2

    def run_gui(self):
        self.text_path.Text = os.getcwd()
        self.mainwindow.ShowAll()


    def onWindowDelete(self, o, args):
        Gtk.Application.Quit()


    def onPathChange(self, o, args):
        if o in [self.mainwindow, self.selector_path]:
            path = self.selector_path.CurrentFolder
            if path:
                self.text_path.Text = path
        if o == self.text_path:
            path = self.get_ui_path()
            if path:
                self.selector_path.SetCurrentFolder(path)
        self.do_compute(o, args)

    def set_file_list(self, items):
        store = Gtk.ListStore(str, str, str, str)
        for item in items:
            col_f, col_g = "white", "white"
            if item.invalid:
                col_f = self.error_color_bg
                col_g = col_f
            store.AppendValues(item.f, item.g, col_f, col_g)
        self.fileview.Model = store

    def get_ui_path(self):
        path = self.text_path.Text
        if not path or not os.path.exists(path):
            self.gtkhelper.change_widget_color(self.text_path, self.error_color_fg)
        else:
            self.gtkhelper.reset_widget_color(self.text_path)
            return path


    def do_compute(self, o, args):
        selected_path = self.get_ui_path()
        if selected_path:
            os.chdir(selected_path)
            self.program = nametrans.Program(self.options)

            items = self.program.nameTransformer.scan_fs()
            items = self.program.nameTransformer.process_items(items)
            self.items = items

            self.set_file_list(self.items)

    def do_apply(self, o, args):
        self.program.perform_renames(self.items)


if __name__ == '__main__' or True:
    def f(args):
        print args.ExceptionObject
    GLib.ExceptionManager.UnhandledException += f

    Gtk.Application.Init()
    app = Application()
    Gtk.Application.Run()
