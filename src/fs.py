# Author: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

import os
import re


class Fs(object):
    @classmethod
    def find(cls, path, rec=False):
        fs = []
        if not rec:
            fs = os.listdir(path)
        else:
            for r, dirs, files in os.walk(path):
                rx = '^\.(?:' + re.escape(os.sep) + ')?'
                r = re.sub(rx, '', r)
                for fp in dirs+files:
                    fp = os.path.join(r, fp)
                    fs.append(fp)
        return sorted(fs)

    @classmethod
    def string_normalize_filepath(cls, fp):
        return os.path.normcase(fp)

    @classmethod
    def string_is_same_file(cls, f, g):
        """Check if filenames are the same according to fs rules"""
        if hasattr(os.path, 'samefile'):
            return f == g
        else:
            return os.path.normcase(f) == os.path.normcase(g)

    @classmethod
    def io_is_same_file(cls, f, g):
        """Check if files are the same on disk"""
        try:
            return os.path.samefile(f, g)
        except AttributeError:
            return os.path.normcase(f) == os.path.normcase(g)

    @classmethod
    def io_invalid_rename(cls, f, g):
        """Handle rename on case insensitive fs, test not only for file exists,
        but also that it's the same file"""
        return os.path.exists(g) and not cls.io_is_same_file(f, g)

    @classmethod
    def do_rename(cls, f, g):
        if cls.io_invalid_rename(f, g):
            # XXX
#            print("%s %s" % (ansicolor.red("Target exists:"), g))
            print("%s %s" % ("Target exists:", g))
        else:
            os.renames(f, g)

    @classmethod
    def do_renamedir(cls, f, g):
        if not os.path.exists(g) or cls.io_is_same_file(f, g):
            os.rename(f, g)
        else:
            for fp in os.listdir(f):
                cls.do_rename(os.path.join(f, fp), os.path.join(g, fp))

    @classmethod
    def io_set_actual_path(cls, filepath):
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
                    cls.do_renamedir(fp_fs, fp_target)
                    break

    @classmethod
    def do_renames(cls, lst):
        for (f, g) in lst:
            cls.do_rename(f, g)

        # another pass on the dirs for case fixes
        dirlist = {}
        for (f, g) in lst:
            d = os.path.dirname(g)
            if d and d not in dirlist and os.path.exists(d):
                dirlist[d] = None
                cls.io_set_actual_path(d)
