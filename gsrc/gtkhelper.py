# Copyright: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

import clr
import System

clr.AddReference('gtk-sharp'); import Gtk
clr.AddReference('gdk-sharp'); import Gdk

import re


def get_thread(func):
    thread = System.Threading.Thread(System.Threading.ThreadStart(func))
    return thread

def exclude_threads(*threads):
    for thread in threads:
        if thread and thread.IsAlive:
            return

def kill_threads(*threads):
    # XXX emits: GLib-CRITICAL **: g_source_remove: assertion `tag > 0' failed
    # XXX locks the gui for seconds on Windows
    "Attempt to kill threads by calling Abort and checking status."
    any_alive = True
    i = 0
    while any_alive:
        i += 1
        any_alive = False
        for thread in threads:
            if thread and thread.IsAlive:
                thread.Abort()
            if thread and thread.IsAlive:
                any_alive = True
#                print i, 

def app_invoke(func):
    Gtk.Application.Invoke(func)

def process_events():
    # XXX infinite loop when running threaded
    'ref: http://www.mono-project.com/Responsive_Applications'
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
