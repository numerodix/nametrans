# Copyright: Martin Matusiak <numerodix@gmail.com>

from __future__ import absolute_import

import re
from typing import Union


class FilepathTransformer(object):
    @classmethod
    def to_unicode(self, s: Union[bytes, str]) -> str:
        us = s.decode('utf-8', 'ignore')
        return us

    @classmethod
    def from_unicode(self, us: Union[str, bytes]) -> bytes:
        s = us.encode('utf-8', 'ignore')
        return s

    @classmethod
    def by_regex(cls, rx_from: str, rx_to: str, s: str) -> str:
        return re.sub(rx_from, rx_to, s)

    @classmethod
    def capitalize(cls, s: str) -> str:
        cap = lambda m: m.group(1).upper() + m.group(2).lower()
        s = re.sub("(?u)(?<![0-9\w'])(\w)([\w']*)", cap, s)
        return s

    @classmethod
    def make_lowercase(cls, s: str) -> str:
        tolower = lambda m: m.group(1).lower()
        s = re.sub('(?u)([\w]*)', tolower, s)
        return s

    @classmethod
    def make_spaces_underscores(cls, s: str) -> str:
        s = re.sub(' ', '_', s)
        return s

    @classmethod
    def do_trim(cls, s: str) -> str:
        # check endpoints
        s = cls.by_regex('^([ ]|-)*', '', s)
        s = cls.by_regex('([ ]|-)*$', '', s)
        return s

    @classmethod
    def make_neat(cls, s: str) -> str:
        # Phase 1: Normalize junk characters to canonical forms.
        # After this phase the string only contains word chars, spaces,
        # hyphens, plus signs, and brackets.
        s = cls.by_regex('_{2,}', '-', s)
        s = cls.by_regex('(?<!^)\.', ' ', s)
        s = cls.by_regex('_', ' ', s)
        s = cls.by_regex('#', ' ', s)
        s = cls.by_regex(':', ' ', s)
        # Phase 2: Collapse separators. Now that junk characters have been
        # normalized, all separator patterns are visible to these rules.
        s = cls.by_regex('-{2,}', '-', s)
        s = cls.by_regex(r'-(\s*-)+', '-', s)
        s = cls.by_regex('\[ *?\]', ' ', s)
        s = cls.by_regex('\( *?\)', ' ', s)
        s = cls.by_regex('[ ]{2,}', ' ', s)
        # Phase 3: Insert spacing around hyphens and plus signs. Phase 2
        # guarantees at most one hyphen/plus in any local region, so this
        # cannot create new separator pairs.
        s = cls.by_regex('(?<!\s)-', ' -', s)
        s = cls.by_regex('-(?!\s)', '- ', s)
        s = cls.by_regex('(?<!\s)[+]', ' +', s)
        s = cls.by_regex('[+](?!\s)', '+ ', s)
        # Phase 4: Final whitespace normalization.
        s = cls.by_regex('[ ]{2,}', ' ', s)
        s = cls.do_trim(s)
        return s

    @classmethod
    def make_neater(cls, s: str) -> str:
        # bracket-y junk
        s = cls.by_regex('\[.*?\]', ' ', s)
        s = cls.by_regex('\(.*?\)', ' ', s)
        s = cls.do_trim(s)
        return s
