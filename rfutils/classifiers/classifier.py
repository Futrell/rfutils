from collections import namedtuple

Classification = namedtuple("Classification", "score label")

class ClassifierParameters(object):
    pass

class Classifier(object):
    """ Classifier

    Provides a common Python interface for many different classifiers.
    
    A classifier has two main methods: 
        train: Which takes training data and trains the classifier.
        classify: Which takes a set of features and classifies it.

    We also have these attributes:
        classify_multiple: Classify multiple test data points in batch.
        trained: A boolean value for whether this instance has been trained.

    Parameters are given when initializing the classifier. 

    The train method both modifies state and returns a reference to the 
    trained classifier, allowing more than one programming style. For example,
    to make an SVMLight model with given test data and C=3, you can do it 
    two ways:
    
    >>> model = SVMLightClassifier(C=3)
    >>> model.train(training_data)
    >>> res = model.classify(test_data)

    Or:

    >>> res = SVMLightClassifier(C=3).train(training_data).classify(test_data)

    The Classifier class itself is abstract. Most subclasses are wrappers
    around other utilities.
    
    """

    trained = False

    def __init__(self, **parameters):
        """ Initialize an classifier with given parameters. """
        self.parameters = ClassifierParameters()
        self.parameters.__dict__.update(parameters)
    
    def train(self, data):
        """ train

        Train a classifier using training data. Change the state of the 
        current classifier instance, and also return the trained model. 
        Existing training is overwritten.

        Arguments:
            - data: An iterable of training examples, which are iterables of 
                length 2 where the first element is the outcome variable, and 
                the second element is an iterable of feature-value pairs.

        Returns:
            A trained Classifier.

        """
        data = ((self._preprocess_label(label), 
                self._preprocess_features(features))
                for label, features in data)
        self._train(data)
        self.trained = True
        return self

    def _train(self, data):
        raise NotImplementedError

    def _preprocess_label(self, label):
        return label

    def _preprocess_features(self, features):
        return features

    def classify(self, features):
        """ classify

        Given an iterable of features (feature-value pairs), return a
        classification. For a binary classifier this is usually just a
        single classification. For a multiclass classifier this is a
        list of classifications sorted by confidence.

        """
        features = self._preprocess_features(features)
        return self._classify(features)

    def classify_multiple(self, features):
        """ classify multiple

        Give classifications for multiple test examples.

        """
        features = (self._preprocess_features(f) for f in features)
        return self._classify_multiple(features)

    def _classify_multiple(self, features):
        return [self._classify(f) for f in features]

    def _classify(self, features):
        raise NotImplementedError
