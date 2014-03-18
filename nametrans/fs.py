# Copyright: Martin Matusiak <numerodix@gmail.com>

from __future__ import absolute_import

import os
import re

from nametrans import callbacks
from nametrans.callbacks import RenameException

EXCEPTION_LIST = (RenameException, OSError)


class Fs(object):
    fs_case_sensitive = None

    @classmethod
    def detect_fs_case_sensitivity(cls, path):
        '''Detect the case sensitivity of a filesystem. Given a path, find a
        file in that directory and check os.path.exists in lowercase and
        uppercase. Should be a reliable test for the specific path, but does
        not remedy crossing filesystem boundaries with mounted
        filesysystems.'''
        # find a file to test on
        fp = None
        if os.path.isdir(path):
            fps = os.listdir(path)
            if fps:
                fp = fps[0]

        if not fp:
            fp = os.path.basename(path)

        cls.fs_case_sensitive = not (os.path.exists(fp.lower()) and
                                     os.path.exists(fp.upper()))

    @classmethod
    def find(cls, path, rec=False):
        cls.detect_fs_case_sensitivity(path)

        def remove_basepath(p):
            rx = '^' + re.escape(path) + '(?:' + re.escape(os.sep) + ')?'
            return re.sub(rx, '', p)

        def write_progress(p):
            p = remove_basepath(p)
            callbacks.progress("Scanning:", (p and p or '.'))

        fs = []
        if not rec:
            write_progress(path)
            fs = os.listdir(path)
        else:
            for p, dirs, files in os.walk(path):
                write_progress(p)
                for fp in dirs + files:
                    fp = os.path.join(p, fp)
                    fs.append(fp)
        fs = map(remove_basepath, fs)
        return sorted(fs)

    @classmethod
    def string_normalize_filepath(cls, fp):
        if not cls.fs_case_sensitive:
            fp = fp.lower()
        return fp

    @classmethod
    def string_is_same_file(cls, f, g):
        """Check if files are the same on disk"""
        return (cls.string_normalize_filepath(f) ==
                cls.string_normalize_filepath(g))

    @classmethod
    def io_invalid_rename(cls, f, g):
        """Handle rename on case insensitive fs, test not only for file exists,
        but also that it's the same file"""
        return os.path.exists(g) and not cls.string_is_same_file(f, g)


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
        if not os.path.exists(g) or cls.string_is_same_file(f, g):
            try:
                cls.do_rename_with_temp_exc(os.rename, f, g)
            except EXCEPTION_LIST as e:
                callbacks.error_handler(e)
        else:
            for fp in os.listdir(f):
                try:
                    cls.do_rename_exc(os.path.join(f, fp), os.path.join(g, fp))
                except EXCEPTION_LIST as e:
                    callbacks.error_handler(e)

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
            except EXCEPTION_LIST as e:
                callbacks.error_handler(e)

        # another pass on the dirs for case fixes
        dirlist = {}
        for (f, g) in lst:
            d = os.path.dirname(g)
            if d and d not in dirlist and os.path.exists(d):
                dirlist[d] = None
                cls.io_set_actual_path(d)
