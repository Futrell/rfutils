
""" Utilities to convert between writing systems. """

CYRILLIC_TO_LATIN = "data/cyrillic2latin.tsv"
ARABIC_TO_LATIN = "data/arabic2latin.tsv"

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
        d = {}
        with open(filename, mode='rt') as infile:
            for line in infile:
                if not line.startswith(comment_marker):
                    source, target = line.strip("\n").split(sep)
                    d[source] = target
        self.dictionary = d

    def transcribe(self, string):
        return "".join(self.dictionary.get(x, x) for x in string)

class CyrillicToLatin(Transcriber):
    filename = CYRILLIC_TO_LATIN

class ArabicToLatin(Transcriber):
    filename = ARABIC_TO_LATIN

    def transcribe(self, string):
        result = super(ArabicToLatin, self).transcribe(string)
        result = (
            result
            .replace("aS", "Sa")
            .replace("iS", "Si")
            .replace("uS", "Su")
        )            
        result = list(result)
        for i, x in enumerate(result):
            if x == 'S':
                result[i] = result[i-1]
        result = "".join(result)
        return (
            result
            .replace("0", "")
            .replace("iy", "ī")
            .replace("uw", "ū")
            .replace("aʾ", "ā")
        )
    
class FanJian(Transcriber):
    """ cong fantizi dao jiantizi """
    def __init__(self):
        import cjklib
        from cjklib.cjknife import CharacterInfo
        self.character_info = CharacterInfo()

    def transcribe(self, string):
        return u"".join(x[0] for x in self.character_info.getSimplified(text))

    
    
