import pickle
from svmlight import SVMLightClassifier

def test_svmlight_classifier():
    training = pickle.load(open("data/svmtrain.pickle"))
    testing = pickle.load(open("data/svmtest.pickle"))
    c = SVMLightClassifier()
    c.train(training)
    results = [c.classify(x[1]) for x in testing]
    assert results[0].label == '1'
    assert results[-1].label == '-1'
    results = c.classify_multiple(x[1] for x in testing)
    assert results[0].label == '1'
    assert results[-1].label == '-1'
    
test_svmlight_classifier()
