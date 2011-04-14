# Copyright: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

import clr

clr.AddReference('gtk-sharp'); import Gtk

from gsrc import gtkhelper
from gsrc import markupdiff


class FileviewList(Gtk.Widget):
    def pyinit(self, parent):
        self.parent = parent

        return self

    def init_widget(self, mainwindow):
        self.mainwindow = mainwindow

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
        for col in self.fileview.Columns:
            col.MinWidth = (window_x / len(self.fileview.Columns))

    def clear_file_list(self):
        self.fileview.Model.Clear()

        # try to reset column width
        self.turn_on_autosize()
        self.fileview.Model.AppendValues('', '', 'white', 'white')
        self.fileview.Model.Clear()

        gtkhelper.process_events()

    def turn_off_autosize(self):
        for col in self.fileview.Columns:
            col.Sizing = Gtk.TreeViewColumnSizing.GrowOnly

    def turn_on_autosize(self):
        for col in self.fileview.Columns:
            col.Sizing = Gtk.TreeViewColumnSizing.Autosize

    def set_file_list(self, items, nscanned, progress_widget, result_widget):
        if len(items) > 1000:
            self.turn_off_autosize()
        else:
            self.turn_on_autosize()

        color_left = self.parent.color_diff_left
        color_right = self.parent.color_diff_right
        color_error_bg = self.parent.color_error_bg

        nclashes = 0
        nrows = len(items)

        style_f = ['<span bgcolor="%s">' % color_left, '</span>']
        style_g = ['<span bgcolor="%s">' % color_right, '</span>']
        for (i, item) in enumerate(items):
            col_f, col_g = "white", "white"
            if item.invalid:
                col_g = color_error_bg
                nclashes += 1
            f, g = markupdiff.diff_markup(item.f, item.g, style_f, style_g)
            wrap = '<span font="8.5"><tt>%s</tt></span>'
            f = wrap % f
            g = wrap % g
            self.fileview.Model.AppendValues(f, g, col_f, col_g)
            if i % 100 == 0:
                progress = "Displaying %s files of %s..." % (i, nrows)
                gtkhelper.set_value(progress_widget, progress)
                gtkhelper.process_events()

        result = "%s file(s) scanned, %s file(s) affected" % (nscanned, nrows)
        if nclashes:
            result += ", %s clash(es)" % nclashes
        gtkhelper.set_value(result_widget, result)
