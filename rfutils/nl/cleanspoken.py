from __future__ import print_function
import sys

try:
    range = xrange
except NameError:
    pass

BLACKLIST_FILENAME = "data/spoken_blacklist.txt"

def read_file_as_set(filename):
    with open(filename, "rt") as infile:
        s = set(line.strip() for line in infile)
    return s

BLACKLIST = read_file_as_set(BLACKLIST_FILENAME)


def remove_duplicate_sequences(iterable, seq_len, key_fn=None):
    """ remove duplicate sequences

    Removes adjacent duplicate sequences of given length from an iterable.

    Example:
        >>> remove_duplicate_sequences("abababcccc", 2)
        ['a', 'b', 'c', 'c']

    """
    if key_fn is None:
        key_fn = lambda x:x

    sequence = list(iterable)

    for i, item in enumerate(sequence):
        this_seq = list(map(key_fn, sequence[i:(i+seq_len)]))
        while True:
            next_seq = list(map(key_fn, sequence[(i+seq_len):(i+2*seq_len)]))
            if this_seq == next_seq:
                del sequence[(i+seq_len):(i+2*seq_len)]
            else:
                break
    return sequence

def clean_spoken(words, key_fn=None):
    """ Clean spoken language

    This function attempts to remove some of the kind of garbage and errors
    you see in transcribed spoken language, so that it can be used to train
    language models etc.

    Probably works best when punctuation has been removed.

    Currently it does these things:
        (1) Remove disfluencies and filled pauses as defined in BLACKLIST.
        (2) Remove duplicate sequences of 1-3 words, retaining the first, 
            e.g. "he is he is he is a cat" -> "he is a cat".

    """
    if key_fn is None:
        key_fn = lambda x: x

    # remove disfluencies etc.
    words = (w for w in words if key_fn(w) not in BLACKLIST)

    # Remove x+, (xy)+, (xyz)+
    for i in range(1, 4):
        words = remove_duplicate_sequences(words, i, key_fn=key_fn)

    return list(words)


def test():
    assert remove_duplicate_sequences("abab", 2) == list("ab")
    assert remove_duplicate_sequences("ababab", 2) == list("ab")
    assert remove_duplicate_sequences("abababcccc", 2) == list("abcc")
    assert remove_duplicate_sequences("abcabcab", 3) == list("abcab")
    assert (clean_spoken("this is a this is a uh um test".split()) == 
            "this is a test".split())

def clean_lines(lines):
    for line in lines:
        words = line.strip().split()
        yield clean_spoken(words)

def main(filename=None):
    if filename is None:
        for line in clean_lines(sys.stdin):
            print(" ".join(line))
    else:
        with open(filename, "rt") as infile:
            for line in clean_lines(infile):
                print(" ".join(line))

if __name__ == "__main__":
    main(*sys.argv[1:])
