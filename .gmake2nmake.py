#!/usr/bin/env python

import re

def main():
    s = open('Makefile').read()
    s = re.sub('rm(?: -f)?', 'del', s)
    s = re.sub('gmcs', 'csc', s)
    s = re.sub(':=', '=', s)
    s = re.sub('/', '\\\\', s)
    s = re.sub('\$<', '$**', s)
    open('Makefile', 'w').write(s)

main()
