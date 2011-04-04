# Author: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

from exceptions import OSError
import os
import re
import sys


RUNTIME_IRONPYTHON = re.search('(?i)ironpython', sys.version) and True or False

class RenameException(Exception): pass
EXCEPTION_LIST = (RenameException, OSError)

def error_handler(exc):
    msg = ' '.join(exc.args)
    print("%s: %s" % (exc.__class__.__name__, msg))


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
    def do_rename_with_temp_exc(cls, func, f, g):
        """Rename f -> g, but using t as tempfile. If writing to g fails,
        will attempt to rollback f <- t."""
        t = f + '.tmp'
        while os.path.exists(t):
            t += 'z'

        # f -> t
        try:
            func(f, t)
        except OSError:
            raise OSError("Failed to create tempfile for rename: %s" % t)

        # t -> g
        try:
            func(t, g)
        except OSError:
            try:
                func(t, f)
            except OSError:
                raise OSError("Failed to rollback rename: %s <- %s" % (f, t))
            raise OSError("Failed rename %s -> %s" % (f, g))

    @classmethod
    def do_rename_exc(cls, f, g):
        """Attempts to detect an overwrite, throwing RenameException.
        If detection fails, will throw OSError."""
        if cls.io_invalid_rename(f, g):
            raise RenameException("Target exists: %s" % g)
        else:
            cls.do_rename_with_temp_exc(os.renames, f, g)

    @classmethod
    def do_renamedir(cls, f, g):
        if not os.path.exists(g) or cls.io_is_same_file(f, g):
            try:
                cls.do_rename_with_temp_exc(os.rename, f, g)
            except EXCEPTION_LIST, e:
                error_handler(e)
        else:
            for fp in os.listdir(f):
                try:
                    cls.do_rename_exc(os.path.join(f, fp), os.path.join(g, fp))
                except EXCEPTION_LIST, e:
                    error_handler(e)

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
            try:
                cls.do_rename_exc(f, g)
            except EXCEPTION_LIST, e:
                error_handler(e)

        # another pass on the dirs for case fixes
        dirlist = {}
        for (f, g) in lst:
            d = os.path.dirname(g)
            if d and d not in dirlist and os.path.exists(d):
                dirlist[d] = None
                cls.io_set_actual_path(d)
