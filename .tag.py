#!/usr/bin/env python
#
# Copyright (c) 2009 Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.
#
# Tag a commit

import imp
import os
import re
import subprocess
import sys

dist = imp.load_source('dist', '.dist.py')


CONSTANTS_FILE = "src/versioninfo.py"
WEBCONSTANTS_FILE = "web/vars.php"


def invoke(cwd, args):
    print(">>>>> Running %s :: %s" % (cwd, " ".join(args)))
    popen = subprocess.Popen(args, cwd=cwd,
                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (out, _err) = popen.communicate()
    out = str(out).strip()
    return popen.returncode, out

def git_tag(version):
    args = ["git", "tag", "-a", version, "-m'%s'" % version]
    (code, out) = invoke(os.getcwd(), args)
    print(out)
    if code > 0: sys.exit(1)

def git_commit(version):
    args = ["git", "commit", "-a", "-mset version %s" % version]
    (code, out) = invoke(os.getcwd(), args)
    print(out)

def set_version(version, packages):
    s = open(CONSTANTS_FILE, 'r').read()
    s = re.sub('release = ".*"', 'release = "%s"' % version, s)
    open(CONSTANTS_FILE, 'w').write(s)

    def format_filesize(bytecount):
        i = 0
        bytecount = float(bytecount)
        while bytecount > 1023:
            bytecount /= 1024
            i += 1
        units = {0: 'b', 1: 'kb', 2: 'mb', 3: 'gb'}
        bc = "%s" % int(bytecount)
        if len(str(int(bytecount))) < 2:
            bc = "%.1f" % bytecount
        bytecount = "%s%s" % (bc, units[i])
        return bytecount

    s = open(WEBCONSTANTS_FILE, 'r').read()
    for pkg in packages.values():
        pkgname = re.sub('-', '_', pkg.name)
        size = format_filesize(pkg.zipfile_filesize)
        filename = pkg.zipfile_filename

        s = re.sub('[$]%s_filename\s*=\s*".*";' % pkgname,
                   '$%s_filename = "%s";' % (pkgname, filename), s)
        s = re.sub('[$]%s_filesize\s*=\s*".*";' % pkgname,
                   '$%s_filesize = "%s";' % (pkgname, size), s)
    open(WEBCONSTANTS_FILE, 'w').write(s)


if __name__ == "__main__":
    try:
        version = sys.argv[1]
    except IndexError:
        print("Usage:  %s <tag>" % sys.argv[0])
        sys.exit()

    packages = dist.DistMaker.find_packages()

    def f(pkgname, fp, filesize):
        packages[pkgname].zipfile_fp = fp
        packages[pkgname].zipfile_filename = os.path.basename(fp)
        packages[pkgname].zipfile_filesize = filesize
    dist.make_dist_zip_callback = f

    distmaker = dist.DistMaker()
    for pkg in packages.values():
        distmaker.run(pkg, release=version, distzip=True)

    set_version(version, packages)
    git_commit(version)
    git_tag(version)
