from __future__ import print_function, division
from collections import defaultdict, Counter
import random

import classifier
import linearclassifier

class Perceptron(linearclassifier.LinearClassifier):

    def __init__(self, classes, num_training_iterations=1, kernel=None):
        self.parameters = classifier.ClassifierParameters()
        self.parameters.num_training_iterations = num_training_iterations
        self.weights = defaultdict(Counter)
        self.classes = set(classes)
        self.kernel = kernel or linearclassifier.dot

    def _update_weights(self, label, features, delta):
        for feature_name, _ in features:
            self.weights[label][feature_name] += delta

    def _train(self, data):
        for label, features in data:
            guess = self.classify(features)[0].label
            if guess != label:
                self._update_weights(guess, features, -1)
                self._update_weights(label, features, +1)
