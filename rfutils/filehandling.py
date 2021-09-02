""" hassle-free filehandling """
import os
import gzip
import bz2
import zipfile
import lzma
            
OPENERS = {
    ".gz" : gzip.open,
    ".gzip" : gzip.open,
    ".bz2" : bz2.BZ2File,
    ".zip": zipfile.ZipFile,
    ".xz": lzma.open,
    ".lzma": lzma.open,
}

builtin_open = open

def open(filename, **kwds):
    _, extension = os.path.splitext(filename)
    opener = OPENERS.get(extension, builtin_open)
    return opener(filename, **kwd)

