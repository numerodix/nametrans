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

clr.AddReference('glade-sharp'); import Glade
clr.AddReference('gtk-sharp'); import Gtk
clr.AddReference('gdk-sharp'); import Gdk
clr.AddReference('glib-sharp'); import GLib

import functools
import re

import nametrans
from src import nametransformer
from src import fs
from src.nametransformer import NameTransformer

from gsrc import gtkhelper
from gsrc import handlers
from gsrc import markupdiff
from gsrc.gtkhelper import GtkHelper
from gsrc.widgets.about_dialog import AboutDialog
from gsrc.widgets.log_window import LogWindow


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
        self.app_title = "nametrans"

        self.app_path = os.path.dirname(__file__)
        self.app_resource_path = os.path.join(self.app_path, 'resources')
        self.app_license_file = os.path.join(self.app_path, 'doc', 'LICENSE')

        self.app_help_url = "http://www.matusiak.eu/numerodix/blog/index.php/2011/03/25/nametrans-renaming-with-search-replace/"

        self.app_icon = "icon.ico"
        self.app_icon_path = os.path.join(self.app_resource_path, self.app_icon)
        self.glade_file = "forms.glade"
        self.diff_color_left = "#b5b5ff"
        self.diff_color_right = "#b5ffb5"
        self.error_color_fg = "#ff0000"
        self.error_color_bg = "#fd7f7f"

        self.gtkhelper = GtkHelper()

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
        self.log.init_widget()

        # init model
        self.init_model()

        ### Init mainwindow

        self.mainwindow.Title = self.app_title
        self.mainwindow.SetIconFromFile(self.app_icon_path)
        self.mainwindow.SetDefaultSize(600, 500)

        self.fileview.Reorderable = False
        self.fileview.AppendColumn("From", Gtk.CellRendererText(),
                                   "markup", 0, "background", 2)
        self.fileview.AppendColumn("To", Gtk.CellRendererText(),
                                   "markup", 1, "background", 3)
        self.fileview.Model = Gtk.ListStore(str, str, str, str)

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
        fs.error_handler = \
            handlers.get_error_handler_gui(self.log.textview_log.Buffer,
                                           nametrans=True)

        GLib.ExceptionManager.UnhandledException += \
                handlers.get_error_handler_gui(self.log.textview_log.Buffer)
#        GLib.ExceptionManager.UnhandledException -= handlers.error_handler_terminal

    def init_signals(self):
        # events that trigger application exit
        self.mainwindow.DeleteEvent += self.onWindowDelete
        self.button_quit.Clicked += self.onWindowDelete
        self.imagemenuitem_quit.Activated += self.onWindowDelete
        self.imagemenuitem_help.Activated += self.onHelp

        # events that signal window resize
        self.mainwindow.ExposeEvent += self.onWindowResize

        # events that signal change in input parameters
        self.text_s_from.Activated += self.onParametersChange
        self.text_s_to.Activated += self.onParametersChange
        for (op, widget) in self.get_flags_widgets():
            widget.Toggled += self.onParametersChange
        self.checkbutton_renseq.Toggled += self.onRenseqToggle
        self.spinbutton_renseq_field.ValueChanged += self.onParametersChange
        self.spinbutton_renseq_width.ValueChanged += self.onParametersChange

        # events that trigger updating the path
        self.mainwindow.Realized += self.onPathChange
        self.selector_path.CurrentFolderChanged += self.onPathChange
        self.text_path.Activated += self.onPathChange
        self.text_path.FocusOutEvent += self.onPathChange

        self.button_log.Clicked += self.log.onToggle
        self.button_compute.Clicked += self.onParametersChange
        self.button_apply.Clicked += self.do_apply

        # about dialog
        self.imagemenuitem_about.Activated += self.about.onRun

    def onWindowResize(self, o, args):
        window_x = self.fileview.Allocation.Width
        for col in self.fileview.Columns:
            col.MinWidth = (window_x / len(self.fileview.Columns))
            col.Sizing = Gtk.TreeViewColumnSizing.Autosize
        self.fileview.QueueResize()

    def run_gui(self):
        self.onPathChange(self.text_path, None)
        self.mainwindow.ShowAll()


    def onWindowDelete(self, o, args):
        Gtk.Application.Quit()


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

    def set_file_list(self, items):
        self.fileview.Model.Clear()
        style_f = ['<span bgcolor="%s">' % self.diff_color_left, '</span>']
        style_g = ['<span bgcolor="%s">' % self.diff_color_right, '</span>']
        for item in items:
            col_f, col_g = "white", "white"
            if item.invalid:
                col_g = self.error_color_bg
            f, g = markupdiff.diff_markup(item.f, item.g, style_f, style_g)
            wrap = '<span font="8.5"><tt>%s</tt></span>'
            f = wrap % f
            g = wrap % g
            self.fileview.Model.AppendValues(f, g, col_f, col_g)

    def get_ui_path(self):
        path = self.text_path.Text
        if not path or not os.path.exists(path):
            self.gtkhelper.change_widget_color(self.text_path, self.error_color_fg)
        else:
            self.gtkhelper.reset_widget_color(self.text_path)
            return path


    def do_compute(self):
        path = self.get_ui_path()
        if path:
            os.chdir(path)
            self.program = nametrans.Program(self.options)

            self.label_status.Text = "Scanning..."

            items = self.program.nameTransformer.scan_fs()
            nscanned = len(items)
            items = self.program.nameTransformer.process_items(items)
            naffected = len(items)
            self.items = items

            self.set_file_list(self.items)
            status = "%s files scanned, %s files affected" % (nscanned, naffected)
            self.label_status.Text = status

    def do_apply(self, o, args):
        self.program.perform_renames(self.items)

    def onHelp(self, o, args):
        System.Diagnostics.Process.Start(self.app_help_url)


if __name__ == '__main__' or True:
    GLib.ExceptionManager.UnhandledException += handlers.error_handler_terminal

    Gtk.Application.Init()
    app = Application()
    Gtk.Application.Run()
