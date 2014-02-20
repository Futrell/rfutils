# -*- coding: utf-8 -*-
""" is ling

Determine in an overly strict way if a string is linguistic in content for 
various languages, based on what characters it contains. The idea is to get 
high precision at the cost of recall, so you should only use this on data sets 
where you can afford to throw out a lot of data.

Currently supports:
    English (en)
    German (de)
    Spanish (es)
    French (fr)
    Italian (it)
    Portuguese (pt)
    Swedish (sv)
    Romanian (ro)
    Dutch (nl)
    Polish (pl)
    Czech (cs)
    Russian (ru)
    Hebrew (he)
    Chinese (zh)
    Japanese (ja)


"""
DEFAULT_LANG = "en"

# Alphabets/syllabaries/etc.
LATIN_ALPHABET = u"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
CYRILLIC_ALPHABET = u"абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
HEBREW_ALPHABET = u"אבגדהוזחטיכךלמםנןסעפףצץקרשת" + u'\u05c1\u05c2\u05bd\u05c4'
HIRAGANA = u"あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわゐゑをんゝっゃゅょがぎぐげござじずぜぞだぢづでどばびぶべぼぱぴぷぺぽゔゞぁぇ"
KATAKANA = u"アイウエオカキクケコガギグゲゴサシスセソザジズゼゾタチツテトダヂヅデドナニヌネノハヒフヘホバビブベボパピプペポマミムメモヤユヨラリルレロワヰヱヲンッーヽャュョァェヾ"

# Punctuation
BASIC_PUNCTUATION = u" ,:;!?'.-“”‘’\"" 
HEBREW_PUNCTUATION = u"׳־״"
CHINESE_PUNCTUATION = u" “”‘’。，、：；！？－…》《〈〉「」﹁﹂『』"
JAPANESE_PUNCTUATION = CHINESE_PUNCTUATION + u"・　"

# Supplemental combining diacritics
HEBREW_VOWELS = u"\u05b4\u05b5\u05b6\u05b7\u05b8\u05b9\u05ba\u05bb\u05bc\u05b0\u05b1\u05b2\u05b3"

BASE_ACCEPTABLE = LATIN_ALPHABET + BASIC_PUNCTUATION

# Define language-specific characters
ACCEPTABLE_CHARACTERS = {
    "en" : LATIN_ALPHABET,
    "de" : LATIN_ALPHABET + u"äüöÄÜÖß",
    "es" : LATIN_ALPHABET + u"áéíóúÁÉÍÓÚüÜñÑ",
    "fr" : LATIN_ALPHABET + u"éÉàèùÀÈÙâêîôûÂÊÎÔÛëïüËÏÜçÇ",
    "it" : LATIN_ALPHABET + u"àèòùìÀÈÒÙÌéóúíÉÓÚÍîÎ",
    "pt" : LATIN_ALPHABET + u"áâãàÁÂÃÀéêÉÊíÍóôõÓÔÕúÚ",
    "sv" : LATIN_ALPHABET + u"åÅäöÄÖ",
    "ro" : LATIN_ALPHABET + u"ĂăÂâÎîȘșŞşŢţȚțÃãǍǎ",
    "nl" : LATIN_ALPHABET + u"áéíóúàèëïöüĳÁÉÍÓÚÀÈËÏÖÜĲ",
    "pl" : LATIN_ALPHABET + u"ĄąĆćĘęŁłŃńÓóŚśŹźŻż",
    "cs" : LATIN_ALPHABET + u"ÁáČčĎďÉéĚěÍíŇňÓóŘřŠšŤťÚúŮůÝýŽž",
    "ru" : CYRILLIC_ALPHABET,
    "he" : HEBREW_ALPHABET + HEBREW_VOWELS,
    "zh" : u"", # Hanzi handled elsewhere
    "ja" : HIRAGANA + KATAKANA, # kanji handled elsewhere
}

ACCEPTABLE_PUNCTUATION = {
    "en" : BASIC_PUNCTUATION,
    "de" : BASIC_PUNCTUATION + u"„«»",
    "es" : BASIC_PUNCTUATION + u"¿¡«»",
    "fr" : BASIC_PUNCTUATION + u"«»",
    "it" : BASIC_PUNCTUATION + u"«»",
    "pt" : BASIC_PUNCTUATION + u"«»",
    "sv" : BASIC_PUNCTUATION,
    "ro" : BASIC_PUNCTUATION + u"«»",
    "nl" : BASIC_PUNCTUATION,
    "pl" : BASIC_PUNCTUATION + u"„«»",
    "cs" : BASIC_PUNCTUATION,
    "ru" : BASIC_PUNCTUATION + u'„«»' + u"—" + u'\u0301',
    "he" : BASIC_PUNCTUATION + HEBREW_PUNCTUATION,
    "zh" : CHINESE_PUNCTUATION,
    "ja" : JAPANESE_PUNCTUATION,
}

def make_tables():
    character_tables = {}
    character_tables_with_punctuation = {}

    for language in ACCEPTABLE_CHARACTERS:
        c_table = {ord(x) : None for x in ACCEPTABLE_CHARACTERS[language]}
        cp_table = {ord(x) : None for x in u"".join([ACCEPTABLE_CHARACTERS[language], 
                                              ACCEPTABLE_PUNCTUATION[language]])}

        character_tables[language] = c_table
        character_tables_with_punctuation[language] = cp_table

    return character_tables, character_tables_with_punctuation

character_tables, character_tables_with_punctuation = make_tables()

def is_linguistic(s, language=DEFAULT_LANG, punctuation=True):
    tables = character_tables_with_punctuation if punctuation else character_tables
        
    if language == "zh":
        return all(u"\u4e00" <= x <= u"\u9fff" 
                   for x in unicode(s).translate(tables["zh"]))
    elif language == "ja":
        return all(u"\u4e00" <= x <= u"\u9fff" 
                   for x in unicode(s).translate(tables["ja"]))
    elif language in tables:
        return not unicode(s).translate(tables[language])

def get_acceptability_fn(language, punctuation=True):
    def acceptable(s):
        return is_linguistic(s, language=language, punctuation=punctuation)
    return acceptable
