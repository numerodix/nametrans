# Author: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

import clr

clr.AddReference('gtk-sharp'); import Gtk

import re

from gsrc import gtkhelper
from gsrc import platform

class LogWindow(object):
    def __init__(self, parent, init_glade_func):
        self.parent = parent
        self.init_glade_func = init_glade_func

        self.gtkhelper = gtkhelper.GtkHelper()
        self.tags = []

        self.initialized_platform_info = False

    def init_widget(self):
        self.init_glade_func(self)

        tag = Gtk.TextTag('em')
        tag.ForegroundGdk = self.gtkhelper.get_gdk_color_obj('red')
        tagtable = self.textview_log.Buffer.TagTable
        tagtable.Add(tag)
        self.tags.append('em')

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
        cols = [
            ["Assembly", "text", 0],
            ["Version", "text", 1],
            ["Location", "text", 2],
        ]
        for (name, att, attid) in cols:
            self.assemblyview.AppendColumn(name, Gtk.CellRendererText(), att, attid)

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


    def apply_markup(self):
        gi =  self.textview_log.Buffer.GetIterAtOffset
        for tag in self.tags:
            topen = '<%s>' % tag
            tclose = '</%s>' % tag
            rx = '(?is)(%s.*?%s)' % (topen, tclose)
            for m in re.finditer(rx, self.textview_log.Buffer.Text):

                it_open_start = gi(m.start())
                it_open_end = gi(m.start() + len(topen))

                it_close_start = gi(m.end() - len(tclose))
                it_close_end = gi(m.end())

                self.textview_log.Buffer.ApplyTag(tag, it_open_start, it_close_end)

                for (frm, to) in [[m.end() - len(tclose), m.end()],
                                  [m.start(), m.start() + len(topen)]]:
                    rit_frm = clr.Reference[Gtk.TextIter](gi(frm))
                    rit_to = clr.Reference[Gtk.TextIter](gi(to))
                    self.textview_log.Buffer.Delete(rit_frm, rit_to)

    def onTextBufferChanged(self, o, args):
        # scroll to the bottom
        it = self.textview_log.Buffer.EndIter
        mark = self.textview_log.Buffer.CreateMark(None, it, True)
        self.textview_log.ScrollToMark(mark, 0, 0, 0, 0)

        self.apply_markup()

        self.logwindow.ShowAll()
        self.logwindow.Present()

    def onToggle(self, o, args):
        if self.logwindow.Visible:
            self.onClose(o, args)
        else:
            self.logwindow.ShowAll()

    def onClose(self, o, args):
        self.logwindow.Hide()

