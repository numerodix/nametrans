# Author: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

import clr

clr.AddReference('gtk-sharp'); import Gtk

from gsrc import platform

class LogWindow(object):
    def __init__(self, parent):
        self.parent = parent
        self.initialized_platform_info = False

    def init_platform_info(self, o, args):
        if not self.initialized_platform_info:
            self.init_platform_labels()
            self.init_assemblies_list()
            self.initialized_platform_info = True

    def init_platform_labels(self):
        platform_s = platform.get_platform_string()
        if platform_s:
            self.label_platform.Text = platform_s
        runtime_s = platform.get_runtime_string()
        if runtime_s:
            self.label_runtime.Text = runtime_s

    def init_assemblies_list(self):
        self.assemblyview.Reorderable = False

        self.set_assemly_list()

    def set_assemly_list(self):
        self.assemblyview.AppendColumn("Assembly", Gtk.CellRendererText(),
                                       "text", 0)
        self.assemblyview.AppendColumn("Version", Gtk.CellRendererText(),
                                       "text", 1)
        self.assemblyview.AppendColumn("Location", Gtk.CellRendererText(),
                                       "text", 2)

        self.assemblyview.Model = Gtk.ListStore(str, str, str)
        assemblies = platform.get_assemblies()
        for ass in assemblies:
            assname = ass.GetName()
            name = str(assname.Name)
            ver = str(assname.Version)
            loc = ''
            if hasattr(ass, 'Location'):
                loc = str(ass.Location)
            self.assemblyview.Model.AppendValues(name, ver, loc)


    def onTextBufferChanged(self, o, args):
        # scroll to the bottom
        it = self.textview_log.Buffer.EndIter
        mark = self.textview_log.Buffer.CreateMark('default', it, True)
        self.textview_log.ScrollToMark(mark, 0, 0, 0, 0)

        self.logwindow.ShowAll()
        self.logwindow.Present()

    def onToggle(self, o, args):
        if self.logwindow.Visible:
            self.onClose(o, args)
        else:
            self.logwindow.ShowAll()

    def onClose(self, o, args):
        self.logwindow.Hide()

