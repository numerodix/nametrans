# Author: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

### <Init>
print("Python armed. Executing %s" % __file__)

# runtime bootstrap
import clr
import System

# py modules provided by runtime
import sys

# set up path to import pylib
for d in ['.', 'pylib']:
    sys.path.append(System.IO.Path.Combine(
        System.IO.Path.GetDirectoryName(__file__), d))

# set PATH to resolve gtk dlls
import os
if System.Environment.OSVersion.Platform.ToString().StartsWith('Win32'):
    path = System.Environment.GetEnvironmentVariable("PATH")
    pypath = os.path.dirname(os.path.abspath(__file__))
    path = "%s;%s" % (path, os.path.join(pypath, 'bin', 'gtk', 'bin'))
    System.Environment.SetEnvironmentVariable("PATH", path)
### </Init>

import System.Diagnostics
import System.Reflection
import System.Threading

clr.AddReference('glade-sharp'); import Glade
clr.AddReference('gtk-sharp'); import Gtk
clr.AddReference('gdk-sharp'); import Gdk
clr.AddReference('glib-sharp'); import GLib

import functools
import re

import nametrans
from src import nametransformer
from src.nametransformer import NameTransformer
import src.callbacks

from gsrc import gtkhelper
from gsrc import handlers
from gsrc.gtkhelper import GtkHelper
from gsrc.widgets.about_dialog import AboutDialog
from gsrc.widgets.fileview_list import FileviewList
from gsrc.widgets.log_window import LogWindow


def pygladeAutoconnect(gxml, target):
#    def _connect(handler_name, event_obj, signal_name, *args):
#        name = ''.join([frag.title() for frag in signal_name.split('_')])
#        event = getattr(event_obj, name)
#        event += getattr(target, handler_name)

    # add all widgets
    for widget in gxml.GetWidgetPrefix(''):
        name = gxml.GetWidgetName(widget)
        # if widget.fileview exists, this class manages the widget,
        # thus bind to widget.fileview.fileview
        if not hasattr(target, name):
            setattr(target, name, widget)
        else:
            subtarget = getattr(target, name)
            setattr(subtarget, name, widget)

    # connect all signals
#    gxml.SignalAutoconnectFull(_connect)

class Application(object):
    def __init__(self):
        self.app_title = "nametrans"

        self.app_path = os.path.dirname(__file__)
        self.app_resource_path = os.path.join(self.app_path, 'resources')
        self.app_license_file = os.path.join(self.app_path, 'doc', 'LICENSE')

        self.app_help_url = "http://www.matusiak.eu/numerodix/blog/index.php/2011/03/25/nametrans-renaming-with-search-replace/"

        self.app_icon = "icon.ico"
        self.app_icon_path = os.path.join(self.app_resource_path, self.app_icon)
        self.glade_file = "forms.glade"
        self.error_color_fg = "#ff0000"

        self.gtkhelper = GtkHelper()

        self.fileview = FileviewList(self)
        self.log = \
            LogWindow(self, functools.partial(self.init_widget, 'logwindow'))
        self.about = \
            AboutDialog(self, functools.partial(self.init_widget, 'aboutdialog'))

        self.init_gui()
        self.init_signals()
        self.run_gui()

    def init_widget(self, name, obj):
        gxml = Glade.XML(os.path.join(self.app_resource_path, self.glade_file),
                         name, None)
        pygladeAutoconnect(gxml, obj)

    def init_model(self):
        self.options, _, optparser = nametransformer.get_opt_parse(sys.argv)
        self.program = None
        self.items = []

        gtkhelper.FieldMap(optparser, self)

    def init_gui(self):
        # init glade
        self.init_widget('mainwindow', self)
        self.fileview.init_widget(self.mainwindow)
        self.log.init_widget()

        # init model
        self.init_model()

        ### Init mainwindow

        self.mainwindow.Title = self.app_title
        self.mainwindow.SetIconFromFile(self.app_icon_path)
        self.mainwindow.SetDefaultSize(600, 500)

        ### Fill in gui from sys.argv input
        self.text_path.Text = (self.options.path and
                               os.path.abspath(self.options.path) or os.getcwd())
        self.text_s_from.Text = self.options.s_from
        self.text_s_to.Text = self.options.s_to
        for (op, widget) in self.get_flags_widgets():
            widget.Active = getattr(self.options, op, False)
        # renseq
        field, width = NameTransformer.parse_renseq_args(self.options.renseq)
        if type(field) == int or type(width) == int:
            self.checkbutton_renseq.Active = True
            if field: self.spinbutton_renseq_field.Value = field
            if width: self.spinbutton_renseq_width.Value = width
        self.onRenseqToggle(self.checkbutton_renseq, None)

        # set up exception handlers
        src.callbacks.error_handler = \
            handlers.get_error_handler_gui(self.log.textview_log.Buffer,
                                           nametrans=True)
        src.callbacks.progress = \
                handlers.get_progress_handler_gui(self.label_progress)

        GLib.ExceptionManager.UnhandledException += \
                handlers.get_error_handler_gui(self.log.textview_log.Buffer)
        GLib.ExceptionManager.UnhandledException -= handlers.error_handler_terminal

    def init_signals(self):
        # events that trigger application exit
        self.mainwindow.DeleteEvent += self.onWindowDelete
        self.button_quit.Clicked += self.onWindowDelete
        self.imagemenuitem_quit.Activated += self.onWindowDelete
        self.imagemenuitem_help.Activated += self.onHelp
        self.imagemenuitem_about.Activated += self.about.onRun

        # events that signal change in input parameters
        self.text_s_from.Activated += self.onParametersChange
        self.text_s_to.Activated += self.onParametersChange
        for (op, widget) in self.get_flags_widgets():
            widget.Toggled += self.onParametersChange
        self.checkbutton_renseq.Toggled += self.onRenseqToggle
        self.spinbutton_renseq_field.ValueChanged += self.onParametersChange
        self.spinbutton_renseq_width.ValueChanged += self.onParametersChange

        # events that trigger updating the path
#        self.mainwindow.Realized += self.onPathChange
        self.selector_path.CurrentFolderChanged += self.onPathChange
        self.text_path.Activated += self.onPathChange
        self.text_path.FocusOutEvent += self.onPathChange

        self.button_log.Clicked += self.log.onToggle
        self.button_compute.Clicked += self.onParametersChange
        self.button_apply.Clicked += self.do_apply

    def run_gui(self):
        self.onPathChange(self.text_path, None)
        self.mainwindow.ShowAll()


    def onWindowDelete(self, o, args):
        Gtk.Application.Quit()

    def onHelp(self, o, args):
        System.Diagnostics.Process.Start(self.app_help_url)


    def onPathChange(self, o, args):
        if o in [self.mainwindow, self.selector_path]:
            path = self.selector_path.CurrentFolder
            if path and path != self.text_path.Text:
                self.text_path.Text = path
                self.do_compute()

        if o == self.text_path:
            path = self.get_ui_path()
            if path and path != self.selector_path.CurrentFolder:
                self.selector_path.SetCurrentFolder(path)
                self.do_compute()

    def get_flags_widgets(self):
        pairs = []
        for op in dir(self.options):
            if op.startswith('flag_'):
                root = re.sub('flag_', '', op)
                widget = getattr(self, 'checkbutton_' + root, None)
                if widget:
                    pairs.append((op, widget))
        return pairs

    def onParametersChange(self, o, args):
        self.options.s_from = self.text_s_from.Text
        self.options.s_to = self.text_s_to.Text

        # flag params
        for (op, widget) in self.get_flags_widgets():
            setattr(self.options, op, widget.Active)

        if self.checkbutton_renseq.Active:
            field = int(self.spinbutton_renseq_field.Value)
            width = int(self.spinbutton_renseq_width.Value)
            if field == 0:
                field = 1
            self.options.renseq = "%s:%s" % (field, width)
        else:
            self.options.renseq = None

        self.do_compute()

    def onRenseqToggle(self, o, args):
        if self.checkbutton_renseq.Active:
            self.spinbutton_renseq_field.Sensitive = True
            self.spinbutton_renseq_width.Sensitive = True
        else:
            self.spinbutton_renseq_field.Sensitive = False
            self.spinbutton_renseq_width.Sensitive = False
        self.onParametersChange(o, args)


    def get_ui_path(self):
        path = self.text_path.Text
        if not path or not os.path.exists(path):
            self.gtkhelper.change_widget_color(self.text_path, self.error_color_fg)
        else:
            self.gtkhelper.reset_widget_color(self.text_path)
            return path


    def do_compute_threaded(self):
        Gdk.Threads.Enter()
        self.fileview.set_file_list([])
        self.label_result.Text = ''
        self.button_compute.Sensitive = False
        self.button_apply.Sensitive = False
        Gdk.Threads.Leave()

        items = self.program.nameTransformer.scan_fs()
        nscanned = len(items)
        items = self.program.nameTransformer.process_items(items)
        naffected = len(items)
        self.items = items

        status = "%s files scanned, %s files affected" % (nscanned, naffected)
        Gdk.Threads.Enter()
        self.label_progress.Text = ''
        self.label_result.Text = status
        self.fileview.set_file_list(self.items)
        self.button_compute.Sensitive = True
        self.button_apply.Sensitive = True
        Gdk.Threads.Leave()

    def do_compute(self):
        path = self.get_ui_path()
        if path:
            os.chdir(path)
            self.program = nametrans.Program(self.options)

            t = System.Threading.Thread(\
                    System.Threading.ThreadStart(self.do_compute_threaded))
            t.Start()


    def do_apply_threaded(self):
        Gdk.Threads.Enter()
        self.button_compute.Sensitive = False
        self.button_apply.Sensitive = False
        Gdk.Threads.Leave()

        self.program.perform_renames(self.items)

        Gdk.Threads.Enter()
        self.button_compute.Sensitive = True
        self.button_apply.Sensitive = True
        Gdk.Threads.Leave()

    def do_apply(self, o, args):
        t = System.Threading.Thread(\
                    System.Threading.ThreadStart(self.do_apply_threaded))
        t.Start()


if __name__ == '__main__' or True:
    GLib.ExceptionManager.UnhandledException += handlers.error_handler_terminal

    GLib.Thread.Init()
    Gdk.Threads.Init()
    Gtk.Application.Init()

    app = Application()

    Gdk.Threads.Enter()
    Gtk.Application.Run()
    Gdk.Threads.Leave()
