#!/usr/env/bin python3
#!-*- coding=utf-8 -*-

import matplotlib.pyplot as plt
import numpy as np
from sklearn.neighbors import KernelDensity
from . import basic_model
import pymc3 as pm
from scipy import optimize
from scipy.stats import expon

# def two_scales(ax1, x, data1, data2, c1, c2):
    # ax2 = ax1.twinx()

    # ax1.plot(x, data1, color=c1)
    # ax1.set_xlabel('Time interval')
    # ax1.set_ylabel('density')

    # ax2.plot(x, data2, color=c2)
    # ax2.set_ylabel('count')
    # return ax1, ax2


class Time_interval_model(basic_model.Basic_model):
    def __init__(self, timestamp, delta_timestamp):
        self.ts = timestamp
        self.delta_t = delta_timestamp

    def kernel_estimate(self, bandwidth=0.01):
        self.kde = KernelDensity(bandwidth=bandwidth).fit(self.delta_t)
        return self.kde

    def kernel_view(self, sample=None, step=1000):
        fig, ax = plt.subplots(1, 1)
        ax0 = ax.twinx()
        plot_field = np.linspace(self.delta_t.min(), self.delta_t.max(), step)
        log_dens = self.kde.score_samples(plot_field[:, np.newaxis])

        ax0.hist(self.delta_t[:, 0], alpha=0.5, color='b')
        ax0.set_ylabel('count')
        ax.plot(plot_field, np.exp(log_dens), color='r', alpha=0.5)
        ax.set_ylabel('density')
        ax.set_xlabel('Time interval')
        if sample:
            ax.vlines(sample)

        plt.show(fig)

    def exp_view(self, lambda_, sample=None, step=1000):
        plot_field = np.linspace(self.delta_t.min(), self.delta_t.max(), step)
        if isinstance(lambda_, list):
            fig, ax = plt.subplots(len(lambda_),1)
            for idx, tmp_lambda in enumerate(lambda_):
                ax[idx].plot(plot_field, expon.pdf(plot_field, scale=1.0 / tmp_lambda), color='r', alpha=0.5)
                ax0 = ax[idx].twinx()
                ax0.hist(self.delta_t[:, 0], color='b', alpha=0.5)
                ax0.set_ylabel('count')
                ax.set_ylabel('density')
                ax.set_xlabel('Time interval')
        else:
            fig, ax = plt.subplots()
            ax.plot(plot_field, expon.pdf(plot_field, scale=1.0 / lambda_), color='r', alpha=0.5)
            ax0 = ax.twinx()
            ax0.hist(self.delta_t[:, 0], color='b', alpha=0.5)
            ax0.set_ylabel('count')
            ax.set_ylabel('density')
            ax.set_xlabel('Time interval')
        plt.show(fig)

    def build(self):
        self.kernel_estimate()
        self.exp_estimate()

    def check(self, sample):
        return np.exp(self.kde.score(sample))

    def exp_estimate(self):
        delta_t = self.delta_t[:,0]
        basic_model = pm.Model()
        mid_dev = (delta_t.max() - delta_t.min()) / 2

        with basic_model:
            lambda_t = pm.Normal('lambda', mu=1/delta_t.mean() , sd=mid_dev)
            dt_obs = pm.Exponential('time_interval', lambda_t, observed=delta_t)

        with basic_model:
            # obtain starting values via MAP
            start = pm.find_MAP(fmin=optimize.fmin_powell)
            # instantiate sampler
            step = pm.Slice()
            # draw 5000 posterior samples
            trace = pm.sample(5000, step=step, start=start)
        pm.summary(trace)
        self.ede = basic_model
        return self.ede
