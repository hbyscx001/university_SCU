#!/usr/env/bin python3
#! -*- coding:utf-8 -*-

from . import basic_model
from sklearn.naive_bayes import MultinomialNB
import numpy as np
import hashlib
from collections import Counter
from functools import reduce
import networkx as nx
import matplotlib.pyplot as plt

def hash_fun(data):
    return int(hashlib.new('md5', data).hexdigest(), base=16)


class Sknb_model(basic_model.Basic_model):
    def build(self, X, Y):
        self.clfs = [MultinomialNB().fit(X, y) for y in np.nditer(Y, flags=['external_loop'], order='F')]

    def predict(self, X):
        predicts_list = [clf.predict_proba(X) for clf in self.clfs]
        return predicts_list

    def score(self, X, Y):
        Y_columns = np.nditer(Y, flags=['external_loop'], order='F')
        scores = [clf.score(X, y) for clf, y in zip(self.clfs, Y_columns)]
        return scores


class Naive_model(basic_model.Basic_model):
    def build(self, X, Y, ts=None):
        if ts:
            return (self.build_nb_models(X, Y), self.build_time_models(ts))
        else:
            return self.build_nb_models(X, Y)

    #修改输入为np.array数组
    def build_nb_models(self, X, Y):
        self.models = []
        for idx in range(Y.shape[1]):
            self.models.append(frequecy_model(X, Y[:,idx]))
        list(map(lambda mod:mod.frequecy_count(), self.models))
        return self.models

    def build_time_models(self, timestamps):
        order_ts = sorted(timestamps)
        delta_t = list[map(lambda pairs: pairs[1]-pairs[0], zip(order_ts[:-1], order_ts[1:]))]


    def X_check(self, X):
        res_dict = {}
        field_len = len(X)
        for idx in range(field_len):
            res_dict['Y_field{}'.format(idx+1)] = self.models[idx].check_X(X)
        return res_dict

    def X_predict(self, X):
        return [mod.predict_X(X) for mod in self.models]

    def test(self, X, Y):
        counts = X.shape[0]
        true_ = sum([all(self.X_predict(x_sample) == y_sample)
                     for x_sample, y_sample in zip(X, Y)])
        for x_sample, y_sample in zip(X, Y):
            if all(self.X_predict(x_sample) == y_sample) == False:
                print('Wrong example:\nx:{}\npredict_y:{}\ny:{}'.format(x_sample, self.X_predict(x_sample), y_sample))
        return true_ / counts * 1.0


class Frequecy_Error(Exception):
    def __init__(self, feature, pos):
        return "feature {} didn't appeared in position: {} before".format(feature, pos)

class frequecy_model(object):
    def __init__(self, X, y):
        self._X = X
        self._y = y
        self.x_columns = [X[:,idx] for idx in range(X.shape[1])]

    def frequecy_time(self):
        pass

    def frequecy_count(self):
        self.X_y_counters = []
        self.X_counters = []
        self.y_counter = Counter(self._y)
        for x_col in self.x_columns:
            self.X_y_counters.append(Counter(tuple(zip(x_col, self._y))))
            self.X_counters.append(Counter(x_col))

    def get_args(self):
        return (self.X_y_counters, self.y_counter)

    def check_X_y(self, X, y, lamda=1):
        res = []
        for pos in range(len(X)):
            if X[pos] not in self.X_counters[pos]:
                raise Frequecy_Error(X[pos], pos+1)
            if y not in self.y_counter:
                raise Frequecy_Error('y',pos+1)
            xy_count = self.X_y_counters[pos][(X[pos], y)] + lamda
            y_count = self.y_counter[y] + lamda * len(self.X_counters[pos])
            res.append(xy_count / y_count)

        return reduce(lambda i,j: i*j, res) * (self.y_counter[y] / sum(self.y_counter.values()))

    def check_X(self, X, sum_to_1=True):
        res = {}
        for y in set(self._y):
            res[y] = self.check_X_y(X, y)
        return res

    def predict_X(self, X):
        res = self.check_X(X)
        return max(res, key=lambda k:res[k])


    def view(self):
        y_set = set(self._y)
        rows = len(self.X_counters)
        columns = len(y_set)

        #plot every row
        for field_idx, x_counter in enumerate(self.X_counters):
            for y_idx, dst_node in enumerate(y_set):
                plt.subplot(rows, columns, field_idx*columns+y_idx+1)
                g = nx.DiGraph()
                plt.title('Field {} to y value {}'.format(field_idx+1, dst_node))

                edges_set = [("x_{}".format(src_node), "y_{}".format(dst_node), { 'prop':"{:.4f}".format(self.X_y_counters[field_idx][(src_node, dst_node)] / x_counter[src_node]) }) for src_node in x_counter]
                g.add_edges_from(edges_set)
                pos = nx.spectral_layout(g)
                for node in g.nodes():
                    nx.draw_networkx_nodes(g,pos, node_color='#A0CBE2', cmap=plt.cm.Blues)

                # for edge in g.edges():
                    # prop = g.edges[edge]['prop']
                nx.draw_networkx_edges(g,pos, edge_cmap=plt.cm.Reds)

                nx.draw_networkx_edge_labels(g, pos)
                nx.draw_networkx_labels(g, pos)
                plt.axis('off')

        plt.show()
        print("Done")
