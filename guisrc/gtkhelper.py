# Author: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

import clr

clr.AddReference('gtk-sharp'); import Gtk
clr.AddReference('gdk-sharp'); import Gdk


class GtkHelper(object):
    def change_widget_color(self, widget, colorstr):
        cls = type(widget)
        if cls == Gtk.Entry:
            colorobj = self.get_gdk_color_obj(colorstr)
            widget.ModifyText(Gtk.StateType.Normal, colorobj)

    def reset_widget_color(self, widget):
        widget.ModifyText(Gtk.StateType.Normal)

    def get_gdk_color_obj(self, colorstr):
        colorobj = Gdk.Color(0, 0, 0)
        _, colorobj = Gdk.Color.Parse(colorstr, colorobj)
        return colorobj
