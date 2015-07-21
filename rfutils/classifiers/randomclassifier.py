""" A classifier that makes random predictions. Useful as a mockup. """
import random

import classifier

class RandomClassifier(classifier.Classifier):
    def __init__(self, classes, **parameters):
        super(RandomClassifier, self).__init__(**parameters)
        self.classes = classes
        
    def _classify(self, features):
        return sorted((classifier.Classification(random.random(), label)
                      for label in self.classes), reverse=True)
