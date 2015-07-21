from __future__ import print_function
import sys
import tempfile
import codecs
import itertools

import systemcall
import kenlm

KENLM_PATH = "/Users/canjo/src/kenlm/kenlm/"
KENLM_CMD =  KENLM_PATH + "bin/lmplz -o %d < %s > %s"

class KenLM(object):
    def __init__(self, n=5, train_cmd=KENLM_CMD):
        self.n = n
        self.data_file=codecs.getwriter('utf-8')(tempfile.NamedTemporaryFile())
        self.model_file = tempfile.NamedTemporaryFile()
        self.data_updated = False
        self._model = None
        self.train_cmd = train_cmd

    def updated_model(self):
        command = self.train_cmd % (self.n,
                                    self.data_file.name,
                                    self.model_file.name,
                                    )
        self.data_file.flush()
        systemcall.system_call(command)
        try:
            return kenlm.LanguageModel(self.model_file.name)
        except IOError as e:
            print("Could not train kenlm model. See kenlm output above.",
                  file=sys.stderr)
            raise e

    @property
    def model(self):
        if self.data_updated:
            self._model = self.updated_model()
            self.data_updated = False
        return self._model

    def __del__(self):
        self.data_file.close()
        self.model_file.close()

    def add_data(self, thing):
        # Add data to a text file; set a flag indicating that data was modified.
        # Model inference over the data won't happen until self.model is
        # accessed.
        print(" ".join(thing), file=self.data_file)
        self.data_updated = True

    def logp_conditioned(self, words, conditions):
        # Won't be called by DepLM unless we want backoff of dependency context
        conditions = list(conditions)
        scores = self.model.full_scores(" ".join(itertools.chain(conditions,
                                                                 words)))
        return sum(score for score, _ in itertools.islice(scores,
                                                          len(conditions),
                                                          None))

    def logp(self, words):
        return self.model.score(" ".join(words))
