from __future__ import print_function
import sys
import os
import uuid
import tempfile

from .. import systemcall
from .. import indices
import classifier

WORK_PATH = "/tmp/"
SVMLIGHT_PATH = "/Users/canjo/tools/svmlight/"

class SVMLightClassifier(classifier.Classifier):

    svm_learn = "svm_learn"
    svm_classify = "svm_classify"

    work_path = WORK_PATH
    svmlight_path = SVMLIGHT_PATH

    default_C = None

    def __init__(self, kernel='linear',
                 verbosity=1, C=default_C, cost_factor=None, 
                 poly_degree=2, rbf_gamma=1,
                 ):
        self.parameters = classifier.ClassifierParameters()
        self.parameters.__dict__.update({'kernel': kernel,
                                         'verbosity': verbosity,
                                         'C': C,
                                         'cost_factor': cost_factor,
                                         'poly_degree': poly_degree,
                                         'rbf_gamma': rbf_gamma,
                                         })

        self.feature_indices = indices.Indices(starting_index=1)
        self.label_indices = indices.Indices(starting_index=1)

        self.model = None

    def _preprocess_label(self, label):
        index = self.label_indices[label]
        if index == 1:
            return "-1"
        elif index == 2:
            return "+1"
        else:
            print("SVMLightClassifier only does binary classification. "
                  "Try using SVMMulticlassClassifier instead.", 
                   file=sys.stderr)
            raise Exception(str(self.indices.keylist))
                            
    def _preprocess_features(self, features):
        for feature, value in features:
            try:
                value = float(value)
            except ValueError, e:
                print("SVMLight only deals in real-valued features.", 
                      file=sys.stderr)
                raise e

            yield self.feature_indices[feature], value

    def _build_learn_cmd(self, train_filename, model_filename):
        cmd_list = [self.svm_learn, "-v", str(self.parameters.verbosity)]

        if self.parameters.C is not None:
            cmd_list.extend(["-c", str(self.parameters.C)])
        if self.parameters.cost_factor is not None:
            cmd_list.extend(["-j", str(self.parameters.cost_factor)])

        if self.parameters.kernel == "polynomial":
            cmd_list.extend(["-t", "1", "-d", str(self.parameters.poly_degree)])
        elif self.parameters.kernel == "rbf":
            cmd_list.extend(["-t", "2", "-g", str(self.parameters.rbf_gamma)])
        elif self.parameters.kernel == "sigmoid":
            cmd_list.extend(["-t", "3"])

        cmd_list.extend([train_filename, model_filename])

        return self.svmlight_path + " ".join(cmd_list)
                
    def _train(self, data):
        with tempfile.NamedTemporaryFile() as train_file:
            for label, features in data:
                # Print lines of the form:
                # +1 0:val 1:val 2:val
                # -1 0:val 3:val 4:val
                # etc.
                line = self._to_svmlight_line(label, features)
                print(line, file=train_file)
            train_file.flush()

            with tempfile.NamedTemporaryFile() as model_file:
                cmd = self._build_learn_cmd(train_file.name,
                                            model_file.name)
                systemcall.system_call(cmd) # this had better block!
                self.model = model_file.read()


    @staticmethod
    def _to_svmlight_line(label, features):
        return "%s %s" % (str(label), " ".join(":".join(map(str, fv))
                                               for fv in sorted(features)))

    def _classify(self, features):
        with tempfile.NamedTemporaryFile() as model_file:
            model_file.write(self.model)
            with tempfile.NamedTemporaryFile() as test_file:
                line = self._to_svmlight_line(0, features)
                print(line, file=test_file)
                test_file.flush()
                with tempfile.NamedTemporaryFile() as result_file:
                    svm_cmd = "%s%s %s %s %s" % (self.svmlight_path,
                                                    self.svm_classify,
                                                    test_file.name,
                                                    model_file.name,
                                                    result_file.name,
                                                    )
                    systemcall.system_call(svm_cmd)
                    result = result_file.read()
    
            return self._process_result(result)

    def _process_result(self, result_line):
        score = float(result_line.strip())
        label = self.label_indices.keylist[2 if score > 0 else 1]
        return classifier.Classification(score, label)
        
    def _classify_multiple(self, features):
        with tempfile.NamedTemporaryFile() as model_file:
            model_file.write(self.model)
            with tempfile.NamedTemporaryFile() as test_file:
                for fs in features:
                    line = self._to_svmlight_line(0, fs)
                    print(line, file=test_file)
                test_file.flush()

                with tempfile.NamedTemporaryFile() as result_file:
                    svm_cmd = "%s%s %s %s %s" % (self.svmlight_path,
                                                self.svm_classify,
                                                test_file.name,
                                                model_file.name,
                                                result_file.name
                                                )
                
                    systemcall.system_call(svm_cmd)
                    results = [line.strip() for line in result_file]
        results = (self._process_result(result) for result in results)
        return list(results)


