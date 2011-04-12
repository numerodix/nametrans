# Author: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

import clr

clr.AddReference('gtk-sharp'); import Gtk
clr.AddReference('gdk-sharp'); import Gdk

import re


def change_widget_color(widget, colorstr):
    cls = type(widget)
    if cls == Gtk.Entry:
        colorobj = get_gdk_color_obj(colorstr)
        widget.ModifyText(Gtk.StateType.Normal, colorobj)

def reset_widget_color(widget):
    widget.ModifyText(Gtk.StateType.Normal)

def get_gdk_color_obj(colorstr):
    colorobj = Gdk.Color()
    _, colorobj = Gdk.Color.Parse(colorstr, colorobj)
    return colorobj
