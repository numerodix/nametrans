# Copyright: Martin Matusiak <numerodix@gmail.com>

from __future__ import absolute_import

import itertools
import re
import string


class DigitString(object):
    def __init__(self, fp, prefix='', postfix=''):
        self.prefix = prefix
        self.postfix = postfix

        digit_runs = re.finditer("([0-9]+)", fp)
        nondigit_runs = re.finditer("([^0-9]+)", fp)

        digit_spans = [m.span() for m in digit_runs if digit_runs]
        nondigit_spans = [m.span() for m in nondigit_runs if nondigit_runs]

        if nondigit_spans and nondigit_spans[0][0] != 0:
            nondigit_spans = [(0, 0)] + nondigit_spans

        def take_slice(tup):
            x, y = tup
            return fp[x:y]

        self.numbers = list(map(take_slice, digit_spans))
        self.chars = list(map(take_slice, nondigit_spans))

    def has_digits(self):
        return len(self.numbers) > 0

    def process_field_number(self, field):
        assert(field != 0)
        field = field - 1 if field > 0 else field
        return field

    def get_field_count(self):
        return len(self.numbers)

    def get_field(self, field):
        field = self.process_field_number(field)
        try:
            return self.numbers[field]
        except IndexError:
            return ""

    def set_field(self, field, number):
        field = self.process_field_number(field)
        assert(type(number) == str)
        assert(re.match('^[0-9]+$', number))
        try:
            self.numbers[field] = number
        except IndexError:
            pass

    def set_field_width(self, field, width):
        val = self.get_field(field)
        if val:
            val = str(int(val)).zfill(width)
            self.set_field(field, val)

    def get_string(self):
        s = ''
        for (a, b) in itertools.zip_longest(self.chars,
                                            self.numbers, fillvalue=''):
            s += a + b
        return self.prefix, s, self.postfix
