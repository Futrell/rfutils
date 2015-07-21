import random
try:
    import cPickle as pickle
except ImportError:
    import pickle
        
import perceptron

def test_perceptron():
    random.seed(0)
    training = pickle.load(open("data/svmtrain.pickle"))
    testing = pickle.load(open("data/svmtest.pickle"))
    random.shuffle(training)
    p = perceptron.Perceptron({'1', '-1'})
    p.train(training)
    results = [p.classify(x[1]) for x in training]
    accuracy = sum(results[i][0].label == training[i][0]
                   for i in range(len(results)))
    assert accuracy == 1943

    results = [p.classify(x[1]) for x in testing]
    accuracy = sum(results[i][0].label == testing[i][0]
                    for i in range(len(results)))
    assert accuracy == 291 # not too good :)
    
test_perceptron()
