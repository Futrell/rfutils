""" hassle-free filehandling """
from __future__ import print_function

import __builtin__
import sys
import os
import gzip
import bz2
import zipfile
import codecs

try:
    import lzma
except ImportError:
    try:
        from backports import lzma
    except ImportError:
        pass
            
OPENERS = {
    ".gz" : gzip.open,
    ".gzip" : gzip.open,
    ".bz2" : bz2.BZ2File,
    ".zip": zipfile.ZipFile,
}

try:
    OPENERS.update({".xz": lzma.open,
                    ".lzma": lzma.open,
                    })
except NameError:
    pass

builtin_open = __builtin__.open

stdout = codecs.getwriter('utf-8')(sys.stdout)
stdin = codecs.getreader('utf-8')(sys.stdout)

def open(filename, mode="rb", encoding=None, errors="strict", **kwargs):
    """ Open anything the right way with no problem. Hopefully! :) """
    if "b" not in mode:
        mode += "b"
    _, extension = os.path.splitext(filename)
    file = OPENERS.get(extension, builtin_open)(filename, mode=mode, **kwargs)
    if encoding is None:
        return file
    else:
        info = codecs.lookup(encoding)
        srw = codecs.StreamReaderWriter(file, info.streamreader, 
                                        info.streamwriter, errors)
        srw.encoding = encoding
        return srw

def file_as_dict(filename, sep="\t", key_col=0, val_col=1, comment_marker="#", 
                 val_type=None):
    def gen():
        with open(filename, "r", encoding="utf-8") as infile:
            if val_type is None:
                for i, line in enumerate(infile):
                    if line.startswith(comment_marker):
                        continue
                    parts = line.strip().split(sep)
                    try:
                        yield parts[key_col], parts[val_col]
                    except IndexError:
                        print("Error reading %s at line %d" % (filename, i), 
                              file=sys.stderr)

            else:
                for i, line in enumerate(infile):
                    if line.startswith(comment_marker):
                        continue
                    parts = line.strip().split(sep)
                    try:
                        yield parts[key_col], val_type(parts[val_col])
                    except IndexError:
                        print("Error reading %s at line %d" % (filename, i), 
                              file=sys.stderr)

    return dict(gen())
