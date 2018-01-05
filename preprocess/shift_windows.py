#!/usr/bin/env python3
# coding:utf-8

import collections
import numpy as np
import pandas as pd
import dpkt
import seaborn as sns
import matplotlib.pyplot as plt

from . import basic_process

class shift_preprocess(basic_process.Basic_processer):
    def __init__(self, queue_sizes):
        self.qs = queue_sizes

    def extract(self, pcap):
        res = []
        queue = collections.deque(maxlen=self.qs)
        for pair in pcap:
            queue.append(pair)
            if len(queue) == self.qs:
                window_features = self._window_count(queue)
                res.append(window_features)
            else:
                continue

        return pd.DataFrame(data=res, columns=['benchmark', 'averge_interval',
                                               'ip_count'])

    def _window_count(self, queue):
        time_serials = (pair[0] for pair in queue)
        avg_interval = np.mean(list(shift_preprocess.avg_interval(time_serials)))

        ip_observe = set()
        for ts, buf in queue:
            ip = dpkt.ethernet.Ethernet(buf).data
            ip_observe.add(ip.dst)
            ip_observe.add(ip.src)
        ip_count = len(ip_observe)

        return (queue[-1][0],avg_interval, ip_count)

    @staticmethod
    def avg_interval(iters):
        prev = next(iters)
        for now in iters:
            yield now - prev
            prev = now

    def view(self, df):
        # sns.pairplot(df.loc[:,['avg_interval', 'ip_count']])
        plt.scatter(df['averge_interval'],df['ip_count'])
        plt.show()

if __name__ == '__main__':
    fh = open('../test/test_data.pcap', 'rb')
    pcaps = dpkt.pcap.Reader(fh)
    pos = shift_preprocess(10)
    res = pos.extract(pcaps)
    pos.view(res)


