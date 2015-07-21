""" Utilities to convert between writing systems. """

CYRILLIC_TO_LATIN_TSV = "data/cyrillic2latin.tsv"

import ..filehandling as fh    
    
class Transcriber(object):
    sep = u"\t"
    comment_marker = u"#"

    def __init__(self, filename=None, sep=None, comment_marker=None):
        if filename is None:
            filename = self.filename
        if sep is None:
            sep = self.sep
        if comment_marker is None:
            comment_marker = self.comment_marker
        self.dictionary = fh.file_as_dict(filename, sep=sep,
                                          comment_marker=comment_marker)

    def transcribe(self, string):
        return u"".join(self.dictionary[x] for x in string)

class CyrillicToLatin(Transcriber):
    filename = CYRILLIC_TO_LATIN_TSV

class FanJian(Transcriber):
    """ cong fantizi dao jiantizi """
    def __init__(self):
        import cjklib
        from cjklib.cjknife import CharacterInfo
        self.character_info = CharacterInfo()

    def transcribe(self, string):
        return u"".join(x[0] for x in self.character_info.getSimplified(text))

    
    
