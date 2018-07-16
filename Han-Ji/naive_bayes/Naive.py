import numpy as np 
import pandas as pd 
from collections import defaultdict

class NaiveBayes:


    def __init__(self, names=[], iterables=[], likelihoods=[]):
        self.feature_vector = defaultdict(float)
        self.definition_dict = self._convert2def(names, iterables, likelihoods)

    def prior_init(self):
        # pior is freq of features
        self.prior_list = defaultdict(float)

    def _convert2def(self, names, iterables, likelihoods):
        '''
        convert 3 lists, names, iterables, and likelihoods into definition dictionary. 

        Definition dict policy:
            definition_dict = {
                "data" : [
                    {'name' : "數字",
                    'iterables': "是元正𨳝一二三四五六七八九十廿卅",
                    'likelihood': 0.6},  
                ],
                "columns" : [
                    {"name" : '(str) use few chars to represent the feature name', 
                    "iterables": '(str, or any iterable) any iterable can be iterated', 
                    "likelihood": '(float) the independent prob of the feature'}
                ] 
            }
        '''
        definition_dict = {
            "data" : [],
            "columns" : {
                "name" : '(str) use few chars to represent the feature name', 
                "iterable": '(str, or any iterable) any iterable can be iterated', 
                "likelihood": '(float) the independent prob of the feature'}
        }

        for name,iterable,likelihood in zip(names,iterables,likelihoods):
            definition_dict['data'].append(
                {"name" : name,
                "iterable" : iterable, 
                "likelihood" : likelihood}
            )        

        return definition_dict

    def load_json(self, filename):
        import json

        with open(filename, "r", encoding="utf-8") as file:
            self.definition_dict = json.load(filename)        

    def load(self, definition):
        '''
        Loading definition from a json file, 
        a definition is a table to define feature vectors and priors.
        '''
        self.definition_dict = definition

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