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
#        self.mainwindow.Realized += self.do_scan
        self.mainwindow.Realized += self.do_compute # XXX
        self.selector_path.CurrentFolderChanged += self.do_compute

        self.button_compute.Clicked += self.do_compute

        self.fileview.HeadersVisible = True
        self.fileview.AppendColumn("From", Gtk.CellRendererText(), "text", 0)
        self.fileview.AppendColumn("To", Gtk.CellRendererText(), "text", 1)

        self.mainwindow.ShowAll()

        self.nametransformer = None

    def onWindowDelete(self, o, args):
        Gtk.Application.Quit()

    def do_compute(self, o, args):
        class Options(object):
            def __init__(self):
                self.s_from = ''
                self.s_to = ''
                self.flag_root = None
                self.flag_filesonly = None
                self.flag_dirsonly = None
                self.flag_recursive = None
                self.flag_capitalize = None
                self.flag_lowercase = None
                self.flag_neat = None
                self.flag_neater = None
                self.flag_underscores = None
                self.flag_dirname = None
                self.renseq = None
                self.flag_flatten = None

        options = Options()
        options.flag_recursive = True
        options.flag_neater = True

        path = self.selector_path.CurrentFolder
        self.nametransformer = nametrans.NameTransformer(options, in_path=path)


        items = self.nametransformer.scan_fs()

        items = self.nametransformer.compute_transforms(items)
        # no change in name
        if not options.renseq:
            items = filter(lambda item: item.f != item.g, items)
        # rename to empty
        items = filter(lambda item: item.g != '', items)

        lst_from, lst_to = [], []
        for item in items:
            lst_from.append(item.f)
            lst_to.append(item.g)
        self.set_file_list(lst_from, lst_to)

    def do_scan(self, o, args):

        files_from = sorted(os.listdir(path), key=lambda x: x.lower())
        files_to = ['']*len(files_from)

        self.set_file_list(files_from, files_to)

    def set_file_list(self, lst_from, lst_to):
        store = Gtk.TreeStore(str, str)
        for (x, y) in zip(lst_from, lst_to):
            store.AppendValues(x, y)
        self.fileview.Model = store


if __name__ == '__main__' or True:
    print("Python running: %s" % __file__)

    Gtk.Application.Init()
    app = Application()
    Gtk.Application.Run()
