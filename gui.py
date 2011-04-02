import sys
sys.path.append('pylib')

import re
import os

import clr
clr.AddReference("System.Windows.Forms")
from System.Windows.Forms import *

class Gui(Form):
    def __init__(self):
        args = str(sys.argv)
        args = re.sub('^', 'argv: ', args)
        self.Controls.Add(Label(Text=args))


if __name__ == '__main__':
    Application.Run(Gui())
