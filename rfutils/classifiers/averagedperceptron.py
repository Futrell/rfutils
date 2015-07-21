from __future__ import print_function, division
from collections import defaultdict, Counter
import random

import classifier
import linearclassifier
import perceptron

class AveragedPerceptron(perceptron.Perceptron):
    def __init__(self, classes, num_training_iterations=1, **parameters):
        super(AveragedPerceptron, self).__init__(classes, **parameters)
        self.parameters.num_training_iterations = num_training_iterations
        self._totals = Counter()
        self._tstamps = Counter()
        self._i = 0

    def _update_weights(self, label, features, delta):
        self._i += 1
        for feature in features:
            weight = self.weights[label].get(feature, 0)
            self._totals[feature, label] += ((self._i - self._tstamps[feature, label])
                                            * weight)
            self._tstamps[feature, label] = self._i
            self.weights[label][feature] = weight + delta

    def _train(self, data):
        data = list(data)
        for _ in xrange(self.parameters.num_training_iterations):
            random.shuffle(data)
            for label, features in data:
                guesses = self.classify(features)
                if not guesses:
                    guess = random.choice(self.classes)
                else:
                    guess = guesses[0].label
                if guess != label:
                    self._update_weights(label, features, +1)
                    self._update_weights(guess, features, -1)
        self._average_weights()

    def _average_weights(self):
        for label, weights in self.weights.iteritems():
            for feature, weight in weights.iteritems():
                total = self._totals[feature, label]
                total += (self._i - self._tstamps[feature, label]) * weight
                averaged = round(total / float(self._i), 3) # new value for weights[label][feature]
                if averaged:
                    self.weights[label][feature] = averaged
