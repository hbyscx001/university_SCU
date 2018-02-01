#!usr/env/bin python3
#! -*- coding:utf-8 -*-

from . import basic_model
import pymc3 as pm
import theano.tensor as tt
import theano
import sklearn
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import LabelEncoder, LabelBinarizer
from sklearn.cross_validation import train_test_split
import pandas as pd

class Bayes_neural_network(basic_model.Basic_model):
    def build(self, X, Y, n_hidden=[5, 5], timestamps=None):
        self.X_encoders = {}
        self.Y_encoder  = None

        tran_X = {}
        for i in range(X.shape[1]):
            encoder = LabelEncoder().fit(X[:,i])
            tran_X['X%s' % i] = encoder.transform(X[:, i])
            self.X_encoders['X%s' % i] = encoder
        df_X = pd.DataFrame(tran_X, index=timestamps)

        encoder = LabelEncoder().fit(Y)
        bin_encoder = LabelBinarizer().fit(encoder.transform(Y))
        df_Y = pd.DataFrame(bin_encoder.transform(encoder.transform(Y)), index=timestamps)

        X_train, X_test, Y_train, Y_test = train_test_split(np.array(df_X), np.array(df_Y), test_size=.5)

        ann_input = theano.shared(X_train)
        ann_output = theano.shared(Y_train)

        n_hidden = 5

		# Initialize random weights between each layer
        init_1 = np.random.randn(df_X.shape[1], n_hidden)
        init_2 = np.random.randn(n_hidden, n_hidden)
        init_out = np.random.randn(n_hidden, df_Y.shape[1])

        with pm.Model() as neural_network:
            weights_in_1 = pm.Normal('w_in_1', 0, sd=1,
									shape=(df_X.shape[1], n_hidden),
									testval=init_1)
            weights_1_2 = pm.Normal('w_1_2', 0, sd=1,
									shape=(n_hidden, n_hidden),
									testval=init_2)
            weights_2_out = pm.Normal('w_2_out', 0, sd=1,
									shape=(n_hidden,  df_Y.shape[1]),
									testval=init_out)

            act_1 = tt.tanh(tt.dot(ann_input, weights_in_1))
            act_2 = tt.tanh(tt.dot(act_1, weights_1_2))
            act_out = tt.nnet.sigmoid(tt.dot(act_2, weights_2_out))
            out = pm.Bernoulli('out',
							act_out,
							observed=ann_output)

        # init_weights = []
        # pre_inputs = tran_X.shape[1]
        # for nodes in n_hidden:
            # init_weights.append(np.random.randn(pre_inputs, nodes))
            # pre_inputs = nodes
        # init_weights.append(np.random.randn(pre_inputs, tran_Y.shape[1]))

        # with pm.Model() as neural_network:
            # hidden_weights = []
            # pre_inputs = tran_X.shape[1]
            # for idx, nodes in enumerate(n_hidden):
                # hidden_weights.append(pm.Normal('layer_{}'.format(idx+1), 0, sd=1,
                                         # shape=(pre_inputs, nodes),
                                         # testval=init_weights[idx]))
                # pre_inputs = nodes

            # out_weight.append(pm.Normal('layer_out', 0, sd=1,
                                        # shape=(pre_inputs, tran_y.shape[1]),
                                        # testval=init_weights[-1]))

            # pre_act = ann_input
            # for idx in range(len(n_hidden)):
                # pre_act = tt.tanh(tt.dot(pre_act, ))
        with neural_network:
            self.v_params = pm.variational.advi(n=50000)

        with neural_network:
            self.trace = pm.variational.sample_vp(self.v_params, draws=5000)
        # with neural_network:
            # self.trace = pm.sample(50000)

        ann_input.set_value(X_test)
        ann_output.set_value(Y_test)
        ppc = pm.sample_ppc(self.trace, model=neural_network, samples=500)
        pred = ppc['out'].mean(axis=0) > 0.5
        print('Accuracy = {}%'.format((Y_test == pred).mean() * 100))

        # self.model = neural_network
        # return self.model
