import random

import randomclassifier

def test_random_classifier():
    random.seed(0)
    rc = randomclassifier.RandomClassifier('abc')
    result = rc.classify([('cat', 1)])
    assert result[0].label == 'a'
    assert result[1].label == 'b'
    assert result[2].label == 'c'

test_random_classifier()    