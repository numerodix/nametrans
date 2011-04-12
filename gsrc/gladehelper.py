# Author: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

def connect(gxml, target):
    # add all widgets
    for widget in gxml.GetWidgetPrefix(''):
        name = gxml.GetWidgetName(widget)
        # if widget.fileview exists, this class manages the widget,
        # thus bind to widget.fileview.fileview
        if not hasattr(target, name):
            setattr(target, name, widget)
        else:
            subtarget = getattr(target, name)
            setattr(subtarget, name, widget)

def reconnect(obj_from, obj_to, names):
    for name in names:
        o = getattr(name, obj_from)
        setattr(obj_to, name, o)
