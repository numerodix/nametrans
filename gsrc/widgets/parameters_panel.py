# Copyright: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

import clr
import System

clr.AddReference('gtk-sharp'); import Gtk
clr.AddReference('IronPython'); import IronPython

import optparse
import os
import re

from ipylib import pyevent

from src.nametransformer import NameTransformer

from gsrc import gladehelper
from gsrc import gtkhelper


class Parameter(object):
    def __init__(self, name, rawname, wname, widget):
        self.name = name
        self.rawname = rawname
        self.wname = wname
        self.widget = widget

class ParametersPanel(Gtk.Widget):
    def pyinit(self, parent):
        self.parent = parent

        self.flag_prefix = 'flag_'
        self.param_prefix = 'param_'

        self.boundonly_names = ['selector_path']

        self.index_by_name = {}
        self.index_by_rawname = {}
        self.index_by_wname = {}

        self.ParameterChanged, self.emitParameterChanged = pyevent.make_event()

        return self

    def init_widget(self, parent, optparser, options):
        # XXX review
        self.parent = parent
        self._options = options

        self._init_indexes(parent, optparser, options)

        widget_names = map(lambda p: p.wname, self.index_by_name.values())
        gladehelper.reconnect(parent, self, widget_names + self.boundonly_names)

        self.set_tooltips(optparser, self.index_by_rawname)

        self.fill_gui_from_optobj(options)

        self.init_signals()

        self.initPath(options)

    def _init_indexes(self, parent, optparser, options):
        # raw param names from options object
        param_names_raw = self._get_param_names_raw(options)

        # clean param names
        f = lambda n: re.sub('^' + re.escape(self.flag_prefix), '', n)
        param_names = map(f, param_names_raw)

        # widget names
        wnames = self._get_widget_names(parent, param_names)

        for (name, rawname, wname) in zip(param_names, param_names_raw, wnames):
            widget = getattr(parent, wname)
            param_obj = Parameter(name, rawname, wname, widget)
            self.index_by_name[name] = param_obj
            self.index_by_rawname[rawname] = param_obj
            self.index_by_wname[wname] = param_obj

    def _get_empty_options_names(self):
        parser = optparse.OptionParser()
        (options, args) = parser.parse_args([])
        names = {}
        for name in dir(options):
            names[name] = None
        return names

    def _get_param_names_raw(self, options):
        invariables = self._get_empty_options_names()
        names = []
        for name in dir(options):
            if not name in invariables:
                names.append(name)
        return names

    def _get_widget_names(self, namespace, param_names):
        wnames = dir(namespace)
        wnames = filter(lambda n: not n.startswith('_'), wnames)

        names = []
        for param_name in param_names:
            for wname in wnames:
                if wname.endswith(self.param_prefix + param_name):
                    names.append(wname)
        return names

    def set_tooltips(self, optparser, index_by_rawname):
        for opt in optparser.option_list:
            if opt.dest and opt.help:
                pobj = index_by_rawname[opt.dest]
                pobj.widget.TooltipText = opt.help

    def init_signals(self):
        self.checkbutton_param_renseq.Toggled += self.onRenseqToggle

        # events that signal change in parameters
        for (name, pobj) in self.index_by_name.items():
            gtkhelper.set_changed_handler(pobj.widget, self.onParameterChanged)

        # events that trigger updating the path
        self.selector_path.CurrentFolderChanged += self.onPathChange
        self.text_param_path.Activated += self.onPathChange
        self.text_param_path.FocusOutEvent += self.onPathChange


    def fill_gui_from_optobj(self, options):
        for (name, pobj) in self.index_by_name.items():
            optval = getattr(options, pobj.rawname)
            gtkhelper.set_value(pobj.widget, optval)
        self.onRenseqToggle(self.checkbutton_param_renseq, None)

    def read_gui_into_optobj(self, options):
        for (name, pobj) in self.index_by_name.items():
            guival = gtkhelper.get_value(pobj.widget)
            setattr(options, pobj.rawname, guival)
        return options


    def onRenseqToggle(self, o, args):
        if self.checkbutton_param_renseq.Active:
            gtkhelper.enable(self.spinbutton_param_renseq_field)
            gtkhelper.enable(self.spinbutton_param_renseq_width)
        else:
            gtkhelper.disable(self.spinbutton_param_renseq_field)
            gtkhelper.disable(self.spinbutton_param_renseq_width)
        self.onParameterChanged(None, None)

    def get_ui_path(self):
        path = self.text_param_path.Text
        if not path or not os.path.exists(path):
            gtkhelper.change_color(self.text_param_path, self.parent.color_error_bg)
        else:
            gtkhelper.reset_color(self.text_param_path)
            return path

    def initPath(self, options):
        gtkhelper.set_value(self.text_param_path, options.path)
        path = self.get_ui_path()
        if path:
            self.selector_path.SetCurrentFolder(path)

    def onPathChange(self, o, args):
        if o == self.selector_path:
            path = self.selector_path.CurrentFolder
            if path and path != self.text_param_path.Text:
                self.text_param_path.Text = path
                self.onParameterChanged(None, None)

        if o == self.text_param_path:
            path = self.get_ui_path()
            if path and path != self.selector_path.CurrentFolder:
                self.selector_path.SetCurrentFolder(path)
                self.onParameterChanged(None, None)

    def onParameterChanged(self, o, args):
        options = self.read_gui_into_optobj(self._options)
        # prevent duplicate events triggered by path input
        if getattr(self, '_path', None) != options.path:
            self.parent.options = options
            self.emitParameterChanged()
        self._path = options.path
