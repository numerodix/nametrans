import sys
sys.path.append('pylib')

import re
import os

import clr
clr.AddReference('gtk-sharp')
import System
import Gtk

def OnDelete(sender, args):
    Gtk.Application.Quit()
    args.RetVal = True

click_count = 0

def OnButtonClick(sender, args):
    global click_count
    click_count += 1
    System.Console.WriteLine("Button Click {0}", click_count)

def RealEntryPoint(title):
    ## Create the window
    Gtk.Application.Init();
    window = Gtk.Window(title)
    window.Resize(200, 200)

    ##  Add a vertical box and a button
    box = Gtk.VBox();
    ok_btn = Gtk.Button("Ok")

    ok_btn.Clicked += OnButtonClick
    box.PackStart(ok_btn, False, False, 0)
    window.Add(box)

    ## Set up the window delete event and display it
    window.DeleteEvent += OnDelete
    window.ShowAll()

    ## And we're off!...
    Gtk.Application.Run();

if __name__ == '__main__' or True:
    print("Python running: %s" % __file__)

    argv = str(sys.argv)
    argv = re.sub('^', 'argv: ', argv)

    RealEntryPoint(argv)
