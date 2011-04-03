import sys
sys.path.append('pylib')

import re
import os

import clr
clr.AddReference("System.Windows.Forms")
from System.Windows.Forms import *

class Gui(Form):
    def __init__(self):
        argv = str(sys.argv)
        argv = re.sub('^', 'argv: ', argv)
        self.Text = argv
        self.Controls.Add(Label(Text=argv))


if __name__ == '__main__' or True:
    print("Python running: %s" % __file__)
    Application.Run(Gui())
