# Author: Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

import os
import re
import shutil

PIXBUF_LOADERS_FILE = 'gdk-pixbuf.loaders'
PIXBUF_LOADERS_PATH = '"C:/Program Files/GtkSharp/2.12'

def pathtransform(fp):
    parts = fp.split(os.sep)
    if parts[0] == 'win32-libs':
        if fp.endswith('-sharp.dll'):
            fp = os.path.join('bin', os.path.basename(fp))
        else:
            fp = re.sub('^win32-libs/GtkSharp/2.12', 'bin/gtk', fp)
    return fp

def _patch_pixbuf_loaders_path(fp):
    content = open(fp).read()
    orig_path = PIXBUF_LOADERS_PATH
    content = re.sub('(?m)^' + re.escape(orig_path), '"..', content)
    return content

def filecopy(fp, newfp):
    if os.path.basename(fp) == PIXBUF_LOADERS_FILE:
        content = _patch_pixbuf_loaders_path(fp)
        open(newfp, 'w').write(content)
    else:
        shutil.copy(fp, newfp)

def writezip(zf, fp, fparc):
    if os.path.basename(fp) == PIXBUF_LOADERS_FILE:
        content = _patch_pixbuf_loaders_path(fp)
        zf.writestr(fparc, content)
    else:
        zf.write(fp, fparc)
