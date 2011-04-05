# Author: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

import os
import re
import string
import sys
from optparse import OptionParser

from src.digitstring import DigitString
from src.fs import Fs
from src.filepathtrans import FilepathTransformer


class FilePath(object):
    def __init__(self, fp):
        self.f, self.g = fp, fp
        self.invalid = False

class NameTransformer(object):
    def __init__(self, options):
        options.in_path = '.'

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

        items = file_items
        if self.options.flag_dirsonly or not items:
            items = dir_items

        return map(FilePath, items)

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

            t = FilepathTransformer.by_regex(s_from, s_to, t)
            if self.options.flag_neat or self.options.flag_neater:
                ext = FilepathTransformer.make_lowercase(ext)
                t = FilepathTransformer.make_neat(t)
                if self.options.flag_neater:
                    t = FilepathTransformer.make_neater(t)
            if self.options.flag_capitalize:
                t = FilepathTransformer.capitalize(t)
            if self.options.flag_lowercase:
                t = FilepathTransformer.make_lowercase(t)
            if self.options.flag_underscores:
                t = FilepathTransformer.make_spaces_underscores(t)

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
            if Fs.io_invalid_rename(item.f, item.g):
                item.invalid = True
        return items

    def process_items(self, items):
        items = self.compute_transforms(items)

        # no change in name
        if not self.options.renseq:
            items = filter(lambda item: item.f != item.g, items)
        # rename to empty
        items = filter(lambda item: item.g != '', items)

        items = self.compute_clashes(items)

        items.sort(key=lambda item: (item.g.lower(), item.f.lower()))

        return items



def get_opt_parse(argv):
    usage = 'Usage:  %s [options] "<from>" "<to>"\n' % argv[0]

    usage += '\n$ %s "apple" "orange"' % argv[0]
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
    (options, args) = parser.parse_args(argv[1:])

    options.s_from, options.s_to = '', ''
    try:
        argsdupe = args[:]
        options.s_from = argsdupe.pop(0)
        options.s_to = argsdupe.pop(0)
    except IndexError: pass

    return options, args, parser
