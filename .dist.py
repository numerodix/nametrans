#!/usr/bin/env python
#
# Author: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

import fnmatch
import os
import re
import shutil
import sys
import traceback
import zipfile
from optparse import OptionParser


def normalize_filepath(fp):
    fp = os.path.normcase(fp)
    return fp


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

        # filter out comments
        lines = map(lambda line: re.sub('#.*$', '', line), lines)
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
            fp = normalize_filepath(fp)

            if prefix == '+':
                self.include.append(fp)
            elif prefix == '-':
                self.exclude.append(fp)

    def match_filepaths(self, filepaths):
        nfilepaths = []
        for pat in self.include:
            for fp in filepaths:
                fpn = normalize_filepath(fp)
                rx = '^' + fnmatch.translate(pat)
                if re.match(rx, fpn):
                    nfilepaths.append(fp)

        nnfilepaths = []
        for fp in nfilepaths:
            fpn = normalize_filepath(fp)
            excluded = False
            for pat in self.exclude:
                rx = '^' + fnmatch.translate(pat)
                if re.match(rx, fpn):
                    excluded = True
            if not excluded:
                nnfilepaths.append(fp)

        nfilepaths = list(set(nnfilepaths))
        nfilepaths.sort(key=lambda fp: fp.lower())

        return nfilepaths

class Package(object):
    def __init__(self, manifest_fp):
        self.manifest_fp = manifest_fp
        self.name = Manifest.get_name_from_filepath(manifest_fp)
        self.distfile_name = self.name

def make_dist_zip_callback(pkgname, zipfile_fp, zipfile_filesize): pass

class DistMaker(object):
    zipdist_dir = 'dist'

    @classmethod
    def find_packages(cls, fps=None):
        packages = {}
        if not fps:
            fps = fnmatch.filter(os.listdir('.'), '*.manifest')
        for fp in fps:
            pkg = Package(fp)
            packages[pkg.name] = pkg
        return packages

    @classmethod
    def get_distfile_name(cls, pkgname, release):
        distfile_name = pkgname
        if release:
            distfile_name = "%s-%s" % (pkgname, release)
        return distfile_name

    @classmethod
    def get_zipfp(cls, distfile_name):
        fpzip = os.path.join(cls.zipdist_dir, distfile_name + '.zip')
        return fpzip

    def find(self, path):
        fps = []
        rx = '^\.(?:' + re.escape(os.sep) + ')?'
        for r, dirs, files in os.walk(path):
            r = re.sub(rx, '', r)
            for fp in files:
                fp = os.path.join(r, fp)
                fps.append(fp)
        return fps

    def make_dist(self, pkg, fps):
        dist_dir = 'dist-%s' % pkg.distfile_name

        if os.path.isdir(dist_dir):
            shutil.rmtree(dist_dir)
        os.mkdir(dist_dir)

        for fp in fps:
            newfp = os.path.join(dist_dir, fp)
            newfp_dir = os.path.dirname(newfp)
            if not os.path.exists(newfp_dir):
                os.makedirs(newfp_dir)
            shutil.copy(fp, newfp)

    def make_dist_zip(self, pkg, fps):
        if not os.path.exists(self.zipdist_dir):
            os.makedirs(self.zipdist_dir)

        fpzip = self.get_zipfp(pkg.distfile_name)
        zf = zipfile.ZipFile(fpzip, 'w', zipfile.ZIP_DEFLATED)

        for fp in fps:
            fparc = os.path.join(pkg.distfile_name, fp)
            zf.write(fp, fparc)
        zf.close()

        make_dist_zip_callback(pkg.name, fpzip, os.stat(fpzip).st_size)

    def run(self, pkg, release=None, distdir=None, distzip=None):
        fps = self.find('.')
        fps.sort(key=lambda fp: fp.lower())

        manifest = Manifest(pkg.manifest_fp)
        fps = manifest.match_filepaths(fps)

        pkg.distfile_name = self.get_distfile_name(pkg.name, release)

        if distdir:
            self.make_dist(pkg, fps)
        if distzip:
            self.make_dist_zip(pkg, fps)


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-d", help="Produce dist directory",
                      dest="distdir", action="store_true")
    parser.add_option("-z", help="Produce dist zipfile",
                      dest="distzip", action="store_true")
    parser.add_option("-r", help="Set release name",
                      dest="release", action="store")
    (options, args) = parser.parse_args()

    packages = DistMaker.find_packages(args)

    for pkg in packages.values():
        try:
            print("Processing %s" % pkg.manifest_fp)
            DistMaker().run(pkg, release=options.release,
                            distdir=options.distdir,
                            distzip=options.distzip)
        except Exception, e:
            traceback.print_exc()
