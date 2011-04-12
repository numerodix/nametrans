
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
