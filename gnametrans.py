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
    path = "%s;%s" % (os.path.join(pypath, 'bin', 'gtk', 'bin'), path)
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
import src.callbacks

from gsrc import gtkhelper
from gsrc import gladehelper
from gsrc import handlers
from gsrc.widgets.about_dialog import AboutDialog
from gsrc.widgets.fileview_list import FileviewList
from gsrc.widgets.log_window import LogWindow
from gsrc.widgets.parameters_panel import ParametersPanel


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

        self.color_diff_left = "#b5b5ff"
        self.color_diff_right = "#b5ffb5"
        self.color_error_bg = "#fd7f7f"

        self.parameters_panel = ParametersPanel().pyinit(self)
        self.fileview = FileviewList().pyinit(self)
        self.log = \
            LogWindow(self, functools.partial(self.init_widget, 'logwindow'))
        self.about = \
            AboutDialog(self, functools.partial(self.init_widget, 'aboutdialog'))

        self.thread_compute = None
        self.thread_apply = None

        self.init_gui()
        self.init_signals()
        self.run_gui()

    def init_widget(self, name, obj):
        gxml = Glade.XML(os.path.join(self.app_resource_path, self.glade_file),
                         name, None)
        gladehelper.connect(gxml, obj)

    def init_model(self):
        self.items = []

    def init_gui(self):
        self.options, _, optparser = nametransformer.get_opt_parse(sys.argv)

        # init glade
        self.init_widget('mainwindow', self)
        self.parameters_panel.init_widget(self, optparser, self.options)
        self.fileview.init_widget(self.mainwindow)
        self.log.init_widget()

        # init model
        self.init_model()

        ### Init mainwindow

        self.mainwindow.Title = self.app_title
        self.mainwindow.SetIconFromFile(self.app_icon_path)
        self.mainwindow.SetDefaultSize(600, 500)

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
        self.mainwindow.Shown += self.onParametersChange # XXX possible lockup?
        self.mainwindow.DeleteEvent += self.onWindowDelete
        self.button_quit.Clicked += self.onWindowDelete
        self.imagemenuitem_quit.Activated += self.onWindowDelete
        self.imagemenuitem_help.Activated += self.onHelp
        self.imagemenuitem_about.Activated += self.about.onRun

        self.button_log.Clicked += self.log.onToggle
        self.button_compute.Clicked += self.onParametersChange
        self.button_apply.Clicked += self.do_apply

        self.parameters_panel.ParameterChanged += self.onParametersChange

    def run_gui(self):
        self.mainwindow.ShowAll()


    def onHelp(self, o, args):
        System.Diagnostics.Process.Start(self.app_help_url)

    def onWindowDelete(self, o, args):
        # hide windows to give the impression of a quicker halt
        self.log.onClose(None, None)
        self.mainwindow.Hide()
        for thread in [self.thread_compute, self.thread_apply]:
            if thread and thread.IsAlive:
                thread.Abort()
        Gtk.Application.Quit()


    def onParametersChange(self, *args):
        self.do_compute()


    def do_compute(self):
        def _compute():
            path = self.options.path
            program = nametrans.Program(self.options)
            if os.path.exists(path) and program.validate_options():
                os.chdir(path)

                def f(*args):
                    self.fileview.set_file_list([])
                gtkhelper.app_invoke(f)

                items = program.nameTransformer.scan_fs()
                nscanned = len(items)
                items = program.nameTransformer.process_items(items)
                naffected = len(items)
                nclashes = sum(map(lambda it: 1 if it.invalid else 0, items))
                self.items = items

                def g(*args):
                    status = ("%s file(s) scanned, %s file(s) affected" %
                              (nscanned, naffected))
                    if nclashes:
                        status += ", %s clash(es)" % nclashes

                    self.fileview.set_file_list(self.items)
                    gtkhelper.set_value(self.label_result, status)
                gtkhelper.app_invoke(g)

        task = self.get_task(_compute, [self.button_compute, self.button_apply])
        self.thread_compute = gtkhelper.get_thread(task)
        self.thread_compute.Start()

    def do_apply(self, o, args):
        def _apply():
            program = nametrans.Program(self.options)
            program.perform_renames(self.items)
        task = self.get_task(_apply, [self.button_compute, self.button_apply])
        self.thread_apply = gtkhelper.get_thread(task)
        self.thread_apply.Start()


    def get_task(self, action, widgets_to_lock):
        '''ref for multithreading:
        http://www.mono-project.com/Responsive_Applications'''
        def task():
            def prologue(*args):
                gtkhelper.set_value(self.label_result, '')
                for w in widgets_to_lock:
                    gtkhelper.disable(w)
            gtkhelper.app_invoke(prologue)

            action()

            def epilogue(*args):
                for w in widgets_to_lock:
                    gtkhelper.enable(w)
                gtkhelper.set_value(self.label_progress, '')
            gtkhelper.app_invoke(epilogue)
        return task


if __name__ == '__main__' or True:
    GLib.ExceptionManager.UnhandledException += handlers.error_handler_terminal

    GLib.Thread.Init()
    Gdk.Threads.Init()
    Gtk.Application.Init()

    app = Application()

    Gdk.Threads.Enter()
    Gtk.Application.Run()
    Gdk.Threads.Leave()
