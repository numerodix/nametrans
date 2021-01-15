#!/usr/bin/env python
#
# Copyright: Martin Matusiak <numerodix@gmail.com>

from __future__ import absolute_import

import os
import re
import sre_constants
import string
import sys

import ansicolor

from nametrans import callbacks
from nametrans import io
from nametrans import nametransformer
from nametrans.fs import Fs
from nametrans.nametransformer import NameTransformer


try:
    input_func = raw_input
except NameError:
    input_func = input


class Program(object):
    def __init__(self, options):
        self.options = options
        self.nameTransformer = NameTransformer(options)

    def validate_options(self):
        try:
            re.compile(self.options.s_from)
            re.compile(self.options.s_to)
            return True
        except (sre_constants.error, re.error) as e:
            re_exc = callbacks.RegularExpressionError(*e.args)
            callbacks.error_handler(re_exc)

    def display_transforms_and_prompt(self, items):
        clashes = 0
        arrow = "->"
        prefix = " * "
        linewidth = 78
        spacing = 2

        def get_slot(linewidth, arrow, prefix, spacing):
            return (linewidth - len(arrow) - prefix - spacing) / 2

        slotlong = get_slot(linewidth, arrow, len(prefix), spacing)
        longest_l = max(map(lambda item: len(item.f), items))
        longest = max(longest_l, max(map(lambda item: len(item.g), items)))
        slot = longest
        slot_l = longest_l
        if longest > slotlong:
            slot = get_slot(linewidth, arrow, len(prefix), spacing)
            slot_l = slot

        for item in items:
            arrow_fmt = ansicolor.yellow(arrow)
            prefix_fmt = ansicolor.green(prefix)
            f_fmt, g_fmt = ansicolor.colordiff(item.f, item.g)
            if item.invalid:
                clashes += 1
                g_fmt = ansicolor.red(item.g)
            if len(item.f) <= slot and len(item.g) <= slot:
                f_fmt = ansicolor.justify_formatted(f_fmt,
                                                    lambda s, w: s.ljust(w), slot_l)
                io.writeln("%s%s %s %s" %
                           (prefix_fmt, f_fmt, arrow_fmt, g_fmt))
            else:
                io.writeln("%s%s\n%s %s" %
                           (prefix_fmt, f_fmt, arrow_fmt, g_fmt))

        s_files = "%s files" % len(items)
        prompt = "Rename %s? [y/N] " % s_files
        if clashes:
            prompt = ("%s clash(es) exist, rename %s? [y/N] " %
                      (clashes, s_files))

        sys.stdout.write(prompt)
        inp = input_func()

        return inp == "y"

    def perform_renames(self, items):
        callbacks.progress("Performing renames...")

        pairs = map(lambda it: (it.f, it.g), items)
        Fs.do_renames(pairs)

        io.clear_line()

    def run(self):
        if self.validate_options():
            items = self.nameTransformer.scan_fs()
            items = self.nameTransformer.process_items(items)
            if items and self.display_transforms_and_prompt(items):
                self.perform_renames(items)


def main():
    options, args, parser = nametransformer.get_opt_parse(sys.argv)

    # options that don't need from/to patterns
    if not args and not any([
        options.flag_capitalize,
        options.flag_lowercase,
        options.flag_neat,
        options.flag_neater,
        options.flag_underscore,
        options.flag_shuffle,
        options.flag_dirname,
        options.renseq,
        options.flag_flatten,
    ]):
        parser.print_help()
        sys.exit(0)

    if not os.path.exists(options.path):
        io.writeln("Invalid path: %s" % options.path)
        sys.exit(1)
    else:
        os.chdir(options.path)

    Program(options).run()


if __name__ == '__main__':
    main()
