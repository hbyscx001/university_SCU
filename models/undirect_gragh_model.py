#!/usr/env/bin python3
# coding:utf-8

from . import basic_model

import pandas as pd
import numpy as np
from collections import Counter
from itertools import product


def df2counter(df):
    return Counter(sample[1:] if len(sample) > 2 else sample[1] for sample in df.itertuples())


# sample与ins_sample是相同columns的数据
def factory(samples):
    sample_counter = df2counter(samples)
    sample_sum = sum(sample_counter.values())

    # type: pd.Series对象
    def density_function(ins_sample):
        return sample_counter[tuple(ins_sample.iloc[0])] / sample_sum
    return density_function


class Undirect_gragh_model(basic_model.Basic_model):
    def __init__(self):
        pass

    # DataFrame columns has the index of the X
    def build(self, samples, factor_index):
        self.index_counter = {}
        self.factors = {idx: None for idx in factor_index}
        for factor_idx in self.factors:
            factor_samples = samples[list(factor_idx)]
            self.factors[factor_idx] = factory(factor_samples)

            for single_idx in factor_idx:
                if single_idx not in self.index_counter.keys():
                    self.index_counter[single_idx] = df2counter(samples[[single_idx]])

        print("Building factor function Done!")

    def check(self, lost_sample):
        lost_indexs = set(self.index_counter) - set(lost_sample.columns)
        _ps = [list(self.index_counter[idx]) for idx in lost_indexs]
        product_sample = list(product(*_ps))
        lost_product = pd.DataFrame(product_sample, columns=lost_indexs)

        sample_factor = {}
        for idx in lost_product.index:
            res_sample = pd.DataFrame(np.concatenate([np.array(lost_product.loc[[idx]]), np.array(lost_sample)], axis=1),
                                      columns=list(lost_product.loc[[idx]]) + list(lost_sample))
            sample_factor[tuple(zip(res_sample.columns, res_sample.iloc[0]))] = self.sample_check(res_sample)

        return sample_factor

    # 对于一个给定的样本计算总因子值, pd.Series对象
    def sample_check(self, sample):
        factor_res = {}
        for factor_idx, factor_func in self.factors.items():
            factor_res[factor_idx] = factor_func(sample[list(factor_idx)])
        return factor_res
