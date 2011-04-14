# Copyright: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

import clr
import System

clr.AddReference('gdk-sharp'); import Gdk

from src import versioninfo

class AboutDialog(object):
    def __init__(self, parent, init_glade_func):
        self.parent = parent
        self.init_glade_func = init_glade_func

    def onRun(self, obj, args):
        self.init_glade_func(self)

        self.aboutdialog.SetIconFromFile(self.parent.app_icon_path)
        self.aboutdialog.Logo = Gdk.Pixbuf(self.parent.app_icon_path)
        self.aboutdialog.Name = self.parent.app_title
        self.aboutdialog.Version = versioninfo.release
        self.aboutdialog.Authors = System.Array[str](versioninfo.authors)
        self.aboutdialog.Comments = versioninfo.desc
        self.aboutdialog.License = open(self.parent.app_license_file).read()
        self.aboutdialog.Website = versioninfo.website

        self.aboutdialog.Run()
        self.aboutdialog.Destroy()

