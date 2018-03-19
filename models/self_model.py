#!/usr/env/bin python3
#! -*- coding:utf-8 -*-

from . import basic_model
from .. import preprocess

import numpy as np
from collections import Counter, defaultdict


class Self_model(basic_model.Basic_model):
    def __init__(self):
        pass

    def check_entropy(self, samples, level=10):
        columns_data = samples.T
        columns_entropy = []
        for col in columns_data:
            entropys = preprocess.self_entropy(col, level)
            columns_entropy.append(entropys)

        print("the entropy of the sample in every field")
        for lvl in range(level):
            entropy_str = "\t".join(["{:.2f}".format(col[lvl]) for col in columns_entropy])
            print("LEVEL {} ->{}".format(lvl+1, entropy_str))

    def _build_field(self, sample, level):
        counters_dict = defaultdict(Counter)

        y_sample = sample[level:]
        X_sample = []

        for y_idx in range(level, len(sample)):
            X_sample.append(tuple(sample[y_idx - level:y_idx]))

        X_sample = np.array(X_sample)

        for x_key in set([tuple(item) for item in X_sample]):
            values = list(y_sample[np.all(X_sample == x_key, axis=1)])
            counters_dict[x_key].update(values)

        for ins_counter in counters_dict.values():
            tmp_sum = float(sum(ins_counter.values()))
            for key in ins_counter:
                ins_counter[key] /= tmp_sum

        return counters_dict

    def build(self, samples, level_list):
        self.field_models = []
        self.level_list = level_list
        for col, level in zip(samples.T, level_list):
            res = self._build_field(col, level)
            self.field_models.append(res)
        print("Done")

    def trust_sample(self, samples):
        return_sample = []

        for col,level,mod in zip(samples.T, self.level_list, self.field_models):
            return_sample.append(self.caculate_field(col, level, mod))

        return return_sample

    def caculate_field(self, field_array, level, mod):
        return [(field_array[idx] == self.map(tuple(field_array[idx-level:idx]), mod),
                 mod[tuple(field_array[idx-level:idx])][field_array[idx]])
                for idx in range(level, len(field_array))]

    def map(self, sample, mod):
        import operator

        sample = tuple(sample)
        field = mod[sample]
        return max(field.items(), key=operator.itemgetter(1))[0]

    def check(self, samples):
        field_result = []
        for data, ins_counter, level in zip(samples, self.field_models, self.level_list):
            X = tuple(data[:-1])
            y = data[-1]
            if X in ins_counter:
                field_result.append(ins_counter[X][y])
            else:
                field_result.append(None)

        return field_result

    def auto_check(self):
        pass
