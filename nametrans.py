#!/usr/bin/env python
#
# Author: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.
#
# <desc> Rename files with regex search/replace semantics </desc>
#
# Doc: http://www.matusiak.eu/numerodix/blog/index.php/2011/03/25/nametrans-renaming-with-search-replace
# Doc: http://www.matusiak.eu/numerodix/blog/index.php/2011/04/09/ironpython-gtk/

import os
import re
import sre_constants
import string
import sys

from lib import ansicolor

from src.fs import Fs
from src import callbacks
from src import io
from src import nametransformer
from src.nametransformer import NameTransformer


class Program(object):
    def __init__(self, options):
        self.options = options
        self.nameTransformer = NameTransformer(options)

    def validate_options(self):
        try:
            re.compile(self.options.s_from)
            re.compile(self.options.s_to)
            return True
        except (sre_constants.error, re.error), e:
            re_exc = callbacks.RegularExpressionError(*e.args)
            callbacks.error_handler(re_exc)

    def display_transforms_and_prompt(self, items):
        clashes = 0
        arrow = "->"; prefix = " * "
        linewidth = 78; spacing = 2

        def get_slot(linewidth, arrow, prefix, spacing):
            return (linewidth - len(arrow) - prefix - spacing) / 2
        slotlong = get_slot(linewidth, arrow, len(prefix), spacing)
        longest_l = max(map(lambda item: len(item.f), items))
        longest = max(longest_l, max(map(lambda item: len(item.g), items)))
        slot = longest; slot_l = longest_l
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
                f_fmt = ansicolor.justify_formatted(f_fmt, string.ljust, slot_l)
                io.writeln("%s%s %s %s" % (prefix_fmt, f_fmt, arrow_fmt, g_fmt))
            else:
                io.writeln("%s%s\n%s %s" % (prefix_fmt, f_fmt, arrow_fmt, g_fmt))

        prompt = "Rename files? [y/N] "
        if clashes:
            prompt = "%s clash(es) exist, rename files? [y/N] " % clashes

        sys.stdout.write(prompt)
        inp = raw_input()

        return inp == "y"

    def perform_renames(self, items):
        callbacks.progress("Performing filenames...")

        pairs = map(lambda it: (it.f, it.g), items)
        Fs.do_renames(pairs)

        io.clear_line()

    def run(self):
        if self.validate_options():
            items = self.nameTransformer.scan_fs()
            items = self.nameTransformer.process_items(items)
            if items and self.display_transforms_and_prompt(items):
                self.perform_renames(items)


if __name__ == '__main__':
    options, args, parser = nametransformer.get_opt_parse(sys.argv)

    # options that don't need from/to patterns
    if not args and not any([
        options.flag_capitalize,
        options.flag_lowercase,
        options.flag_neat,
        options.flag_neater,
        options.flag_underscore,
        options.flag_dirname,
        options.renseq,
        options.flag_flatten,
    ]):
        parser.print_help()
        sys.exit(2)

    if not os.path.exists(options.path):
        io.writeln("Invalid path: %s" % options.path)
        sys.exit(1)
    else:
        os.chdir(options.path)

    Program(options).run()
