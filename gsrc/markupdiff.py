# Copyright: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

import difflib

def diff_markup(x, y, tagpair_x, tagpair_y):
    xopen, xclose = tagpair_x
    yopen, yclose = tagpair_y

    xparts, yparts = [], []
    xcur, ycur = 0, 0

    sm = difflib.SequenceMatcher(None, x, y)
    for match in sm.get_matching_blocks():
        x_seg_diff = x[xcur:match.a]
        y_seg_diff = y[ycur:match.b]

        if x_seg_diff: x_seg_diff = "%s%s%s" % (xopen, x_seg_diff, xclose)
        if y_seg_diff: y_seg_diff = "%s%s%s" % (yopen, y_seg_diff, yclose)

        xparts.append(x_seg_diff)
        yparts.append(y_seg_diff)

        x_seg_same = x[match.a:match.a+match.size]
        y_seg_same = y[match.b:match.b+match.size]

        xparts.append(x_seg_same)
        yparts.append(y_seg_same)

        xcur = match.a+match.size
        ycur = match.b+match.size

    nonempty = lambda i: i != ''
    xparts = filter(nonempty, xparts)
    yparts = filter(nonempty, yparts)

    x_fmt = ''.join(xparts)
    y_fmt = ''.join(yparts)

    return x_fmt, y_fmt
