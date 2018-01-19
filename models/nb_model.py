#!/usr/env/bin python3
#! -*- coding:utf-8 -*-

from . import basic_model
from sklearn.naive_bayes import MultinomialNB
import numpy as np

class Naive_model(basic_model.Basic_model):
    def _build(self, X, y):
        tmp_model = MultinomialNB()
        tmp_model.fit(X, y)
        return tmp_model

    def build(self, X, Y):
        models = []
        for idx in range(len(Y[0])):
            y = [ item[idx] for item in Y ]
            models.append(self._build(X, y))
        return models
