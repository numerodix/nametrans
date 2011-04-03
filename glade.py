import re
import os
import sys


import clr
clr.AddReference('gtk-sharp')
import Gtk
clr.AddReference('glade-sharp')
import Glade


import nametrans


def pygladeAutoconnect(gxml, target):
#    def _connect(handler_name, event_obj, signal_name, *args):
#        name = ''.join([frag.title() for frag in signal_name.split('_')])
#        event = getattr(event_obj, name)
#        event += getattr(target, handler_name)

    # add all widgets
    for widget in gxml.GetWidgetPrefix(''):
        setattr(target, gxml.GetWidgetName(widget), widget)

    # connect all signals
#    gxml.SignalAutoconnectFull(_connect)

class Application:
    def __init__(self):
        mypath = os.path.dirname(__file__)
        gxml = Glade.XML(os.path.join(mypath, "gui.glade"), "mainwindow", None)
        pygladeAutoconnect(gxml, self)

        self.mainwindow.SetDefaultSize(400, 260)

        # events that trigger application exit
        self.mainwindow.DeleteEvent += self.onWindowDelete
        self.button_quit.Clicked += self.onWindowDelete

        # events that trigger re-scanning files
        self.mainwindow.Realized += self.do_compute # XXX
        self.selector_path.CurrentFolderChanged += self.do_compute

        self.button_compute.Clicked += self.do_compute

        self.button_apply.Clicked += self.do_apply

        self.fileview.HeadersVisible = True
        self.fileview.AppendColumn("From", Gtk.CellRendererText(), "text", 0)
        self.fileview.AppendColumn("To", Gtk.CellRendererText(), "text", 1)

        self.options, _, _ = nametrans.get_options_object()
        self.nametransformer = None
        self.items = []

        self.mainwindow.ShowAll()

    def onWindowDelete(self, o, args):
        Gtk.Application.Quit()

    def do_compute(self, o, args):
        self.options.flag_recursive = True
        self.options.flag_neater = True

        self.options.in_path = self.selector_path.CurrentFolder
        self.nametransformer = nametrans.NameTransformer(self.options,
                                                         in_path=self.options.in_path)


        items = self.nametransformer.scan_fs()
        items = self.nametransformer.process_items(items)
        self.items = items

        self.set_file_list(self.items)

    def do_apply(self, o, args):
        def errorfunc(fp):
            print("%s %s" % "Target exists:", fp)
        self.nametransformer.perform_renames_in_dir(self.options.in_path,
                                                    self.items, errorfunc)

    def set_file_list(self, items):
        store = Gtk.TreeStore(str, str)
        for item in items:
            store.AppendValues(item.f, item.g)
        self.fileview.Model = store


if __name__ == '__main__' or True:
    print("Python running: %s" % __file__)

    Gtk.Application.Init()
    app = Application()
    Gtk.Application.Run()
