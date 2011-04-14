#!/usr/bin/env python

import re

def main():
    fp = 'Makefile'
    s = open(fp).read()
    s = re.sub('rm(?: -f)?', 'del', s)
    s = re.sub('gmcs', 'csc', s)
    s = re.sub(':=', '=', s)
    s = re.sub('/', '\\\\', s)
    s = re.sub('\$<', '$**', s)
    open(fp, 'w').write(s)
    print('Wrote %s' % fp)

main()
