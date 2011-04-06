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
from src import fs
from src.nametransformer import NameTransformer

from guisrc import markupdiff
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
        self.app_title = "nametrans"
        self.app_path = os.path.dirname(__file__)
        self.app_icon = "icon.png"
        self.glade_file = "forms.glade"
        self.diff_color_left = "#b5b5ff"
        self.diff_color_right = "#b5ffb5"
        self.error_color_fg = "#ff0000"
        self.error_color_bg = "#fd7f7f"

        self.gtkhelper = GtkHelper()

        self.log = LogWindow()

        self.init_model()
        self.init_glade()
        self.init_gui()
        self.init_signals()
        self.run_gui()

    def init_glade(self):
        def init_widget(name, obj):
            gxml = Glade.XML(os.path.join(self.app_path, self.glade_file), name, None)
            pygladeAutoconnect(gxml, obj)
        init_widget('mainwindow', self)
        init_widget('logwindow', self.log)

    def init_model(self):
        self.options, _, _ = nametransformer.get_opt_parse(sys.argv)
        self.program = None
        self.items = []

    def init_signals(self):
        # events that trigger application exit
        self.mainwindow.DeleteEvent += self.onWindowDelete
        self.button_quit.Clicked += self.onWindowDelete

        # events that signal window resize
        self.mainwindow.ExposeEvent += self.onWindowResize

        # events that signal change in input parameters
        self.text_s_from.Changed += self.onParametersChange
        self.text_s_to.Changed += self.onParametersChange
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
        self.button_compute.Clicked += self.do_compute
        self.button_apply.Clicked += self.do_apply

        # logwindow events
        self.log.textview_log.Buffer.Changed += self.log.onTextBufferChanged
        self.log.button_close.Clicked += self.log.onClose

    def onWindowResize(self, o, args):
        window_x = self.fileview.Allocation.Width
        for col in self.fileview.Columns:
            col.MinWidth = (window_x / len(self.fileview.Columns))
            col.Sizing = Gtk.TreeViewColumnSizing.Autosize
        self.fileview.QueueResize()

    def init_gui(self):
        ### Init mainwindow

        self.mainwindow.Title = self.app_title
        self.mainwindow.SetIconFromFile(os.path.join(self.app_path,
                                                     self.app_icon))
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

        ### Init logwindow

        self.log.logwindow.Title = "Error log"
        self.log.logwindow.SetIconFromFile(os.path.join(self.app_path,
                                                        self.app_icon))
        self.log.logwindow.SetDefaultSize(400, 260)

        def error_handler(exc):
            msg = ' '.join(exc.args)
            s = "%s: %s\n" % (exc.__class__.__name__, msg)
            self.log.textview_log.Buffer.Text += s
        fs.error_handler = error_handler

        def glib_handler(args):
            s = "%s\n\n" % args.ExceptionObject
            self.log.textview_log.Buffer.Text += s
        GLib.ExceptionManager.UnhandledException += glib_handler

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
                self.do_compute(o, args)

        if o == self.text_path:
            path = self.get_ui_path()
            if path and path != self.selector_path.CurrentFolder:
                self.selector_path.SetCurrentFolder(path)
                self.do_compute(o, args)

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

        self.do_compute(o, args)

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
        style_f = ['<span background="%s">' % self.diff_color_left,
                   '</span>']
        style_g = ['<span background="%s">' % self.diff_color_right,
                   '</span>']
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


    def do_compute(self, o, args):
        path = self.get_ui_path()
        if path:
            os.chdir(path)
            self.program = nametrans.Program(self.options)

            items = self.program.nameTransformer.scan_fs()
            items = self.program.nameTransformer.process_items(items)
            self.items = items

            self.set_file_list(self.items)

    def do_apply(self, o, args):
        # XXX logwindow popup test
#        v = None + 1
        self.program.perform_renames(self.items)

class LogWindow(object):
    def onTextBufferChanged(self, o, args):
        # scroll to the bottom
        it = self.textview_log.Buffer.EndIter
        mark = self.textview_log.Buffer.CreateMark('default', it, True)
        self.textview_log.ScrollToMark(mark, 0, 0, 0, 0)

        self.logwindow.ShowAll()

    def onToggle(self, o, args):
        if self.logwindow.Visible:
            self.onClose(o, args)
        else:
            self.logwindow.ShowAll()

    def onClose(self, o, args):
        self.logwindow.Hide()


if __name__ == '__main__' or True:
    def f(args):
        print args.ExceptionObject
    GLib.ExceptionManager.UnhandledException += f

    Gtk.Application.Init()
    app = Application()
    Gtk.Application.Run()
