import numpy as np 
import pandas as pd 
from collections import defaultdict

class NaiveBayes:


    def __init__(self):
        self.feature_vector = defaultdict(float)

    def prior_init(self):

        # pior is freq of features
        self.prior_list = defaultdict(float)

    def load(self, definition):
        '''
        Loading definition from a json file, 
        a definition is a table to define feature vectors and priors.
        '''
        self.prior_init()
        self.prior_list

    def fit(self, Xtrain, Ytrain):
        '''
        Auto-extract a feature vector from a given document (str), 
        Note: I have no idea currently ...
        '''
        self.feature_vector

    def predict(self, X):
        return np.array([ 
            self.predict
        ])

    def predict_phrase(self, phrase):
        '''
        Predict a single phrase
        '''
        return np.round( self.calc_posterior(phrase) )

    def calc_posterior(self, phrase):
        '''
        Clac the posterior based on Bayes rule.
        '''
        return