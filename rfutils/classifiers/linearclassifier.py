from __future__ import print_function
from collections import defaultdict

try:
    import pandas as pd
except ImportError:
    pd = None
    try:
        import numpy as np
    except ImportError:
        np = None

import classifier

def polynomial_kernel(degree, alpha=1.0):
    '''This kernel returns the dot product raised to some power.'''
    def run(values_and_weights):
        return (dot(values_and_weights) + alpha) ** degree
    return run

def dot(values_and_weights):
    return sum(v*w for v,w in values_and_weights)

class LinearClassifier(classifier.Classifier):
    def __init__(self, kernel=None, **parameters):
        self.parameters = classifier.ClassifierParameters()
        self.parameters.__dict__.update(parameters)
        self.classes = set()
        self.kernel = kernel or dot
        self.weights = defaultdict(Counter)

    def score(self, features, label):
        relevant_weights = self.weights[label]
        return self.kernel((value, relevant_weights[feature_name])
                            for feature_name, value in features
                            if feature_name in relevant_weights)

    def _classify(self, features):
        scores = ((label, self.score(features, label))
                  for label in self.classes)
        classifications = (classifier.Classification(score, label)
                            for label, score in scores)
        return sorted(classifications, reverse=True)
        
