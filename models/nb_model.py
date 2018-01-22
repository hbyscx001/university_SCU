#!/usr/env/bin python3
#! -*- coding:utf-8 -*-

from . import basic_model
from sklearn.naive_bayes import MultinomialNB
import numpy as np
import hashlib
from collections import Counter

def hash_fun(data):
    return int(hashlib.new('md5', data).hexdigest(), base=16)

class Naive_model(basic_model.Basic_model):
    def build(self, X, Y):
        models = []
        for idx in range(len(Y[0])):
            y = [ item[idx] for item in Y ]
            models.append(frequecy_model(X, y))
        list(map(lambda mod:mod.frequecy_count(), models))
        return models

    def naive_check(self, X):
        pass

class Frequecy_Error(Exception):
    def __init__(self, feature, pos):
        return "feature {} didn't appeared in position: {} before".format(msg, pos)

class frequecy_model(object):
    def __init__(self, X, y):
        self._X = X
        self._y = y

    def frequecy_count(self):
        self.X_y_counters = []
        self.X_counters = []
        for x in [[row[idx] for row in self._X] for idx in range(len(self._X[0]))]:
            self.X_y_counters.append(Counter(tuple(zip(x, self._y))))
            self.X_counters.append(Counter(x))

    def get_args(self):
        return (self.X_y_counters, self.y_counter)

    def check_X_y(self, X, y):
        res = []
        for pos in range(len(X)):
            xy_count = self.X_y_counters[pos][(X[pos], y)]
            x_count = self.X_counters[pos][X[pos]]
            if x_count == 0:
                raise Frequecy_Error(X[pos], pos)
            res.append(xy_count / x_count)
        return res

    def check_X(self, X):
        res = {}
        for y in set(self._y):
            res[y] = self.check_X_y(X, y)
        return res
