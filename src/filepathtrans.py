# Copyright: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

import re


class FilepathTransformer(object):
    @classmethod
    def by_regex(cls, rx_from, rx_to, s):
        return re.sub(rx_from, rx_to, s)

    @classmethod
    def capitalize(cls, s):
        cap = lambda m: m.group(1).upper() + m.group(2).lower()
        s = re.sub("(?u)(?<![0-9\w'])(\w)([\w']*)", cap, s)
        return s

    @classmethod
    def make_lowercase(cls, s):
        tolower = lambda m: m.group(1).lower()
        s = re.sub('(?u)([\w]*)', tolower, s)
        return s

    @classmethod
    def make_spaces_underscores(cls, s):
        s = re.sub(' ', '_', s)
        return s

    @classmethod
    def do_trim(cls, s):
        # check endpoints
        s = cls.by_regex('^([ ]|-)*', '', s)
        s = cls.by_regex('([ ]|-)*$', '', s)
        return s

    @classmethod
    def make_neat(cls, s):
        # too many hyphens and underscores
        s = cls.by_regex('_{2,}', '-', s)
        s = cls.by_regex('-{2,}', '-', s)
        s = cls.by_regex('-[ ]+-', '-', s)
        # junk-y chars past the start of the string
        s = cls.by_regex('(?<!^)\.', ' ', s)
        s = cls.by_regex('_', ' ', s)
        s = cls.by_regex('#', ' ', s)
        s = cls.by_regex(':', ' ', s)
        # let's have spaces around hyphen
        s = cls.by_regex('(?<!\s)-', ' -', s)
        s = cls.by_regex('-(?!\s)', '- ', s)
        s = cls.by_regex('(?<!\s)[+]', ' +', s)
        s = cls.by_regex('[+](?!\s)', '+ ', s)
        # empty brackets
        s = cls.by_regex('\[ *?\]', ' ', s)
        s = cls.by_regex('\( *?\)', ' ', s)
        # normalize spaces
        s = cls.by_regex('[ ]{2,}', ' ', s)
        s = cls.do_trim(s)
        return s

    @classmethod
    def make_neater(cls, s):
        # bracket-y junk
        s = cls.by_regex('\[.*?\]', ' ', s)
        s = cls.by_regex('\(.*?\)', ' ', s)
        s = cls.do_trim(s)
        return s
