#!/usr/bin/env python
#
# Author: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

import fnmatch
import os
import re
import shutil
import sys


class Manifest(object):
    def __init__(self, fp):
        self.include = []
        self.exclude = []

        self.parse(fp)

    @classmethod
    def get_name_from_filepath(cls, filepath):
        root, _ = os.path.splitext(filepath)
        m = re.search('\.(.*)', root)
        return m.group(1)

    def process_imports(self, lines):
        nlines = []
        for line in lines:
            m = re.search('^#include (.*)$', line)
            if m:
                fp_imp = m.group(1)
                imp_content = open(fp_imp).read()
                imp_lines = imp_content.split('\n')
                nlines.extend(imp_lines)
            else:
                nlines.append(line)
        return nlines

    def parse(self, filepath):
        content = open(filepath).read()
        lines = content.split('\n')
        
        # process imports
        lines = self.process_imports(lines)

        # filter out empty
        lines = filter(lambda line: line != '', lines)
        # make unique
        lines = list(set(lines))
        # strip
        lines = map(lambda fp: fp.strip(), lines)

        for line in lines:
            m = re.search('^(?:([+]|[-]) )?(.*)', line)
            [prefix, fp] = m.groups()

            # remove ./
            rx = '^\.(?:' + re.escape(os.sep) + ')?'
            fp = re.sub(rx, '', fp)
            # normalize os.sep
            fp = os.path.normcase(fp)

            if prefix == '+':
                self.include.append(fp)
            elif prefix == '-':
                self.exclude.append(fp)

    def match_filepaths(self, filepaths):
        nfilepaths = []
        for pat in self.include:
            for fp in filepaths:
                rx = '^' + fnmatch.translate(pat)
                if re.match(rx, fp):
                    nfilepaths.append(fp)

        nnfilepaths = []
        for fp in nfilepaths:
            excluded = False
            for pat in self.exclude:
                rx = '^' + fnmatch.translate(pat)
                if re.match(rx, fp):
                    excluded = True
            if not excluded:
                nnfilepaths.append(fp)

        nfilepaths = list(set(nnfilepaths))
        nfilepaths.sort(key=lambda fp: fp.lower())

        return nfilepaths


class DistMaker(object):
    def find(self, path):
        fps = []
        rx = '^\.(?:' + re.escape(os.sep) + ')?'
        for r, dirs, files in os.walk(path):
            r = re.sub(rx, '', r)
            for fp in files:
                fp = os.path.join(r, fp)
                fps.append(fp)
        return fps

    def make_dist(self, manifest_name, fps):
        dist_dir = 'dist-%s' % manifest_name

        if os.path.isdir(dist_dir):
            shutil.rmtree(dist_dir)
        os.mkdir(dist_dir)

        for fp in fps:
            newfp = os.path.join(dist_dir, fp)
            if os.path.isdir(fp):
                shutil.copytree(fp, newfp)
            else:
                fp_dir = os.path.dirname(fp)
                newfp_dir = os.path.dirname(newfp)
                if not os.path.exists(newfp_dir):
                    os.makedirs(newfp_dir)
                    shutil.copystat(fp_dir, newfp_dir)
                shutil.copy(fp, newfp)

    def run(self, manifest_file=None):
        manifest_name = Manifest.get_name_from_filepath(manifest_file)

        fps = self.find('.')
        fps.sort(key=lambda fp: fp.lower())

        manifest = Manifest(manifest_file)
        fps = manifest.match_filepaths(fps)

        self.make_dist(manifest_name, fps)


if __name__ == '__main__':
    fp = None
    try:
        fp = sys.argv[1]
    except IndexError: pass

    DistMaker().run(manifest_file=fp)
