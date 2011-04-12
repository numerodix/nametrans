# Author: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

import clr

clr.AddReference('gtk-sharp'); import Gtk

import optparse
import re

from src.nametransformer import NameTransformer

from gsrc import gladehelper


class Parameter(object):
    def __init__(self, name, rawname, wname, is_flag):
        self.name = name
        self.rawname = rawname
        self.wname = wname
        self.is_flag = is_flag

class ParametersPanel(object):
    def __init__(self):
        self.flag_prefix = 'flag_'
        self.param_prefix = 'param_'

        self.special_names = ['renseq_field', 'renseq_width']

        self.index_by_name = {}
        self.index_by_rawname = {}
        self.index_by_wname = {}

    def init_widget(self, parent, optparser, options):
        self._init_indexes(parent, optparser, options)

        widget_names = map(lambda p: p.wname, self.index_by_name.values())
        gladehelper.reconnect(parent, self, widget_names)

        self.set_tooltips(optparser, self.index_by_rawname)

        self.fill_gui_from_optobj(options)

        self.init_signals()

    def _init_indexes(self, parent, optparser, options):
        # raw param names from options object
        param_names_raw = self._get_param_names_raw(options) + self.special_names

        # clean param names
        f = lambda n: re.sub('^' + re.escape(self.flag_prefix), '', n)
        param_names = map(f, param_names_raw)

        # widget names
        wnames = self._get_widget_names(parent, param_names)

        for (name, rawname, wname) in zip(param_names, param_names_raw, wnames):
            widgetobj = getattr(parent, wname)
            is_flag = type(widgetobj) == Gtk.CheckButton
            param_obj = Parameter(name, rawname, wname, is_flag)
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
                wname = pobj.wname
                widgetobj = getattr(self, wname)
                widgetobj.TooltipText = opt.help

    def fill_gui_from_optobj(self, options):
        for (name, pobj) in self.index_by_name.items():
            if name not in self.special_names:
                widgetobj = getattr(self, pobj.wname)
                if pobj.is_flag:
                    widgetobj.Active = getattr(options, pobj.rawname, False)
                else:
                    widgetobj.Text = getattr(options, pobj.rawname) or ''

        # renseq
        field, width = NameTransformer.parse_renseq_args(options.renseq)
        if type(field) == int or type(width) == int:
            self.checkbutton_param_renseq.Active = True
            if field: self.spinbutton_param_renseq_field.Value = field
            if width: self.spinbutton_param_renseq_width.Value = width
        self.onRenseqToggle(self.checkbutton_param_renseq, None)

    def onRenseqToggle(self, o, args):
        if self.checkbutton_param_renseq.Active:
            self.spinbutton_param_renseq_field.Sensitive = True
            self.spinbutton_param_renseq_width.Sensitive = True
        else:
            self.spinbutton_param_renseq_field.Sensitive = False
            self.spinbutton_param_renseq_width.Sensitive = False
#        self.onParametersChange(o, args)

    def init_signals(self):
        self.checkbutton_param_renseq.Toggled += self.onRenseqToggle
