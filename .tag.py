#!/usr/bin/env python
#
# Copyright (c) 2009 Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.
#
# Tag a commit

import os
import re
import subprocess
import sys

CONSTANTS_FILE = "src/versioninfo.py"


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
    args = ["git", "commit", "-a", "-m'set version %s'" % version]
    (code, out) = invoke(os.getcwd(), args)
    print(out)

def set_version(version):
    s = open(CONSTANTS_FILE, 'r').read()
    s = re.sub('release = ".*"', 'release = "%s"' % version, s)
    open(CONSTANTS_FILE, 'w').write(s)


if __name__ == "__main__":
    try:
        version = sys.argv[1]
    except IndexError:
        print("Usage:  %s <tag>" % sys.argv[0])
        sys.exit()

    set_version(version)
    git_commit(version)
    git_tag(version)
