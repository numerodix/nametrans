# Author: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

import clr

clr.AddReference('gtk-sharp'); import Gtk
clr.AddReference('gdk-sharp'); import Gdk

import re


class GtkHelper(object):
    def change_widget_color(self, widget, colorstr):
        cls = type(widget)
        if cls == Gtk.Entry:
            colorobj = self.get_gdk_color_obj(colorstr)
            widget.ModifyText(Gtk.StateType.Normal, colorobj)

    def reset_widget_color(self, widget):
        widget.ModifyText(Gtk.StateType.Normal)

    def get_gdk_color_obj(self, colorstr):
        colorobj = Gdk.Color()
        _, colorobj = Gdk.Color.Parse(colorstr, colorobj)
        return colorobj


class FieldMap(object):
    "Map options in optparser to widgets, using opt.help as widget tooltip"
    def __init__(self, optparser, widget_namespace):
        self.index_name_to_option = {}
        self.index_name_to_widget = {}

        for opt in optparser.option_list:
            if opt.dest:
                name = re.sub('^flag_', '', opt.dest)
                self.index_name_to_option[name] = opt

        widgetnames = dir(widget_namespace)
        widgetnames = filter(lambda wn: not wn.startswith('_'), widgetnames)
        widgetnames = filter(lambda wn: not hasattr(getattr(widget_namespace, wn),
                                                   '__call__'), widgetnames)

        for name in self.index_name_to_option:
            for wname in widgetnames:
                if wname.endswith(name):
                    self.index_name_to_widget[name] = getattr(widget_namespace,
                                                              wname)

        assert(len(self.index_name_to_option) == len(self.index_name_to_widget))

        for name in self.index_name_to_option:
            opt = self.index_name_to_option[name]
            widget = self.index_name_to_widget[name]
            if opt.help:
                widget.TooltipText = opt.help

