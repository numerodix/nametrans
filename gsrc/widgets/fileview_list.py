# Author: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

import clr

clr.AddReference('gtk-sharp'); import Gtk

from gsrc import markupdiff

class FileviewList(object):
    def __init__(self, parent):
        self.parent = parent

        self.diff_color_left = "#b5b5ff"
        self.diff_color_right = "#b5ffb5"
        self.error_color_bg = "#fd7f7f"

    def init_widget(self, mainwindow):
        # init gui
        self.fileview.Reorderable = False
        self.fileview.AppendColumn("From", Gtk.CellRendererText(),
                                   "markup", 0, "background", 2)
        self.fileview.AppendColumn("To", Gtk.CellRendererText(),
                                   "markup", 1, "background", 3)
        self.fileview.Model = Gtk.ListStore(str, str, str, str)

        # events that signal window resize
        mainwindow.ExposeEvent += self.onWindowResize

    def onWindowResize(self, o, args):
        "Triggered on window resize event to keep columns of equal width"
        window_x = self.fileview.Allocation.Width
        needs_resize = False
        for col in self.fileview.Columns:
            col.MinWidth = (window_x / len(self.fileview.Columns))
            if col.MinWidth != col.Width:
                needs_resize = True
                col.Sizing = Gtk.TreeViewColumnSizing.Autosize
        if needs_resize:
            self.fileview.QueueResize()

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

