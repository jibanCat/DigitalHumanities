import sys 
import os
import re
import numpy as np 
import pandas as pd 
from collections import defaultdict

class NaiveBayes:
    """
    A NaiveBayes class designed for calculate the probability of a 
    specific type of tags (time, place, person names, etc). 
    It is currently only able to calculate the probability for one sentence a 
    a time. 
    Also noted that I use hard-coded definition of likelihood tables to 
    calculate the posterior. Users are expected to use their domain knowledge 
    to decide the likelihoods based on whatever methods.

    I followed a similar way for using Bayes rule as in 
        <How to Write a Spelling Corrector: https://norvig.com/spell-correct.html>

    Args:
        names (list) : a list of feature names.
        iterables (list) : a list of iterables corresponding to feature names.
        likelihoods (list) : a list of probabilities corresponing to feature names.
        prior (float) : a prior probability associated with the type of tag you want to calssify.
    """

    def __init__(self, names=[], iterables=[], likelihoods=[], prior=0.5, filename=None):
        self.prior = prior
        self.feature_vector = defaultdict(int)
        self.definition_dict = self._convert2def(names, iterables, likelihoods)

        if filename != None and os.path.exists(filename):
            self.load_json(filename)

        self.feature_vector_init()
        self.likelihood_init()
        self.iterable_init()

    def feature_vector_init(self):
        try:
            for feature_dict in self.definition_dict['data']:
                self.feature_vector[feature_dict['name']] = 0
        except KeyError as e: 
            print('[Warning] No avaliable features currently.', e)

    def likelihood_init(self):
        self.likelihoods = { x['name']: x['likelihood'] for x in self.definition_dict['data'] }

    def iterable_init(self):
        self.iterables = { x['name']: x['iterable'] for x in self.definition_dict['data'] }

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
            self.definition_dict = json.load(file)        

    def to_json(self, filename):
        import json

        with open(filename, "w", encoding="utf-8") as file:
            json.dump(self.definition_dict, file)

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

    def calc_posterior(self, phrase, regularize=None):
        '''
        Clac the posterior based on Bayes rule.

        Args:
            phrase (str) : the phrase you want to calc the naive bayes probability.
            regularize (float, default None) : if float, using this number as 
                punishment for irrelevant words

        Returns:
            prob (float) : the posterior probability of phrase being classified
        '''
        self.feature_vector_init()
        self.update_feature_vector(phrase, regularize=regularize)
        return self._calc_bayes_rule_iid(self.feature_vector, self.likelihoods, self.prior)

    def _calc_bayes_rule_iid(self, feature_vector, likelihood, prior):
        """Calc the posterior using bayes theorem. 
        The assumption here is the naive bayes, so the prob of features 
        are independent. The joint prob of likelihood is a prod of individual
        feature prob."""
        positive_likelihood = prior * np.prod([
            likelihood[key]**hits for key, hits in feature_vector.items()
        ])
        negative_likelihood = (1 - prior) * np.prod([
            (1 - likelihood[key])**hits for key, hits in feature_vector.items()
        ])

        # Bayes theorem
        posterior = positive_likelihood / (positive_likelihood + negative_likelihood)
        return posterior        

    def update_feature_vector(self, phrase, regularize=None):
        """
        update the feature vector based on the list of features and a given phrase and 
        a given feature name.

        Args:
            phrase (str) : the phrase you want to calc the naive bayes probability.
            regularize (float, default None) : if float, using this number as 
                punishment for irrelevant words
        """
        matched_words = set([])

        for name in self.iterables.keys():
            for x in self.iterables[name]:
                if x in phrase:
                    self.feature_vector[name] += 1
                    matched_words.add(x)

        if type(regularize) == float:
            self.likelihoods['irrelevant']    = regularize
            self.feature_vector['irrelevant'] = len(re.sub(
                r"[{}]".format(''.join(matched_words)), r"", phrase
            )) if len(matched_words) > 0 else len(phrase)
