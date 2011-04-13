# Author: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

import clr

clr.AddReference('gtk-sharp'); import Gtk
clr.AddReference('gdk-sharp'); import Gdk

import re


def process_events():
    while Gtk.Application.EventsPending():
        Gtk.Application.RunIteration()

def change_color(widget, colorstr):
    cls = type(widget)
    if cls == Gtk.Entry:
        colorobj = get_gdk_color_obj(colorstr)
        widget.ModifyBase(Gtk.StateType.Normal, colorobj)

def reset_color(widget):
    widget.ModifyBase(Gtk.StateType.Normal)

def get_gdk_color_obj(colorstr):
    colorobj = Gdk.Color()
    _, colorobj = Gdk.Color.Parse(colorstr, colorobj)
    return colorobj

def enable(widget):
    widget.Sensitive = True

def disable(widget):
    widget.Sensitive = False

def get_value(widget):
    cls = type(widget)
    if cls == Gtk.CheckButton:
        return widget.Active or False
    if cls == Gtk.Entry:
        return widget.Text or ''
    if cls == Gtk.SpinButton:
        return int(widget.Value)

def set_value(widget, value):
    cls = type(widget)
    if cls == Gtk.CheckButton:
        widget.Active = value or False
    if cls == Gtk.Entry:
        widget.Text = value or ''
    if cls == Gtk.Label:
        widget.Text = value or ''
    if cls == Gtk.SpinButton:
        widget.Value = value or 0

def set_changed_handler(widget, handler):
    cls = type(widget)
    if cls == Gtk.CheckButton:
        widget.Toggled += handler
    if cls == Gtk.Entry:
        widget.Activated += handler
    if cls == Gtk.SpinButton:
        widget.ValueChanged += handler
