#!/usr/bin/env python
#
# Author: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.
#
# <desc> Rename files with regex search/replace semantics </desc>
#
# Doc: http://www.matusiak.eu/numerodix/blog/index.php/2011/03/25/nametrans-renaming-with-search-replace

import itertools
import os
import re
import string
import sys
from optparse import OptionParser

from lib import ansicolor


RUNTIME_IRONPYTHON = re.search('(?i)ironpython', sys.version) and True or False


class DigitString(object):
    def __init__(self, fp, prefix='', postfix=''):
        self.prefix = prefix
        self.postfix = postfix

        digit_runs = re.finditer("([0-9]+)", fp)
        nondigit_runs = re.finditer("([^0-9]+)", fp)

        digit_spans = [m.span() for m in digit_runs if digit_runs]
        nondigit_spans = [m.span() for m in nondigit_runs if nondigit_runs]

        if nondigit_spans and nondigit_spans[0][0] != 0:
            nondigit_spans = [(0,0)] + nondigit_spans

        self.numbers = map(lambda (x,y): fp[x:y], digit_spans)
        self.chars = map(lambda (x,y): fp[x:y], nondigit_spans)

    def has_digits(self):
        return len(self.numbers) > 0

    def process_field_number(self, field):
        assert(field != 0)
        field = field - 1 if field > 0 else field
        return field

    def get_field_count(self):
        return len(self.numbers)

    def get_field(self, field):
        field = self.process_field_number(field)
        try:
            return self.numbers[field]
        except IndexError:
            return ""

    def set_field(self, field, number):
        field = self.process_field_number(field)
        assert(type(number) == str)
        assert(re.match('^[0-9]+$', number))
        try:
            self.numbers[field] = number
        except IndexError: pass

    def set_field_width(self, field, width):
        val = self.get_field(field)
        if val:
            val = string.zfill(str(int(val)), width)
            self.set_field(field, val)

    def get_string(self):
        s = ''
        for (a,b) in itertools.izip_longest(self.chars, self.numbers, fillvalue=''):
            s += a + b
        return self.prefix, s, self.postfix

class Renamer(object):
    @classmethod
    def by_regex(cls, rx_from, rx_to, s):
        return re.sub(rx_from, rx_to, s)

    @classmethod
    def capitalize(cls, s):
        cap = lambda m: m.group(1).upper() + m.group(2).lower()
        s = re.sub("(?u)(?<![0-9\w'])(\w)([\w']*)", cap, s)
        return s

    @classmethod
    def make_lowercase(cls, s):
        tolower = lambda m: m.group(1).lower()
        s = re.sub('(?u)([\w]*)', tolower, s)
        return s

    @classmethod
    def make_spaces_underscores(cls, s):
        s = re.sub(' ', '_', s)
        return s

    @classmethod
    def do_trim(cls, s):
        # check endpoints
        s = Renamer.by_regex('^([ ]|-)*', '', s)
        s = Renamer.by_regex('([ ]|-)*$', '', s)
        return s

    @classmethod
    def make_neat(cls, s):
        # too many hyphens and underscores
        s = Renamer.by_regex('_{2,}', '-', s)
        s = Renamer.by_regex('-{2,}', '-', s)
        s = Renamer.by_regex('-[ ]+-', '-', s)
        # junk-y chars past the start of the string
        s = Renamer.by_regex('\.', ' ', s)
        s = Renamer.by_regex('_', ' ', s)
        s = Renamer.by_regex('#', ' ', s)
        s = Renamer.by_regex(':', ' ', s)
        # let's have spaces around hyphen
        s = Renamer.by_regex('(?<!\s)-', ' -', s)
        s = Renamer.by_regex('-(?!\s)', '- ', s)
        s = Renamer.by_regex('(?<!\s)[+]', ' +', s)
        s = Renamer.by_regex('[+](?!\s)', '+ ', s)
        # empty brackets
        s = Renamer.by_regex('\[ *?\]', ' ', s)
        s = Renamer.by_regex('\( *?\)', ' ', s)
        # normalize spaces
        s = Renamer.by_regex('[ ]{2,}', ' ', s)
        s = cls.do_trim(s)
        return s

    @classmethod
    def make_neater(cls, s):
        # bracket-y junk
        s = Renamer.by_regex('\[.*?\]', ' ', s)
        s = Renamer.by_regex('\(.*?\)', ' ', s)
        s = cls.do_trim(s)
        return s

class Fs(object):
    @classmethod
    def find(cls, path, rec=False):
        path = os.path.abspath(path)
        fs = []
        if not rec:
            fs = os.listdir(path)
        else:
            for r, dirs, files in os.walk(path):
                for fp in dirs+files:
                    fp = os.path.join(r, fp)
                    fs.append(fp)
        fs = map(lambda fp: os.path.join(path, fp), fs)
        return sorted(fs)

    @classmethod
    def string_strip_basepath(cls, basepath, fps):
        rx = '^' + re.escape(basepath) + '(?:' + re.escape(os.sep) + ')?'
        fps = map(lambda fp: re.sub(rx, '', fp), fps)
        return fps

    @classmethod
    def string_normalize_filepath(cls, fp):
        return os.path.normcase(fp)

    @classmethod
    def io_is_same_file(cls, f, g):
        """Check if files are the same on disk"""
        v = False
        try: # Unix branch
            v = os.path.samefile(f, g)
            # we are on Unix because AttributeError has not fired
            # if running on IronPython do workaround for bug
            if RUNTIME_IRONPYTHON:
                v = f == g
        except AttributeError: # Windows branch
            v = os.path.normcase(f) == os.path.normcase(g)
        return v

    @classmethod
    def io_invalid_rename(cls, f, g):
        """Handle rename on case insensitive fs, test not only for file exists,
        but also that it's the same file"""
        return os.path.exists(g) and not cls.io_is_same_file(f, g)

    @classmethod
    def do_rename(cls, f, g, errorfunc):
        if cls.io_invalid_rename(f, g):
            errorfunc(g)
        else:
            os.renames(f, g)

    @classmethod
    def do_renamedir(cls, f, g, errorfunc):
        if not os.path.exists(g) or cls.io_is_same_file(f, g):
            os.rename(f, g)
        else:
            for fp in os.listdir(f):
                cls.do_rename(os.path.join(f, fp), os.path.join(g, fp),
                              errorfunc)

    @classmethod
    def io_set_actual_path(cls, filepath, errorfunc):
        """Fix a filepath that has the wrong case on the fs by renaming
        its parts directory by directory"""
        parts = filepath.split(os.sep)
        for (i, part) in enumerate(parts):
            prefix = os.sep.join(parts[:i]) if i > 0 else '.'
            fps = os.listdir(prefix)
            for fp in fps:
                if part.lower() == fp.lower() and not part == fp:
                    prefix = '' if prefix == '.' else prefix
                    fp_fs = os.path.join(prefix, fp)
                    fp_target = os.path.join(prefix, part)
                    cls.do_renamedir(fp_fs, fp_target, errorfunc)
                    break

    @classmethod
    def do_renames(cls, lst, errorfunc):
        for (f, g) in lst:
            cls.do_rename(f, g, errorfunc)

        # another pass on the dirs for case fixes
        dirlist = {}
        for (f, g) in lst:
            d = os.path.dirname(g)
            if d and d not in dirlist and os.path.exists(d):
                dirlist[d] = None
                cls.io_set_actual_path(d, errorfunc)

class FilePath(object):
    def __init__(self, basepath, fp):
        self.basepath = basepath
        self.f, self.g = fp, fp
        self.invalid = False
    F = property(fget=lambda self: os.path.join(self.basepath, self.f))
    G = property(fget=lambda self: os.path.join(self.basepath, self.g))

class NameTransformer(object):
    def __init__(self, options, in_path=None):
        options.in_path = in_path and in_path or os.getcwd()

        if options.flag_neat or options.flag_neater:
            options.flag_root = True
            if not options.flag_lowercase:
                options.flag_capitalize = True
        if options.flag_dirname:
            options.flag_root = True
            options.flag_filesonly = True
        if options.renseq:
            options.flag_root = True
            options.flag_filesonly = True

        self.options = options

    def scan_fs(self):
        fps = Fs.find(self.options.in_path,
                      rec=any([self.options.flag_recursive,
                               self.options.flag_flatten]))

        file_items = filter(os.path.isfile, fps)
        dir_items = filter(os.path.isdir, fps)

        # split off basepath
        file_items = Fs.string_strip_basepath(self.options.in_path, file_items)
        dir_items = Fs.string_strip_basepath(self.options.in_path, dir_items)

        items = file_items
        if self.options.flag_dirsonly or not items:
            items = dir_items

        return map(lambda fp: FilePath(self.options.in_path, fp), items)

    def get_patterns(self):
        s_from = self.options.s_from
        s_to = self.options.s_to
        if s_from:
            if self.options.flag_literal:
                s_from = re.escape(s_from)
            if self.options.flag_ignorecase:
                s_from = '(?i)' + s_from
        return s_from, s_to

    def split_filepath(self, fp):
        path, root, ext = '', fp, ''
        if self.options.flag_filesonly and self.options.flag_root:
            path, name = os.path.split(fp)
            root, ext = os.path.splitext(name)
        elif self.options.flag_filesonly:
            path, root = os.path.split(fp)
        elif self.options.flag_root:
            root, ext = os.path.splitext(fp)
        return path, root, ext

    def index_items_by_dir(self, items):
        dirindex = {}
        for item in items:
            d = os.path.dirname(item.g) or '.'
            if d not in dirindex:
                dirindex[d] = [item]
            else:
                dirindex[d].append(item)
        return dirindex

    def apply_flatten(self, items):
        for item in items:
            item.g = re.sub(re.escape(os.sep), ' - ', item.g)
        return items

    def apply_dirname(self, items):
        dirindex = self.index_items_by_dir(items)

        items = []
        for (d, its) in dirindex.items():
            if d == '.':
                d = os.path.basename(os.path.abspath(d))
            w = len(str(len(its)))
            for (i, item) in enumerate(sorted(its)):
                path, _, ext = self.split_filepath(item.g)
                root = "%s %s" % (os.path.basename(d), string.zfill(i+1, w))
                item.g = os.path.join(path, root)+ext
                items.append(item)

        return items

    def apply_renseq(self, items):
        parts = self.options.renseq.split(':')

        arg_width = "0"
        if len(parts) == 1:
            arg_field = parts[0]
        if len(parts) == 2:
            arg_field = parts[0]
            arg_width = parts[1] or "0"

        if arg_field:
            arg_field = int(arg_field)
        arg_width = int(arg_width)

        dirindex = self.index_items_by_dir(items)
        items = []
        for (d, its) in dirindex.items():
            dstrings = []
            maxfields = 0
            for item in its:
                path, filename, ext = self.split_filepath(item.g)
                digitstring = DigitString(filename, prefix=path, postfix=ext)
                if digitstring.has_digits():
                    dstrings.append((item, digitstring))
                    maxfields = max(maxfields, digitstring.get_field_count())

            fields = range(1, maxfields+1)
            if arg_field:
                fields = [arg_field]

            for field in fields:
                # find width from names
                width = arg_width if arg_width else 0
                if not width:
                    maxlen = 0
                    for (item, digitstring) in dstrings:
                        v = digitstring.get_field(field)
                        if v:
                            maxlen = max(maxlen, len(str(int(v))))
                    width = maxlen

                for (item, digitstring) in dstrings:
                    digitstring.set_field_width(field, width)

            for (item, digitstring) in dstrings:
                path, filename, ext = digitstring.get_string()
                item.g = os.path.join(path, filename)+ext
                items.append(item)

        return items

    def compute_transforms(self, items):
        if self.options.flag_flatten:
            items = self.apply_flatten(items)
        if self.options.flag_dirname:
            items = self.apply_dirname(items)
        if self.options.renseq:
            items = self.apply_renseq(items)

        for item in items:
            path, t, ext = self.split_filepath(item.g)
            s_from, s_to = self.get_patterns()

            t = Renamer.by_regex(s_from, s_to, t)
            if self.options.flag_neat or self.options.flag_neater:
                ext = Renamer.make_lowercase(ext)
                t = Renamer.make_neat(t)
                if self.options.flag_neater:
                    t = Renamer.make_neater(t)
            if self.options.flag_capitalize:
                t = Renamer.capitalize(t)
            if self.options.flag_lowercase:
                t = Renamer.make_lowercase(t)
            if self.options.flag_underscores:
                t = Renamer.make_spaces_underscores(t)

            item.g = os.path.join(path, t + ext)
        return items

    def compute_clashes(self, items):
        index = {}
        for item in items:
            fp = Fs.string_normalize_filepath(item.g)
            if fp not in index:
                index[fp] = item
            else:
                item.invalid = True
                index[fp].invalid = True
            if Fs.io_invalid_rename(item.F, item.G):
                item.invalid = True
        return items

    def display_transforms_and_prompt(self, items):
        items.sort(key=lambda item: item.g.lower())

        clashes = False
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
                clashes = True
                g_fmt = ansicolor.red(item.g)
            if len(item.f) <= slot and len(item.g) <= slot:
                f_fmt = ansicolor.justify_formatted(f_fmt, string.ljust, slot_l)
                print("%s%s %s %s" % (prefix_fmt, f_fmt, arrow_fmt, g_fmt))
            else:
                print("%s%s\n%s %s" % (prefix_fmt, f_fmt, arrow_fmt, g_fmt))

        prompt = "Rename files? [y/N] "
        if clashes:
            prompt = "Clashes exist, rename files? [y/N] "

        sys.stdout.write(prompt)
        inp = raw_input()

        return inp == "y"


    def process_items(self, items):
        items = self.compute_transforms(items)
        # no change in name
        if not self.options.renseq:
            items = filter(lambda item: item.f != item.g, items)
        # rename to empty
        items = filter(lambda item: item.g != '', items)

        if items:
            items = self.compute_clashes(items)

        return items

    def perform_renames_in_dir(self, basepath, items, errorfunc):
        pairs = map(lambda it: (it.f, it.g), items)

        oldcwd = os.getcwd()
        try:
            os.chdir(self.options.in_path)
            Fs.do_renames(pairs, errorfunc)
        finally:
            os.chdir(oldcwd)

    def run(self):
        items = self.scan_fs()
        items = self.process_items(items)
        if items and self.display_transforms_and_prompt(items):

            def errorfunc(fp):
                print("%s %s" % (ansicolor.red("Target exists:"), fp))

            self.perform_renames_in_dir(self.options.in_path, items,
                                        errorfunc)

def get_options_object():
    usage = 'Usage:  %s [options] "<from>" "<to>"\n' % sys.argv[0]

    usage += '\n$ %s "apple" "orange"' % sys.argv[0]
    usage += '\n * I like apple.jpg -> I like orange.jpg'
    usage += '\n * pineapple.jpg    -> pineorange.jpg'

    parser = OptionParser(usage=usage)
    parser.add_option("-r", help="Apply recursively",
                      dest="flag_recursive", action="store_true")
    parser.add_option("--dirs", help="Apply rename to directories, not files",
                      dest="flag_dirsonly", action="store_true")
    parser.add_option("--files", help="Apply rename only to files",
                      dest="flag_filesonly", action="store_true")
    parser.add_option("--lit", help="Treat patterns as literal, not regex",
                      dest="flag_literal", action="store_true")
    parser.add_option("-i", help="Apply pattern ignoring case",
                      dest="flag_ignorecase", action="store_true")
    parser.add_option("--root", help="Apply rename to root only (not extension)",
                      dest="flag_root", action="store_true")
    parser.add_option("--cap", help="Capitalize",
                      dest="flag_capitalize", action="store_true")
    parser.add_option("--lower", help="Make lowercase",
                      dest="flag_lowercase", action="store_true")
    parser.add_option("--neat", help="Make neat",
                      dest="flag_neat", action="store_true")
    parser.add_option("--neater", help="Remove more junk than regular neat",
                      dest="flag_neater", action="store_true")
    parser.add_option("--under", help="Use underscores for spaces",
                      dest="flag_underscores", action="store_true")
    parser.add_option("--dirname", help="Use the current directory name as filename",
                      dest="flag_dirname", action="store_true")
    parser.add_option("--renseq", help="Change width of numbers in names",
                      dest="renseq", action="store", metavar="field:width")
    parser.add_option("--flatten", help="Flatten directory tree to flat directory",
                      dest="flag_flatten", action="store_true")
    (options, args) = parser.parse_args()

    options.s_from, options.s_to = '', ''
    try:
        options.s_from = args.pop(0)
        options.s_to = args.pop(0)
    except IndexError: pass

    return options, args, parser


if __name__ == '__main__':
    options, args, parser = get_options_object()

    # options that don't need from/to patterns
    if not args and not any([
        options.flag_capitalize,
        options.flag_lowercase,
        options.flag_neat,
        options.flag_neater,
        options.flag_underscores,
        options.flag_dirname,
        options.renseq,
        options.flag_flatten,
    ]):
        parser.print_help()
        sys.exit(2)

    NameTransformer(options).run()
