#!/usr/bin/env python3
# coding:utf-8

from collections import Counter
import math
import numpy as np


def conditional_entropy(X, y):
    counter_X = Counter(tuple(i) for i in X)
    entropy_list = []

    for ins_x, count_x in counter_X.items():
        prop_x = count_x / sum(counter_X.values())
        ins_y = y[np.all(X == ins_x, axis=1)]
        counter_Y = Counter(ins_y)
        prop_y = [item / len(ins_y) for item in counter_Y.values()]
        entropy_list.append(prop_x * -1.0 * sum(prop * math.log(prop)
                                              for prop in prop_y))

    return sum(entropy_list)

def self_entropy(samples, level=1):
    res = []
    for i in range(1,level+1):
        y_samples = samples[i:]
        X_samples = []

        for y_idx in range(i, len(samples)):
            X_samples.append(tuple(samples[y_idx - i:y_idx]))

        X_samples = np.array(X_samples)
        res.append(conditional_entropy(X_samples, y_samples))
        # print("the entropy of sample in level {}:{}".format(i, conditional_entropy(X_samples, y_samples)))
    return res
